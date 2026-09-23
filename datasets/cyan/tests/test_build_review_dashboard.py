"""Offline tests for the review dashboard builder on a synthetic mosaic. No network."""

import base64
import io
import json

import numpy as np
import rasterio
from PIL import Image
from rasterio.transform import from_origin

from datasets.cyan.viz import build_review_dashboard as b

NAME = "L20261882026194.L3m_7D_CYAN_CI_cyano_CYAN_CONUS_300m.tif"
ORIGIN = (-3949197.04669, 3791526.267078)


def write_mosaic(path, arr):
    transform = from_origin(ORIGIN[0], ORIGIN[1], 300.0, 300.0)
    with rasterio.open(
        path,
        "w",
        driver="GTiff",
        height=arr.shape[0],
        width=arr.shape[1],
        count=1,
        dtype="uint8",
        crs="EPSG:5070",
        transform=transform,
        compress="lzw",
    ) as ds:
        ds.write(arr, 1)
        ds.update_tags(OBPG_version="6.0")
    return transform


def qa_stub(name):
    return {
        "raw_dir": "raw",
        "measured_at": "2026-09-22T12:00:00Z",
        "fatal": False,
        "n_files": 1,
        "collection": {
            "collection_flags": [],
            "notes": [],
            "version_tags": {"OBPG_version=6.0": 1},
            "grid_consistent": True,
            "collection_consistent": True,
        },
        "completeness": {"expected": 1, "present": 1, "missing": []},
        "manifest": {"records": 1},
        "code": {"base_revision": "abc"},
        "per_file": [
            {
                "filename": name,
                "parsed": {
                    "start_date": "2026-07-07",
                    "end_date": "2026-07-13",
                    "temporal": "7D",
                    "stream": "CYAN",
                },
                "class_pct": {"valid": 0.03, "below_detection": 11.1, "land": 88.9, "nodata": 0.0},
                "class_counts": {"valid": 1, "below_detection": 400, "land": 3199, "nodata": 0},
                "total_pixels": 3600,
                "dn_valid": {"max": 200},
                "processing_version_tag": "OBPG_version=6.0",
                "flags": [],
            }
        ],
    }


def test_snap_window_clamps_to_the_mosaic():
    transform = from_origin(ORIGIN[0], ORIGIN[1], 300.0, 300.0)
    win = b.snap_window(transform, 26328, 15138, -81.5, 42.0, 2000)
    assert win["width"] == 2000 and win["height"] == 2000
    assert 0 <= win["col"] <= 26328 - 2000 and 0 <= win["row"] <= 15138 - 2000
    edge = b.snap_window(transform, 100, 100, -81.5, 42.0, 40)
    assert edge == {"col": 60, "row": 60, "width": 40, "height": 40}
    small = b.snap_window(transform, 30, 30, -81.5, 42.0, 40)
    assert small == {"col": 0, "row": 0, "width": 30, "height": 30}


def test_class_counts_and_reprojection_preserve_codes():
    arr = np.full((40, 40), 254, np.uint8)
    arr[:20, :] = 0
    arr[0, :3] = [1, 130, 253]
    arr[1, :2] = 255
    counts = b.class_counts(arr)
    assert counts == {"below_detection": 795, "valid": 3, "land": 800, "nodata": 2, "dn_max": 253}
    transform = from_origin(1_000_000.0, 2_000_000.0, 300.0, 300.0)
    dst, alpha, _, geo = b.reproject_window(arr, transform)
    covered = dst[alpha > 0]
    assert set(np.unique(covered).tolist()) == {0, 1, 130, 253, 254, 255}
    assert geo["west"] < geo["east"] and geo["south"] < geo["north"]
    assert alpha.max() == 255
    # code 0 must survive: about half the covered pixels are below detection
    assert 0.4 < (covered == 0).sum() / covered.size < 0.6
    zeros = np.zeros((20, 20), np.uint8)
    dz, az, _, _ = b.reproject_window(zeros, transform)
    assert np.unique(dz[az > 0]).tolist() == [0], "code 0 must not be nudged to 1"


