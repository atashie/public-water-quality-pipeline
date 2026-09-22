"""Offline tests for the pull plan and the route-comparison summary. No network."""

from datasets.cyan.access import compare_routes, cyan_api, pull_cyan

G = "https://oceandata.sci.gsfc.nasa.gov/getfile/"
NAMES = [
    "L20161152016121.L3m_7D_CYAN_CI_cyano_CYAN_CONUS_300m.tif",
    "L20161222016128.L3m_7D_CYANV6T_CI_cyano_CYAN_CONUS_300m.tif",
    "L20161222016128.L3m_7D_CYAN_CI_cyano_CYAN_CONUS_300m.tif",
    "L20161292016135.L3m_7D_CYANV6T_CI_cyano_CYAN_CONUS_300m.tif",
]
PER_SAT = G + "S3A_OLCI_EFRNT.20160424.L3m.7D.CYAN.CI_cyano.CYAN_CONUS.300m.tif"


def test_build_plan_counts_and_collapse():
    plan = pull_cyan.build_plan([G + n for n in NAMES] + [PER_SAT, "https://x/readme.txt"], "CYAN")
    assert plan["urls"] == 6 and plan["merged"] == 4
    assert plan["per_satellite_excluded"] == 1 and plan["other_excluded"] == 1
    assert plan["after_stream_collapse"] == 3
    assert plan["preferred_stream_count"] == 2 and plan["fallback_stream_count"] == 1
    assert plan["first"] == NAMES[0] and plan["last"] == NAMES[3]
    streams = [f.stream for f in plan["files"]]
    assert streams == ["CYAN", "CYAN", "CYANV6T"]


def test_build_plan_limit():
    plan = pull_cyan.build_plan([G + n for n in NAMES], "CYAN", limit=2)
    assert plan["planned"] == 2 and plan["after_stream_collapse"] == 3
    assert [f.filename for f in plan["files"]] == [NAMES[0], NAMES[2]]


def test_default_outdir_and_latency():
    out = pull_cyan.default_outdir("conus", "weekly", "all")
    assert out.name == "weekly_conus_mosaic" and out.parent.name == "raw"
    assert pull_cyan.default_outdir("conus", "daily", "7_2+6_2").name == "daily_conus_7_2-6_2"
    assert pull_cyan.age_at_retrieval_days("2026-09-19", "2026-09-22T10:00:00Z") == 3
    assert pull_cyan.age_at_retrieval_days("2026-09-21", "2026-09-22T00:00:00Z") == 1


def test_plan_drift_reports_added_and_removed():
    same = pull_cyan.plan_drift(NAMES[:2], NAMES[:2])
    assert same == {"added": [], "removed": [], "same": True}
    drift = pull_cyan.plan_drift(NAMES[:2], [NAMES[1], NAMES[2]])
    assert drift["added"] == [NAMES[2]] and drift["removed"] == [NAMES[0]]
    assert drift["same"] is False


def test_summarize_presence():
    files = [cyan_api.parse_cyan_filename(n) for n in (NAMES[0], NAMES[2], NAMES[3])]
    heads = [
        {"filename": NAMES[0], "status": 200, "bytes": 100},
        {"filename": NAMES[2], "status": 404, "bytes": None},
    ]
    s = compare_routes.summarize_presence(files, heads)
    assert s["listed"] == 3 and s["present"] == 1 and s["missing"] == 2
    assert s["status_counts"] == {"200": 1, "404": 1, "None": 1}
    assert s["newest_present_window_end"] == "2016-04-30"
    assert s["newest_listed_window_end"] == "2016-05-14"
    assert s["missing_files"] == [NAMES[2], NAMES[3]]
