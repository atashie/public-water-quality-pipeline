"""CyAN CI_cyano product: encoding, index conversion, filename parsing, file search, cloud access.

Ported from the owner's HAB_PoC repository on 2026-09-22 and rewritten against the checked
claims in ../METADATA.md. Every constant names its claim id. Nothing here contacts a provider
on import. The functions that do take a caller-provided ``requests.Session`` and are named
``search_files``, ``get_s3_credentials``, and ``tea_head``.
"""

from __future__ import annotations

import datetime as _dt
import re
from collections.abc import Iterable
from dataclasses import asdict, dataclass

import numpy as np

# --------------------------------------------------------------------------- #
# Encoding, claims cl-cyan-encoding-dn-table and cl-cyan-encoding-dn-formula
# --------------------------------------------------------------------------- #
DN_BELOW_DETECTION = 0  # water observed, index below the detection limit. A measurement.
DN_VALID_MIN = 1
DN_VALID_MAX = 253
DN_LAND = 254
DN_NODATA = 255  # cloud, ice cover, no valid retrieval

CI_SLOPE = 0.011714
CI_INTERCEPT = -4.1870866

# NOAA's look-alike product uses land 252 and invalid 251, 253, 254, 255. Never apply its
# constants here. Claims cl-cyan-encoding-noaa-flagging and cl-cyan-encoding-noaa-valid-range.
NOAA_DN_LAND = 252


def dn_to_ci(dn: np.ndarray) -> np.ndarray:
    """Digital number to index for 1 to 253. Codes 0, 254, and 255 become NaN.

    Zero has no index magnitude, so it is NaN here. Callers that need to keep the
    below-detection class apart from no-data use ``classify_dn``.
    """
    dn = np.asarray(dn)
    valid = (dn >= DN_VALID_MIN) & (dn <= DN_VALID_MAX)
    out = np.full(dn.shape, np.nan, dtype="float64")
    out[valid] = 10.0 ** (dn[valid].astype("float64") * CI_SLOPE + CI_INTERCEPT)
    return out


def classify_dn(dn: np.ndarray) -> dict[str, np.ndarray]:
    """Boolean masks for the four mutually exclusive code classes."""
    dn = np.asarray(dn)
    return {
        "below_detection": dn == DN_BELOW_DETECTION,
        "valid": (dn >= DN_VALID_MIN) & (dn <= DN_VALID_MAX),
        "land": dn == DN_LAND,
        "nodata": dn == DN_NODATA,
    }


# --------------------------------------------------------------------------- #
# Endpoints, claims in METADATA section 7
# --------------------------------------------------------------------------- #
SEARCH_URL = "https://oceandata.sci.gsfc.nasa.gov/api/cyan_file_search"
GETFILE_BASE = "https://oceandata.sci.gsfc.nasa.gov/getfile/"
TEA_BASE = "https://obdaac-tea.earthdatacloud.nasa.gov/ob-cumulus-prod-public/"
S3_BUCKET = "ob-cumulus-prod-public"
S3_CREDENTIALS_URL = "https://obdaac-tea.earthdatacloud.nasa.gov/s3credentials"
S3_REGION = "us-west-2"
CMR_GRANULES_URL = "https://cmr.earthdata.nasa.gov/search/granules.json"
CMR_COLLECTION_OLCI = "C3416412382-OB_CLOUD"

# Search vocabulary, claims cl-cyan-access-param-region-period-product,
# cl-cyan-access-param-areaids, and cl-cyan-access-param-dates-and-flags.
REGION = {"conus": 1, "alaska": 0, "ak": 0}
PERIOD = {"daily": 2, "weekly": 1}
PRODUCT = {"ci": 1, "ci_cyano": 1, "truecolor": 2, "tc": 2}

EMPTY_RESULT_MARKERS = ("your query generated 0 file", "no results")


def getfile_url(filename: str) -> str:
    return GETFILE_BASE + filename


def tea_url(filename: str) -> str:
    return TEA_BASE + filename


# --------------------------------------------------------------------------- #
# Filename parsing, claims cl-cyan-naming-*
# --------------------------------------------------------------------------- #
_SENSOR = {"L": "OLCI/Sentinel-3", "M": "MERIS/Envisat"}
_DATE_RE = re.compile(r"^([LM])(\d{7})(\d{7})?$")
_PER_SATELLITE_RE = re.compile(r"^S3[AB]_OLCI", re.IGNORECASE)