def test_png_data_url_roundtrip_keeps_values():
    gray = np.array([[0, 130], [254, 255]], np.uint8)
    alpha = np.array([[255, 255], [255, 0]], np.uint8)
    url = b.png_data_url(gray, alpha)
    assert url.startswith("data:image/png;base64,")
    img = Image.open(io.BytesIO(base64.b64decode(url.split(",", 1)[1])))
    back = np.array(img)
    assert back[..., 0].tolist() == gray.tolist() and back[..., 1].tolist() == alpha.tolist()
    js = b.frame_js("florida", "2026-07-07_7D", url)
    assert js.startswith('CYAN_FRAME("florida", "2026-07-07_7D", "data:image/png;base64,')


def test_build_writes_summary_and_frames(tmp_path):
    raw = tmp_path / "raw"
    raw.mkdir()
    arr = np.full((60, 60), 254, np.uint8)
    arr[10:30, 10:30] = 0
    arr[12, 12] = 200
    write_mosaic(raw / NAME, arr)
    qa = tmp_path / "qa-raw-2026-09-22T1200Z.json"
    qa.write_text(json.dumps(qa_stub(NAME)), encoding="utf-8")
    regions = tmp_path / "regions.json"
    corner = {"id": "corner", "label": "Top-left corner", "lon": -124.0, "lat": 49.0}
    regions.write_text(json.dumps({"default_size_px": 40, "regions": [corner]}), encoding="utf-8")
    out = tmp_path / "site"
    argv = ["--raw", str(raw), "--qa", str(qa), "--regions", str(regions), "--out", str(out)]
    argv += ["--basemap", str(tmp_path / "absent.geojson")]
    summary = b.build(b.parse_args(argv))
    assert summary["n_files"] == 1 and summary["regions"][0]["window"]["width"] == 40
    frame = summary["regions"][0]["frames"][0]
    counts = frame["counts"]
    assert frame["key"] == "2026-07-07_7D"
    assert counts["land"] + counts["below_detection"] + counts["valid"] == 1600
    js = (out / "data" / "frames" / "corner" / "2026-07-07_7D.js").read_text(encoding="utf-8")
    assert js.startswith('CYAN_FRAME("corner", "2026-07-07_7D", "data:image/png;base64,')
    text = (out / "data" / "summary.js").read_text(encoding="utf-8")
    assert text.startswith("window.CYAN_REVIEW = ") and '"record":[{' in text
    assert summary["record"][0]["rows"][0]["dn_max"] == 200
    assert summary["record"][0]["rows"][0]["counts"] == [1, 400, 3199, 0]
    assert summary["record"][0]["rows"][0]["total"] == 3600
    assert "sources" in summary["code"]
    assert not (out / "data" / "basemap_states.js").exists()


def test_select_files_last_n_per_cadence(tmp_path):
    raw = tmp_path / "raw"
    raw.mkdir()
    names = [
        "L20261882026194.L3m_7D_CYAN_CI_cyano_CYAN_CONUS_300m.tif",
        "L20261952026201.L3m_7D_CYAN_CI_cyano_CYAN_CONUS_300m.tif",
        "L2026209.L3m_DAY_CYAN_CI_cyano_CYAN_CONUS_300m.tif",
        "L2026209.L3m_DAY_CYAN_CI_cyano_CYAN_CONUS_300m_1_1.tif",
    ]
    for n in names:
        write_mosaic(raw / n, np.zeros((4, 4), np.uint8))
    files = b.select_files([str(raw)], "all")
    assert [f.filename for _, f in files] == [names[0], names[1], names[2]]
    last = b.select_files([str(raw)], "last:1")
    assert sorted(f.filename for _, f in last) == sorted([names[2], names[1]])
