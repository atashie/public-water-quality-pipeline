"""Offline tests for the QA/QC script on synthetic GeoTIFFs. No network."""

import json

import numpy as np
import pytest
import rasterio
from rasterio.transform import from_origin

from datasets._common import net
from datasets.cyan.qaqc import qa_cyan

NAMES = [
    "L20261882026194.L3m_7D_CYAN_CI_cyano_CYAN_CONUS_300m.tif",
    "L20261952026201.L3m_7D_CYAN_CI_cyano_CYAN_CONUS_300m.tif",
    "L20262092026215.L3m_7D_CYAN_CI_cyano_CYAN_CONUS_300m.tif",
]
STARTS = ["2026-07-07", "2026-07-14", "2026-07-28"]


def write_tif(path, arr, version="6.0", pixel=300.0, epsg=5070):
    transform = from_origin(1_000_000.0, 2_000_000.0, pixel, pixel)
    with rasterio.open(
        path,
        "w",
        driver="GTiff",
        height=arr.shape[0],
        width=arr.shape[1],
        count=1,
        dtype="uint8",
        crs=f"EPSG:{epsg}",
        transform=transform,
        compress="deflate",
    ) as ds:
        ds.write(arr, 1)
        if version:
            ds.update_tags(OBPG_version=version)


def base_array():
    base = np.full((10, 10), 254, dtype=np.uint8)  # land everywhere
    base[:5, :] = 0  # below detection on the top half
    base[0, :3] = [1, 130, 253]  # three data pixels
    base[1, :2] = 255  # two no-data pixels
    return base


def manifest_record(path, latency, end_date, sha=None):
    return {
        "filename": path.name,
        "sha256": sha or net.sha256_file(path),
        "bytes": path.stat().st_size,
        "cached": False,
        "integrity": "unverified",
        "route": "getfile",
        "processing_version": "OBPG_version=6.0",
        "accessed_utc": "2026-09-22T12:00:00Z",
        "age_at_retrieval_days": latency,
        "end_date": end_date,
    }


def make_dir(tmp_path, versions=("6.0", "6.0", "6.0"), bad_digest=False, manifest=True):
    tmp_path.mkdir(parents=True, exist_ok=True)
    for i, name in enumerate(NAMES):
        arr = base_array()
        if i == 2:
            arr[4, 9] = 200  # one more data pixel, replacing a below-detection pixel
        write_tif(tmp_path / name, arr, version=versions[i])
    if manifest:
        for i, name in enumerate(NAMES):
            sha = "0" * 64 if (bad_digest and i == 2) else None
            net.append_manifest(
                tmp_path / "manifest.jsonl",
                manifest_record(tmp_path / name, 2 + i, f"2026-07-{13 + 7 * i:02d}", sha),
            )
    return tmp_path


def plan_file(tmp_path, filenames, period="weekly"):
    plan = {
        "period": period,
        "planned": len(filenames),
        "first": filenames[0],
        "last": filenames[-1],
        "filenames": filenames,
    }
    p = tmp_path / "plan.json"
    p.write_text(json.dumps(plan), encoding="utf-8")
    return p


def test_qa_one_counts_classes_and_reads_structure(tmp_path):
    raw = make_dir(tmp_path)
    manifest = {m["filename"]: m for m in net.read_manifest(raw / "manifest.jsonl")}
    rec = qa_cyan.qa_one(raw / NAMES[0], manifest[NAMES[0]])
    assert rec["class_counts"] == {"below_detection": 45, "valid": 3, "land": 50, "nodata": 2}
    assert rec["total_pixels"] == 100
    assert rec["epsg"] == 5070 and rec["pixel_size_m"] == [300.0, 300.0]
    assert rec["dtype"] == "uint8" and rec["band_count"] == 1
    assert rec["processing_version_tag"] == "OBPG_version=6.0"
    assert "IMAGE_STRUCTURE" in rec["tag_namespaces"]
    assert rec["tags"]["default"]["OBPG_version"] == "6.0"
    assert rec["sha256_ok"] is True
    assert rec["dn_valid"]["min"] == 1 and rec["dn_valid"]["max"] == 253
    assert rec["dn_valid"]["p50"] == 130
    assert rec["ci_max"] == pytest.approx(10 ** (253 * 0.011714 - 4.1870866))
    assert rec["flags"] == []
    assert rec["parsed"]["start_date"] == STARTS[0]