def doy_to_date(token: str) -> _dt.date:
    """YYYYDDD to a date. Leap years are handled by the calendar, never by hand.

    Raises ValueError when the day of year falls outside the named year.
    """
    year, doy = int(token[:4]), int(token[4:7])
    date = _dt.date(year, 1, 1) + _dt.timedelta(days=doy - 1)
    if doy < 1 or date.year != year:
        raise ValueError(f"day {doy} is not in year {year}")
    return date


@dataclass
class CyanFile:
    filename: str
    url: str
    sensor: str
    sensor_code: str
    start_date: str
    end_date: str
    temporal: str
    stream: str
    product: str
    region: str
    resolution: str
    tile: str
    is_mosaic: bool = False

    def as_dict(self) -> dict:
        return asdict(self)


def parse_cyan_filename(name_or_url: str) -> CyanFile | None:
    """Parse a merged CI_cyano file name or getfile URL. Returns None for anything else.

    Tile: ``L3m_7D_CYAN_CI_cyano_CYAN_CONUS_300m_<col>_<row>.tif``.
    Whole region: the same without the column and row. Daily files carry one date stamp.
    """
    url = name_or_url
    filename = name_or_url.rsplit("/", 1)[-1]
    stem = filename[:-4] if filename.lower().endswith(".tif") else filename
    if "." not in stem:
        return None
    datepart, _, rest = stem.partition(".")
    m = _DATE_RE.match(datepart)
    if not m:
        return None
    sensor_code, start_tok = m.group(1), m.group(2)
    end_tok = m.group(3) or start_tok
    try:
        start_date = doy_to_date(start_tok).isoformat()
        end_date = doy_to_date(end_tok).isoformat()
    except ValueError:
        return None
    tokens = rest.split("_")
    if len(tokens) < 8 or "CI" not in tokens or "cyano" not in tokens:
        return None
    level, temporal, stream = tokens[0], tokens[1], tokens[2]
    if level != "L3m" or temporal not in ("DAY", "7D"):
        return None
    region = "AK" if "AK" in tokens else ("CONUS" if "CONUS" in tokens else "?")
    res_idx = next((i for i, t in enumerate(tokens) if t.endswith("m") and t[:-1].isdigit()), None)
    if res_idx is None:
        return None
    trailing = tokens[res_idx + 1 :]
    if len(trailing) >= 2 and trailing[-2].isdigit() and trailing[-1].isdigit():
        tile, is_mosaic = f"{trailing[-2]}_{trailing[-1]}", False
    elif len(trailing) == 0:
        tile, is_mosaic = f"{region}_mosaic", True
    else:
        return None
    return CyanFile(
        filename=filename,
        url=url,
        sensor=_SENSOR.get(sensor_code, sensor_code),
        sensor_code=sensor_code,
        start_date=start_date,
        end_date=end_date,
        temporal=temporal,
        stream=stream,
        product="CI_cyano",
        region=region,
        resolution=tokens[res_idx],
        tile=tile,
        is_mosaic=is_mosaic,
    )


def categorize_search_results(urls: Iterable[str]) -> dict[str, list]:
    """Split search URLs into merged files, per-satellite files, and everything else.

    The search mixes the merged product with single-sensor files. Only merged files are
    used. The split is explicit so that nothing is dropped silently.
    """
    merged: list[CyanFile] = []
    per_satellite: list[str] = []
    other: list[str] = []
    for u in urls:
        fn = u.rsplit("/", 1)[-1]
        parsed = parse_cyan_filename(u)
        if parsed is not None:
            merged.append(parsed)
        elif _PER_SATELLITE_RE.match(fn):
            per_satellite.append(u)
        else:
            other.append(u)
    return {"merged": merged, "per_satellite": per_satellite, "other": other}


def prefer_stream(files: Iterable[CyanFile], preferred: str = "CYAN") -> list[CyanFile]:
    """One file per (temporal, region, tile, start, end), keeping ``preferred`` when present.

    Two name streams can coexist for one date. The choice and its reason are in
    METADATA section 10. The output is sorted by start date then tile.
    """
    by_key: dict[tuple, CyanFile] = {}
    for f in files:
        key = (f.temporal, f.region, f.tile, f.start_date, f.end_date)
        cur = by_key.get(key)
        if cur is None or (f.stream == preferred and cur.stream != preferred):
            by_key[key] = f
    return sorted(by_key.values(), key=lambda x: (x.start_date, x.tile))


