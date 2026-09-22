"""HTTP helpers shared across datasets: retrying sessions, credentials, cached downloads.

Ported from the owner's HAB_PoC repository (data-sources/_common/net.py) on 2026-09-22 and
generalized. Design goals, per the rules in .claude/rules/datasets.md:

- Every download is cached. A file that exists with enough bytes is not fetched again unless
  its sha256 disagrees with the expected value from a prior manifest.
- Every download is logged to a JSONL manifest with sha256, byte size, source URL, and
  access time, so any figure or metric traces to the exact bytes it used.
- Credentials are read from the environment or the ignored ``.env`` at the repository root.
  They are never printed.
"""

from __future__ import annotations

import hashlib
import json
import os
import time
from dataclasses import dataclass
from pathlib import Path

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DOTENV = REPO_ROOT / ".env"
DEFAULT_USER_AGENT = (
    "public-water-quality-pipeline/0.1 (research ingest; contact: repository owner)"
)


# --------------------------------------------------------------------------- #
# Credentials
# --------------------------------------------------------------------------- #
def load_dotenv(dotenv_path: Path) -> None:
    """Push KEY=VALUE lines from ``dotenv_path`` into os.environ when not already set.

    Existing environment variables win, so a shell or CI override takes precedence.
    Blank lines and lines starting with ``#`` are ignored. Surrounding quotes are stripped.
    """
    if not dotenv_path.is_file():
        return
    for raw in dotenv_path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        key, val = key.strip(), val.strip().strip('"').strip("'")
        os.environ.setdefault(key, val)


def resolve_env(name: str, dotenv_path: Path | None = DEFAULT_DOTENV) -> str | None:
    """Return the value of ``name`` from the environment or the ``.env`` file, or None.

    Precedence: an existing environment variable, then the ``.env`` file. An empty value
    counts as unset.
    """
    if dotenv_path is not None:
        load_dotenv(dotenv_path)
    value = os.environ.get(name, "").strip()
    return value or None


def resolve_edl_token(dotenv_path: Path | None = DEFAULT_DOTENV) -> str | None:
    """Earthdata Login bearer token for OB.DAAC downloads. Variable ``OB_DAAC_EDL_TOKEN``."""
    return resolve_env("OB_DAAC_EDL_TOKEN", dotenv_path)


def resolve_appkey(dotenv_path: Path | None = DEFAULT_DOTENV) -> str | None:
    """OB.DAAC AppKey, the alternative to the bearer token. Variable ``OB_DAAC_APPKEY``."""
    return resolve_env("OB_DAAC_APPKEY", dotenv_path)


# --------------------------------------------------------------------------- #
# Sessions
# --------------------------------------------------------------------------- #
def make_session(
    total_retries: int = 5,
    backoff_factor: float = 1.5,
    status_forcelist: tuple[int, ...] = (429, 500, 502, 503, 504),
    user_agent: str = DEFAULT_USER_AGENT,
) -> requests.Session:
    """A requests.Session with retry and backoff for flaky provider endpoints.

    Transient 5xx responses are retried. ``Retry-After`` headers are honored. Requests
    honors ``~/.netrc`` for hosts not otherwise authenticated.
    """
    retry = Retry(
        total=total_retries,
        connect=total_retries,
        read=total_retries,
        status=total_retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
        allowed_methods=frozenset(["GET", "POST", "HEAD"]),
        raise_on_status=False,
        respect_retry_after_header=True,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session = requests.Session()
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    session.headers.update({"User-Agent": user_agent})
    return session


# --------------------------------------------------------------------------- #
# Cached, manifested downloads
# --------------------------------------------------------------------------- #
@dataclass
class DownloadResult:
    """What ``download_file`` returns. ``integrity`` is one of:

    - ``verified``: the sha256 matches the expected value from a prior manifest.
    - ``refetched_stale_cache``: the cached bytes were stale or corrupt, the file was fetched
      again, and the fresh bytes match the expected value.
    - ``mismatch``: freshly fetched bytes still differ from the expected value. The provider
      changed the file, for example by reprocessing.
    - ``unverified``: no expected sha256 was supplied.
    """

    url: str
    path: Path
    bytes: int
    sha256: str
    cached: bool
    accessed_utc: str
    integrity: str = "unverified"


def sha256_file(path: Path, chunk: int = 1 << 20) -> str:
    """The sha256 hex digest of a file, read in chunks."""
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda: f.read(chunk), b""):
            h.update(block)
    return h.hexdigest()


