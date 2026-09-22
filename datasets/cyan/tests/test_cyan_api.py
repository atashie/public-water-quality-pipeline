"""Offline tests for the CyAN access layer. No network."""

import math

import numpy as np
import pytest
import requests

from datasets.cyan.access import cyan_api as c

WEEKLY_MOSAIC = "L20161152016121.L3m_7D_CYAN_CI_cyano_CYAN_CONUS_300m.tif"
WEEKLY_TILE = "https://oceandata.sci.gsfc.nasa.gov/getfile/L20262492026255.L3m_7D_CYAN_CI_cyano_CYAN_CONUS_300m_1_1.tif"
DAILY_MOSAIC = "L2026213.L3m_DAY_CYAN_CI_cyano_CYAN_CONUS_300m.tif"
MERIS_TILE = "M20120922012098.L3m_7D_CYAN_CI_cyano_CYAN_CONUS_300m_5_3.tif"
V6T_MOSAIC = "L20221602022166.L3m_7D_CYANV6T_CI_cyano_CYAN_CONUS_300m.tif"
CYAN_MOSAIC_SAME_WEEK = "L20221602022166.L3m_7D_CYAN_CI_cyano_CYAN_CONUS_300m.tif"
ALASKA_TILE = "L2026213.L3m_DAY_CYAN_CI_cyano_CYAN_AK_300m_2_1.tif"
PER_SAT = "https://oceandata.sci.gsfc.nasa.gov/getfile/S3A_OLCI_EFRNT.20260801.L3m.DAY.CYAN.CI_cyano.CYAN_CONUS.300m_1_1.tif"


def test_doy_decode_handles_leap_year():
    assert c.doy_to_date("2016115").isoformat() == "2016-04-24"
    assert c.doy_to_date("2016116").isoformat() == "2016-04-25"
    assert c.doy_to_date("2026256").isoformat() == "2026-09-13"
    assert c.doy_to_date("2026262").isoformat() == "2026-09-19"


def test_parse_weekly_mosaic():
    f = c.parse_cyan_filename(WEEKLY_MOSAIC)
    assert f.sensor_code == "L" and f.temporal == "7D" and f.stream == "CYAN"
    assert f.start_date == "2016-04-24" and f.end_date == "2016-04-30"
    assert f.is_mosaic and f.tile == "CONUS_mosaic" and f.region == "CONUS"
    assert f.resolution == "300m"


def test_parse_weekly_tile_from_url():
    f = c.parse_cyan_filename(WEEKLY_TILE)
    assert f.url == WEEKLY_TILE and f.filename.endswith("_1_1.tif")
    assert f.tile == "1_1" and not f.is_mosaic
    assert f.start_date == "2026-09-06" and f.end_date == "2026-09-12"


def test_parse_daily_single_stamp_and_alaska():
    d = c.parse_cyan_filename(DAILY_MOSAIC)
    assert d.temporal == "DAY" and d.start_date == d.end_date == "2026-08-01"
    a = c.parse_cyan_filename(ALASKA_TILE)
    assert a.region == "AK" and a.tile == "2_1"


def test_parse_meris_and_rejects():
    m = c.parse_cyan_filename(MERIS_TILE)
    assert m.sensor_code == "M" and m.start_date == "2012-04-01" and m.end_date == "2012-04-07"
    assert c.parse_cyan_filename(PER_SAT) is None
    assert c.parse_cyan_filename("garbage.tif") is None
    assert c.parse_cyan_filename("L2026213.L3b_DAY_CYAN_CI_cyano_CYAN_CONUS_300m.tif") is None
    assert c.parse_cyan_filename("L2026999.L3m_DAY_CYAN_CI_cyano_CYAN_CONUS_300m.tif") is None


def test_categorize_is_explicit_about_exclusions():
    cats = c.categorize_search_results([WEEKLY_TILE, PER_SAT, "https://x/other.txt"])
    assert [f.filename for f in cats["merged"]] == [WEEKLY_TILE.rsplit("/", 1)[-1]]
    assert cats["per_satellite"] == [PER_SAT]
    assert cats["other"] == ["https://x/other.txt"]