# --------------------------------------------------------------------------- #
# File search, METADATA section 7.1
# --------------------------------------------------------------------------- #
def search_form(
    region: str, period: str, product: str, areaids: str, sdate: str, edate: str
) -> dict:
    return {
        "region": REGION[region.lower()],
        "period": PERIOD[period.lower()],
        "product": PRODUCT[product.lower()],
        "areaids": areaids,
        "sdate": sdate,
        "edate": edate,
        "addurl": 1,
        "results_as_file": 1,
        "wgetflag": 1,
    }


def parse_search_body(status_code: int, body: str) -> list[str] | None:
    """URLs from a search response, ``[]`` for an explicit empty result, None to retry.

    An empty result is accepted only when the body says so: the HTML page stating that the
    query generated 0 files, observed on 2026-09-22, or a plain "No Results". Any other HTML,
    an empty body, or an unexpected body is treated as a failed request. A provider outage
    then fails loudly instead of passing as an empty archive.
    """
    if status_code != 200:
        return None
    if "getfile" in body:
        return [ln.strip() for ln in body.splitlines() if ln.strip().startswith("http")]
    low = body.lower()
    if any(m in low for m in EMPTY_RESULT_MARKERS):
        return []
    return None


def search_files(
    session,
    region: str,
    period: str,
    product: str,
    areaids: str,
    sdate: str,
    edate: str,
    tries: int = 6,
    timeout: int = 90,
) -> list[str]:
    """Query the file search and return getfile URLs. Retries on transient failures."""
    form = search_form(region, period, product, areaids, sdate, edate)
    last = None
    for _ in range(tries):
        resp = session.post(SEARCH_URL, data=form, timeout=timeout)
        last = resp
        parsed = parse_search_body(resp.status_code, resp.text or "")
        if parsed is not None:
            return parsed
    raise RuntimeError(
        f"cyan_file_search failed after {tries} attempts, "
        f"last status {getattr(last, 'status_code', '?')}. Params {form}."
    )


# --------------------------------------------------------------------------- #
# Version tag from the file, METADATA section 10
# --------------------------------------------------------------------------- #
def read_processing_version(path) -> str | None:
    """The processing version from a GeoTIFF's metadata tags, or None. Reads no pixel."""
    import rasterio

    with rasterio.open(path) as ds:
        tags = ds.tags()
    for k, v in tags.items():
        if "version" in k.lower():
            return str(v)
    for v in tags.values():
        if isinstance(v, str) and "CYAN" in v.upper() and "V" in v.upper():
            return str(v)
    return None


# --------------------------------------------------------------------------- #
# Earthdata Cloud, METADATA section 7.3
# --------------------------------------------------------------------------- #
def bearer_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def get_s3_credentials(session, token: str, timeout: int = 60) -> tuple[int, dict | None]:
    """Temporary credentials from the OB.DAAC endpoint. Returns (status, json or None).

    The caller never logs the returned dict. Credentials last 1 hour and work only
    from us-west-2, claims cl-cyan-access-s3-credentials-1hour and
    cl-cyan-access-s3-same-region-readonly.
    """
    r = session.get(S3_CREDENTIALS_URL, headers=bearer_headers(token), timeout=timeout)
    if r.status_code != 200:
        return r.status_code, None
    try:
        return r.status_code, r.json()
    except ValueError:
        return r.status_code, None


def tea_head(session, filename: str, token: str, timeout: int = 60) -> dict:
    """HEAD one object through the HTTPS distribution endpoint, following redirects.

    Returns status, content length when the final response carries it, the final host,
    and the redirect chain length. No body is read.
    """
    r = session.head(
        tea_url(filename), headers=bearer_headers(token), timeout=timeout, allow_redirects=True
    )
    length = r.headers.get("Content-Length")
    from urllib.parse import urlparse

    return {
        "filename": filename,
        "status": r.status_code,
        "bytes": int(length) if length and length.isdigit() else None,
        "final_host": urlparse(r.url).hostname,
        "redirects": len(r.history),
    }