def test_flags_for_missing_tag_bad_digest_and_orphan(tmp_path):
    raw = make_dir(tmp_path, versions=("6.0", None, "6.0"), bad_digest=True)
    manifest = {m["filename"]: m for m in net.read_manifest(raw / "manifest.jsonl")}
    no_tag = qa_cyan.qa_one(raw / NAMES[1], manifest[NAMES[1]])
    assert "no version tag in the file metadata" in no_tag["flags"]
    bad = qa_cyan.qa_one(raw / NAMES[2], manifest[NAMES[2]])
    assert "sha256 differs from the manifest" in bad["flags"]
    orphan = qa_cyan.qa_one(raw / NAMES[0], None)
    assert "not in the manifest" in orphan["flags"]


def test_projection_and_pixel_flags(tmp_path):
    write_tif(tmp_path / NAMES[0], np.zeros((4, 4), dtype=np.uint8), pixel=250.0, epsg=4326)
    rec = qa_cyan.qa_one(tmp_path / NAMES[0], None)
    assert any(f.startswith("projection not Albers") for f in rec["flags"])
    assert any(f.startswith("pixel size not 300 m") for f in rec["flags"])
    assert "no data-class pixels" in rec["flags"]


def test_unreadable_file_keeps_its_name_facts_and_is_fatal(tmp_path):
    raw = make_dir(tmp_path)
    (raw / NAMES[1]).write_bytes(b"not a tiff")
    rec = qa_cyan.qa_one(raw / NAMES[1], None)
    assert rec["flags"] == ["unreadable"] and "error" in rec
    assert rec["parsed"]["start_date"] == STARTS[1]
    s = qa_cyan.qa_directory(raw, qa_cyan.load_plan(plan_file(raw, NAMES)))
    assert s["fatal"] is True
    assert s["inventory"]["unreadable"] == [NAMES[1]]
    assert s["completeness"]["unreadable_dates"] == [STARTS[1]]
    assert STARTS[1] in s["completeness"]["missing"]
    assert s["completeness"]["missing_planned"] == [STARTS[1]]
    assert s["completeness"]["missing_not_planned"] == ["2026-07-21"]


def test_clean_directory_with_plan_passes(tmp_path):
    raw = make_dir(tmp_path)
    s = qa_cyan.qa_directory(raw, qa_cyan.load_plan(plan_file(raw, NAMES)))
    assert s["fatal"] is False and s["collection"]["collection_flags"] == []
    comp = s["completeness"]
    assert comp["bounds_from"] == "plan" and comp["expected"] == 4 and comp["present"] == 3
    assert comp["missing"] == ["2026-07-21"]
    assert comp["missing_not_planned"] == ["2026-07-21"] and comp["missing_planned"] == []
    x = s["collection"]
    assert x["grid_consistent"] and x["collection_consistent"]
    assert x["values"]["epsg"] == ["5070"] and x["version_tags"] == {"OBPG_version=6.0": 3}
    assert x["land_count_min_max"] == [50, 50] and x["notes"][0].startswith("1 expected date")
    m = s["manifest"]
    age = m["age_at_retrieval_days"]
    assert age["min"] == 2 and age["max"] == 4 and age["newest_file"] == 4
    assert age["key_in_manifest"] == "age_at_retrieval_days"
    assert s["inventory"]["planned"] == 3 and s["inventory"]["planned_missing_on_disk"] == []


def test_mixed_versions_fail_the_collection(tmp_path):
    raw = make_dir(tmp_path, versions=("6.0", "7.0", "6.0"))
    s = qa_cyan.qa_directory(raw, None)
    assert s["fatal"] is True
    assert any(
        f.startswith("mixed processing_version_tag") for f in s["collection"]["collection_flags"]
    )
    assert s["collection"]["grid_consistent"] is True
    assert s["collection"]["collection_consistent"] is False