def test_prefer_stream_collapses_duplicates_and_sorts():
    files = [c.parse_cyan_filename(n) for n in (V6T_MOSAIC, CYAN_MOSAIC_SAME_WEEK, WEEKLY_MOSAIC)]
    plan = c.prefer_stream(files, preferred="CYAN")
    assert [f.filename for f in plan] == [WEEKLY_MOSAIC, CYAN_MOSAIC_SAME_WEEK]
    only_v6t = c.prefer_stream([c.parse_cyan_filename(V6T_MOSAIC)], preferred="CYAN")
    assert only_v6t[0].stream == "CYANV6T"


def test_dn_to_ci_and_classes():
    dn = np.array([0, 1, 130, 253, 254, 255], dtype=np.uint8)
    ci = c.dn_to_ci(dn)
    assert math.isnan(ci[0]) and math.isnan(ci[4]) and math.isnan(ci[5])
    assert ci[1] == pytest.approx(10 ** (1 * c.CI_SLOPE + c.CI_INTERCEPT))
    assert ci[3] == pytest.approx(10 ** (253 * c.CI_SLOPE + c.CI_INTERCEPT))
    assert ci[2] > ci[1]
    cls = c.classify_dn(dn)
    assert cls["below_detection"].tolist() == [True, False, False, False, False, False]
    assert cls["valid"].tolist() == [False, True, True, True, False, False]
    assert cls["land"].tolist() == [False, False, False, False, True, False]
    assert cls["nodata"].tolist() == [False, False, False, False, False, True]
    assert c.NOAA_DN_LAND != c.DN_LAND


def test_urls():
    assert c.getfile_url(DAILY_MOSAIC).startswith("https://oceandata.sci.gsfc.nasa.gov/getfile/")
    assert c.tea_url(DAILY_MOSAIC) == c.TEA_BASE + DAILY_MOSAIC
    form = c.search_form("conus", "weekly", "ci", "all", "2016-01-01", "2016-12-31")
    assert form["region"] == 1 and form["period"] == 1 and form["product"] == 1
    assert form["areaids"] == "all" and form["sdate"] == "2016-01-01"
    assert form["edate"] == "2016-12-31" and form["addurl"] == 1
    assert form["results_as_file"] == 1 and form["wgetflag"] == 1


def test_parse_search_body():
    listing = f"{WEEKLY_TILE}\nhttps://oceandata.sci.gsfc.nasa.gov/getfile/{DAILY_MOSAIC}\n"
    assert c.parse_search_body(200, listing) == listing.split()
    assert (
        c.parse_search_body(200, "<html><body>Your query generated 0 file(s).</body></html>") == []
    )
    assert c.parse_search_body(200, "No Results") == []
    assert c.parse_search_body(502, "Bad Gateway") is None
    assert c.parse_search_body(200, "something unexpected") is None


def test_parse_search_body_fails_closed_on_unexpected_html_and_empty_body():
    outage = "<html><body>Service temporarily unavailable</body></html>"
    assert c.parse_search_body(200, outage) is None
    assert c.parse_search_body(200, "") is None
    assert c.parse_search_body(200, "   \n") is None


class FakeSession:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def post(self, url, data=None, timeout=None):
        self.calls.append((url, data))
        status, text = self.responses.pop(0)
        r = requests.Response()
        r.status_code = status
        r._content = text.encode()
        return r


def test_search_files_retries_then_returns():
    s = FakeSession([(502, "Bad Gateway"), (200, WEEKLY_TILE + "\n")])
    assert c.search_files(s, "conus", "weekly", "ci", "1_1", "2026-09-01", "2026-09-22") == [
        WEEKLY_TILE
    ]
    assert len(s.calls) == 2 and s.calls[0][0] == c.SEARCH_URL


def test_search_files_gives_up():
    s = FakeSession([(502, "x")] * 3)
    with pytest.raises(RuntimeError):
        c.search_files(s, "conus", "weekly", "ci", "all", "2026-09-01", "2026-09-22", tries=3)