def utc_now_iso() -> str:
    """The current UTC time as an ISO 8601 string with a ``Z`` suffix."""
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def download_file(
    session: requests.Session,
    url: str,
    dest: Path,
    appkey: str | None = None,
    bearer_token: str | None = None,
    expected_sha256: str | None = None,
    timeout: int = 300,
    min_bytes: int = 1,
    login_hosts: tuple[str, ...] = ("urs.earthdata.nasa.gov",),
) -> DownloadResult:
    """Download ``url`` to ``dest`` with caching and integrity states. See ``DownloadResult``.

    Cache hit: ``dest`` exists with at least ``min_bytes``. Without ``expected_sha256`` the
    cached file is returned as ``unverified``. With it, a match returns ``verified`` and a
    mismatch discards the cached file and fetches again.

    Authentication precedence: ``bearer_token`` as an ``Authorization: Bearer`` header, then
    ``appkey`` as a query parameter, then whatever ``~/.netrc`` supplies.

    The response streams to a ``.part`` file, is checked for ``min_bytes``, and is renamed
    atomically. A 200 response whose final URL is on a login host with an HTML body means
    authentication failed, and raises ``PermissionError``.
    """
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)

    cache_was_stale = False
    if dest.is_file() and dest.stat().st_size >= min_bytes:
        have = sha256_file(dest)
        if expected_sha256 is None:
            return DownloadResult(
                url, dest, dest.stat().st_size, have, True, utc_now_iso(), "unverified"
            )
        if have == expected_sha256:
            return DownloadResult(
                url, dest, dest.stat().st_size, have, True, utc_now_iso(), "verified"
            )
        cache_was_stale = True
        dest.unlink()

    fetch_url = url
    headers: dict[str, str] = {}
    if bearer_token:
        headers["Authorization"] = f"Bearer {bearer_token}"
    elif appkey:
        sep = "&" if "?" in fetch_url else "?"
        fetch_url = f"{fetch_url}{sep}appkey={appkey}"

    tmp = dest.with_suffix(dest.suffix + ".part")
    with session.get(
        fetch_url, headers=headers, stream=True, timeout=timeout, allow_redirects=True
    ) as r:
        ctype = r.headers.get("Content-Type", "")
        final_host = requests.utils.urlparse(r.url).hostname or ""
        if r.status_code == 200 and "text/html" in ctype and final_host in login_hosts:
            raise PermissionError(
                f"Download for {url} landed on the login page {final_host}. "
                "Authentication is missing or invalid. Check .env, see .env.example."
            )
        r.raise_for_status()
        written = 0
        with tmp.open("wb") as f:
            for chunk in r.iter_content(chunk_size=1 << 20):
                if chunk:
                    f.write(chunk)
                    written += len(chunk)

    if written < min_bytes:
        tmp.unlink(missing_ok=True)
        raise OSError(f"Downloaded {written} bytes for {url}, below min_bytes={min_bytes}.")

    tmp.replace(dest)
    fetched_sha = sha256_file(dest)
    if expected_sha256 is None:
        integrity = "unverified"
    elif fetched_sha == expected_sha256:
        integrity = "refetched_stale_cache" if cache_was_stale else "verified"
    else:
        integrity = "mismatch"
    return DownloadResult(
        url, dest, dest.stat().st_size, fetched_sha, False, utc_now_iso(), integrity
    )


def append_manifest(manifest_path: Path, record: dict) -> None:
    """Append one JSON record per line to a download manifest."""
    manifest_path = Path(manifest_path)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    with manifest_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, sort_keys=True) + "\n")


def read_manifest(manifest_path: Path) -> list[dict]:
    """Read every record of a JSONL manifest. A missing file reads as empty."""
    manifest_path = Path(manifest_path)
    if not manifest_path.is_file():
        return []
    out = []
    for line in manifest_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            out.append(json.loads(line))
    return out