def test_planned_file_missing_on_disk_is_fatal_even_without_manifest_record(tmp_path):
    raw = make_dir(tmp_path)
    (raw / NAMES[0]).unlink()
    manifest = [m for m in net.read_manifest(raw / "manifest.jsonl") if m["filename"] != NAMES[0]]
    (raw / "manifest.jsonl").write_text(
        "".join(json.dumps(m) + "\n" for m in manifest), encoding="utf-8"
    )
    s = qa_cyan.qa_directory(raw, qa_cyan.load_plan(plan_file(raw, NAMES)))
    assert s["fatal"] is True
    assert s["inventory"]["planned_missing_on_disk"] == [NAMES[0]]
    assert s["completeness"]["bounds_from"] == "plan"
    assert s["completeness"]["expected"] == 4 and STARTS[0] in s["completeness"]["missing"]
    assert s["completeness"]["missing_planned"] == [STARTS[0]]
    assert s["completeness"]["missing_not_planned"] == ["2026-07-21"]


def test_unplanned_file_on_disk_is_a_collection_flag(tmp_path):
    raw = make_dir(tmp_path)
    s = qa_cyan.qa_directory(raw, qa_cyan.load_plan(plan_file(raw, NAMES[:2])))
    assert s["fatal"] is True
    assert s["inventory"]["on_disk_not_planned"] == [NAMES[2]]
    assert "on_disk_not_planned: 1 file(s)" in s["collection"]["collection_flags"]
    comp = s["completeness"]
    assert comp["bounds_from"] == "plan" and comp["expected"] == 2 and comp["missing"] == []


def test_without_a_plan_the_bounds_come_from_disk_and_the_notes_say_so(tmp_path):
    raw = make_dir(tmp_path)
    s = qa_cyan.qa_directory(raw, None)
    comp = s["completeness"]
    assert comp["bounds_from"] == "filenames on disk" and comp["missing"] == ["2026-07-21"]
    assert comp["missing_not_planned"] is None and comp["missing_planned"] is None
    assert s["collection"]["notes"][0].startswith("no approved plan given")
    assert s["collection"]["notes"][1].startswith("1 expected date(s) without a readable file")
    assert s["fatal"] is False


def test_legacy_latency_key_is_still_read(tmp_path):
    raw = make_dir(tmp_path, manifest=False)
    for i, name in enumerate(NAMES):
        rec = manifest_record(raw / name, 5, f"2026-07-{13 + 7 * i:02d}")
        rec["latency_days"] = rec.pop("age_at_retrieval_days")
        net.append_manifest(raw / "manifest.jsonl", rec)
    m = qa_cyan.manifest_stats(net.read_manifest(raw / "manifest.jsonl"))
    assert m["age_at_retrieval_days"]["key_in_manifest"] == "latency_days"
    assert m["age_at_retrieval_days"]["max"] == 5


def test_main_exit_codes_and_dated_outputs(tmp_path):
    raw = make_dir(tmp_path / "clean")
    plan = plan_file(raw, NAMES)
    out = tmp_path / "out"
    argv = ["--raw", str(raw), "--plan", str(plan), "--outdir", str(out)]
    rc = qa_cyan.main([*argv, "--stamp", "2026-09-22T1200Z"])
    assert rc == 0
    j = json.loads((out / "qa-clean-2026-09-22T1200Z.json").read_text())
    assert j["measured_at"].endswith("Z") and j["n_files"] == 3 and j["fatal"] is False
    assert "sources" in j["code"] and any(k.endswith("qa_cyan.py") for k in j["code"]["sources"])
    assert any(k.endswith("manifest.jsonl") for k in j["code"]["inputs"])
    assert any(k.endswith("plan.json") for k in j["code"]["inputs"])
    report = (out / "qa-report-2026-09-22T1200Z.md").read_text()
    assert "# CyAN QA/QC report, 2026-09-22T1200Z" in report and ": pass" in report
    assert "never planned ['2026-07-21'], planned but not readable []" in report

    bad = make_dir(tmp_path / "bad", bad_digest=True)
    rc = qa_cyan.main(["--raw", str(bad), "--outdir", str(out), "--stamp", "2026-09-22T1201Z"])
    assert rc == 1
    assert ": FAIL" in (out / "qa-report-2026-09-22T1201Z.md").read_text()
    assert (out / "qa-clean-2026-09-22T1200Z.json").exists(), "earlier results are kept"
