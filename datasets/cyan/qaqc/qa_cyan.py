#!/usr/bin/env python
"""QA/QC for pulled CyAN CI_cyano GeoTIFFs. Reads local files only. Contacts nothing.

For every raw directory given:
  * Inventory reconciliation: the approved plan, the manifest, the files on disk, and the
    files that open, each against the others.
  * Integrity: sha256 recomputed against the download manifest.
  * Structure: band count, data type, projection and EPSG code, pixel size, shape, transform,
    nodata flag, compression, metadata tags by namespace, and the processing-version tag.
  * Composition under the documented encoding: counts of code 0 below detection, codes 1 to
    253 data, code 254 land, and code 255 no data, with the data-code distribution.
  * Collection invariants: grid, projection, data type, band count, nodata flag, stream,
    and processing version must each take one value across the collection.
  * Completeness in time: expected dates from the plan's bounds, or from the filenames when
    no plan is given, against readable files. Unreadable files keep their filename dates.
    With a plan, missing dates split into dates the plan never listed, which are gaps in the
    search listing, and planned files that are absent or unreadable.
  * Manifest statistics: bytes, age at retrieval, integrity events, version tags.

Writes qa-<dir>-<stamp>.json per directory and one qa-report-<stamp>.md, where the stamp is
the run's UTC time. Reruns never overwrite an earlier result. Never edit a result by hand.

Exit status: 0 when every file is readable, every sha256 matches, the plan, the manifest, and
the disk hold the same files, and every collection invariant holds. 1 when any of those fails,
after the results are written. 2 for a usage error. Notes such as a varying land count or a
date the plan never listed do not change the status.

Usage:
  uv run python datasets/cyan/qaqc/qa_cyan.py \
      --raw data/cyan/raw/weekly_conus_mosaic --plan datasets/cyan/outputs/<weekly plan>.json \
      --raw data/cyan/raw/daily_conus_mosaic --plan datasets/cyan/outputs/<daily plan>.json
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[3]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from datasets._common import net, provenance  # noqa: E402
from datasets.cyan.access import cyan_api as c  # noqa: E402

DEFAULT_OUT = REPO / "datasets" / "cyan" / "outputs"
PERCENTILES = (50, 90, 99)
AGE_KEYS = ("age_at_retrieval_days", "latency_days")
INVARIANTS = ("crs", "epsg", "shape", "transform", "pixel_size_m", "dtype", "band_count")
INVARIANTS_EXTRA = ("nodata_flag", "stream", "processing_version_tag")
FATAL_FLAGS = ("unreadable", "sha256 differs from the manifest")


def version_tag(tags: dict) -> str | None:
    for k, v in tags.items():
        if "version" in k.lower():
            return f"{k}={v}"
    return None


def parsed_name(name: str) -> dict | None:
    f = c.parse_cyan_filename(name)
    if f is None:
        return None
    return {
        "stream": f.stream,
        "temporal": f.temporal,
        "tile": f.tile,
        "region": f.region,
        "start_date": f.start_date,
        "end_date": f.end_date,
    }


def qa_one(path: Path, manifest_rec: dict | None) -> dict:
    """QA one GeoTIFF. Reads the whole band once. An unreadable file keeps its name facts."""
    import rasterio

    rec: dict = {
        "filename": path.name,
        "bytes": path.stat().st_size,
        "parsed": parsed_name(path.name),
    }
    if manifest_rec:
        rec["manifest_sha256"] = manifest_rec.get("sha256")
        rec["sha256_ok"] = net.sha256_file(path) == manifest_rec.get("sha256")
    else:
        rec["sha256_ok"] = None

    try:
        with rasterio.open(path) as ds:
            rec["band_count"] = ds.count
            rec["dtype"] = ds.dtypes[0]
            rec["width"], rec["height"] = ds.width, ds.height
            rec["shape"] = f"{ds.width}x{ds.height}"
            rec["crs"] = ds.crs.to_string() if ds.crs else None
            rec["epsg"] = ds.crs.to_epsg() if ds.crs else None
            rec["transform"] = [round(v, 6) for v in tuple(ds.transform)[:6]]
            rec["pixel_size_m"] = [round(ds.res[0], 4), round(ds.res[1], 4)]
            rec["bounds"] = [round(v, 3) for v in ds.bounds]
            rec["nodata_flag"] = ds.nodata
            rec["compression"] = ds.profile.get("compress")
            rec["block_shape"] = list(ds.block_shapes[0]) if ds.block_shapes else None
            rec["tag_namespaces"] = sorted(ds.tag_namespaces())
            rec["tags"] = {ns: ds.tags(ns=ns) for ns in rec["tag_namespaces"]}
            rec["tags"]["default"] = ds.tags()
            rec["processing_version_tag"] = version_tag(ds.tags())
            arr = ds.read(1)
    except Exception as e:  # noqa: BLE001
        rec["error"] = repr(e)
        rec["flags"] = ["unreadable"]
        return rec

    total = int(arr.size)
    rec["total_pixels"] = total
    counts = np.bincount(arr.ravel(), minlength=256) if arr.dtype == np.uint8 else None
    if counts is not None:
        classes = {
            "below_detection": int(counts[c.DN_BELOW_DETECTION]),
            "valid": int(counts[c.DN_VALID_MIN : c.DN_VALID_MAX + 1].sum()),
            "land": int(counts[c.DN_LAND]),
            "nodata": int(counts[c.DN_NODATA]),
        }
        rec["class_counts"] = classes
        rec["class_pct"] = {k: round(100.0 * v / total, 4) for k, v in classes.items()}
        valid_counts = counts[c.DN_VALID_MIN : c.DN_VALID_MAX + 1]
        n_valid = int(valid_counts.sum())
        if n_valid:
            dns = np.arange(c.DN_VALID_MIN, c.DN_VALID_MAX + 1)
            cum = np.cumsum(valid_counts)
            pct = {p: int(dns[np.searchsorted(cum, p / 100 * n_valid)]) for p in PERCENTILES}
            rec["dn_valid"] = {
                "min": int(dns[valid_counts > 0][0]),
                "max": int(dns[valid_counts > 0][-1]),
                "mean": round(float((dns * valid_counts).sum() / n_valid), 3),
                **{f"p{p}": v for p, v in pct.items()},
            }
            rec["ci_max"] = float(c.dn_to_ci(np.array([rec["dn_valid"]["max"]]))[0])
        else:
            rec["dn_valid"] = None
            rec["ci_max"] = None
    else:
        rec["class_counts"] = None

    flags = []
    if rec["band_count"] != 1 or rec["dtype"] != "uint8":
        flags.append("not single-band uint8")
    crs_up = (rec["crs"] or "").upper()
    if rec["epsg"] != 5070 and "ALBERS" not in crs_up:
        flags.append(f"projection not Albers or EPSG:5070 ({rec['crs']})")
    if abs(rec["pixel_size_m"][0] - 300.0) > 0.5 or abs(rec["pixel_size_m"][1] - 300.0) > 0.5:
        flags.append(f"pixel size not 300 m ({rec['pixel_size_m']})")
    if rec.get("class_pct") and rec["class_pct"]["nodata"] >= 99.0:
        flags.append("almost entirely no data")
    if rec.get("class_counts") and rec["class_counts"]["valid"] == 0:
        flags.append("no data-class pixels")
    if rec["sha256_ok"] is False:
        flags.append("sha256 differs from the manifest")
    if rec["sha256_ok"] is None:
        flags.append("not in the manifest")
    if rec["processing_version_tag"] is None:
        flags.append("no version tag in the file metadata")
    if rec["parsed"] is None:
        flags.append("filename does not parse")
    rec["flags"] = flags
    return rec


def reconcile(
    planned: set[str] | None, manifest: set[str], disk: set[str], readable: set[str]
) -> dict:
    """Which names each inventory holds that another does not."""
    out = {
        "planned": len(planned) if planned is not None else None,
        "in_manifest": len(manifest),
        "on_disk": len(disk),
        "readable": len(readable),
        "planned_missing_on_disk": sorted(planned - disk) if planned is not None else [],
        "on_disk_not_planned": sorted(disk - planned) if planned is not None else [],
        "manifest_only": sorted(manifest - disk),
        "disk_only": sorted(disk - manifest),
        "unreadable": sorted(disk - readable),
    }
    return out


def expected_dates(
    records: list[dict],
    bounds: tuple[str, str] | None,
    temporal: str | None,
    planned_dates: set[str] | None = None,
) -> dict:
    """Expected start dates against readable files. Unreadable files keep their dates.

    With planned dates, each missing date is either one the plan never listed, a gap in the
    search listing, or a planned file that is absent or unreadable. Without a plan the split
    is None.
    """
    split = planned_dates is not None
    named = [r for r in records if r.get("parsed")]
    starts_all = sorted(r["parsed"]["start_date"] for r in named)
    if not starts_all and not bounds:
        return {
            "expected": 0,
            "present": 0,
            "missing": [],
            "missing_not_planned": [] if split else None,
            "missing_planned": [] if split else None,
            "unreadable_dates": [],
        }
    temporal = temporal or Counter(r["parsed"]["temporal"] for r in named).most_common(1)[0][0]
    step = 7 if temporal == "7D" else 1
    first, last = bounds if bounds else (starts_all[0], starts_all[-1])
    expected, d = [], dt.date.fromisoformat(first)
    while d <= dt.date.fromisoformat(last):
        expected.append(d.isoformat())
        d += dt.timedelta(days=step)
    readable = {r["parsed"]["start_date"] for r in named if "error" not in r}
    unreadable = sorted({r["parsed"]["start_date"] for r in named if "error" in r})
    missing = [e for e in expected if e not in readable]
    return {
        "temporal": temporal,
        "bounds_from": "plan" if bounds else "filenames on disk",
        "first": first,
        "last": last,
        "expected": len(expected),
        "present": sum(1 for e in expected if e in readable),
        "duplicates": len(starts_all) - len(set(starts_all)),
        "missing": missing,
        "missing_not_planned": [e for e in missing if e not in planned_dates] if split else None,
        "missing_planned": [e for e in missing if e in planned_dates] if split else None,
        "unreadable_dates": unreadable,
    }


def collection_checks(records: list[dict], inventory: dict) -> dict:
    """Invariants every readable file must share, plus notes that do not fail the run."""
    ok = [r for r in records if "error" not in r]
    values = {
        k: sorted({str(r.get(k)) for r in ok})
        for k in INVARIANTS + INVARIANTS_EXTRA
        if k != "stream"
    }
    values["stream"] = sorted({str((r.get("parsed") or {}).get("stream")) for r in ok})
    flags, notes = [], []
    for k in ("crs", "epsg", "shape", "transform", "pixel_size_m"):
        if len(values[k]) > 1:
            flags.append(f"grid differs across files: {k} takes {len(values[k])} values")
    for k in ("dtype", "band_count", "nodata_flag", "stream", "processing_version_tag"):
        if len(values[k]) > 1:
            flags.append(f"mixed {k}: {values[k]}")
    for k in (
        "planned_missing_on_disk",
        "on_disk_not_planned",
        "manifest_only",
        "disk_only",
        "unreadable",
    ):
        if inventory[k]:
            flags.append(f"{k}: {len(inventory[k])} file(s)")
    land = [r["class_counts"]["land"] for r in ok if r.get("class_counts")]
    if land and min(land) != max(land):
        notes.append(
            f"land count varies from {min(land):,} to {max(land):,} pixels, a spread of "
            f"{max(land) - min(land):,}. The spread is a lower bound on differing pixels"
        )
    n_sha_bad = sum(1 for r in ok if r.get("sha256_ok") is False)
    if n_sha_bad:
        flags.append(f"sha256 differs from the manifest: {n_sha_bad} file(s)")
    return {
        "n_files": len(records),
        "n_readable": len(ok),
        "values": values,
        "version_tags": dict(Counter(r.get("processing_version_tag") for r in ok)),
        "streams": dict(Counter((r.get("parsed") or {}).get("stream") for r in ok)),
        "compressions": sorted({str(r.get("compression")) for r in ok}),
        "tag_namespaces": sorted({ns for r in ok for ns in r.get("tag_namespaces", [])}),
        "default_tag_keys": sorted({k for r in ok for k in r.get("tags", {}).get("default", {})}),
        "land_count_min_max": [min(land), max(land)] if land else None,
        "grid_consistent": not any(f.startswith("grid differs") for f in flags),
        "collection_consistent": not flags,
        "collection_flags": flags,
        "notes": notes,
    }


def manifest_stats(manifest: list[dict]) -> dict:
    if not manifest:
        return {"records": 0}

    def age(m):
        return next((m[k] for k in AGE_KEYS if m.get(k) is not None), None)

    ages = [age(m) for m in manifest if age(m) is not None]
    newest = max(manifest, key=lambda m: m.get("end_date", ""))
    return {
        "records": len(manifest),
        "bytes_total": sum(m.get("bytes", 0) for m in manifest),
        "fetched": sum(1 for m in manifest if not m.get("cached")),
        "cached": sum(1 for m in manifest if m.get("cached")),
        "integrity": dict(Counter(m.get("integrity") for m in manifest)),
        "routes": dict(Counter(m.get("route") for m in manifest)),
        "version_tags": dict(Counter(m.get("processing_version") for m in manifest)),
        "accessed_first": min(m["accessed_utc"] for m in manifest),
        "accessed_last": max(m["accessed_utc"] for m in manifest),
        "age_at_retrieval_days": {
            "key_in_manifest": next((k for k in AGE_KEYS if newest.get(k) is not None), None),
            "min": min(ages),
            "median": float(np.median(ages)),
            "max": max(ages),
            "newest_file": age(newest),
            "newest_file_window_end": newest.get("end_date"),
        }
        if ages
        else None,
    }


def load_plan(path: Path | None) -> dict | None:
    if not path:
        return None
    plan = json.loads(path.read_text(encoding="utf-8"))
    period = plan.get("period")
    plan["_temporal"] = {"weekly": "7D", "daily": "DAY"}.get(period)
    plan["_bounds"] = None
    if plan.get("first") and plan.get("last"):
        a, b = c.parse_cyan_filename(plan["first"]), c.parse_cyan_filename(plan["last"])
        if a and b:
            plan["_bounds"] = (a.start_date, b.start_date)
    return plan


def qa_directory(raw: Path, plan: dict | None) -> dict:
    tifs = sorted(raw.glob("*.tif"))
    manifest = net.read_manifest(raw / "manifest.jsonl")
    by_name = {m["filename"]: m for m in manifest if "filename" in m}
    per_file = []
    for i, t in enumerate(tifs, 1):
        per_file.append(qa_one(t, by_name.get(t.name)))
        if i % 50 == 0:
            print(f"  [{i}/{len(tifs)}]")
    disk = {t.name for t in tifs}
    readable = {r["filename"] for r in per_file if "error" not in r}
    planned = set(plan["filenames"]) if plan and plan.get("filenames") else None
    planned_dates = None
    if planned is not None:
        planned_dates = {f.start_date for f in map(c.parse_cyan_filename, planned) if f}
    inventory = reconcile(planned, set(by_name), disk, readable)
    collection = collection_checks(per_file, inventory)
    bounds = plan["_bounds"] if plan else None
    temporal = plan["_temporal"] if plan else None
    completeness = expected_dates(per_file, bounds, temporal, planned_dates)
    if planned is None:
        collection["notes"].append(
            "no approved plan given. Completeness bounds come from the filenames on disk, so an "
            "absent first or last date cannot be detected"
        )
    if completeness.get("missing_not_planned"):
        collection["notes"].append(
            f"{len(completeness['missing_not_planned'])} expected date(s) the plan never "
            "listed: absent from the search listing. Not a physical archive check"
        )
    elif planned is None and completeness.get("missing"):
        collection["notes"].append(
            f"{len(completeness['missing'])} expected date(s) without a readable file. "
            "Absent from the search listing or from the pull. Not a physical archive check"
        )
    fatal = bool(collection["collection_flags"]) or any(
        f in FATAL_FLAGS for r in per_file for f in r.get("flags", [])
    )
    return {
        "raw_dir": provenance.rel(raw),
        "n_files": len(per_file),
        "n_files_with_flags": sum(1 for r in per_file if r.get("flags")),
        "flag_counts": dict(Counter(f for r in per_file for f in r.get("flags", []))),
        "fatal": fatal,
        "inventory": inventory,
        "collection": collection,
        "completeness": completeness,
        "manifest": manifest_stats(manifest),
        "per_file": per_file,
    }


def write_report(summaries: list[dict], path: Path, stamp: str) -> None:
    lines = [f"# CyAN QA/QC report, {stamp}\n"]
    for s in summaries:
        x, comp, man, inv = s["collection"], s["completeness"], s["manifest"], s["inventory"]
        v = x["values"]
        verdict = "FAIL" if s["fatal"] else "pass"
        lines.append(f"## `{s['raw_dir']}`: {verdict}\n")
        flags = s["flag_counts"] or "none"
        lines.append(
            f"{s['n_files']} files. {s['n_files_with_flags']} carry a flag. Flags: {flags}."
        )
        cflags, notes = x["collection_flags"] or "none", x["notes"] or "none"
        lines.append(f"Collection flags: {cflags}. Notes: {notes}.\n")
        lines.append("| Check | Result |\n|---|---|")
        counts = f"planned {inv['planned']}, manifest {inv['in_manifest']}, disk {inv['on_disk']}"
        lines.append(f"| Inventory | {counts}, readable {inv['readable']} |")
        gaps = (
            f"planned missing {len(inv['planned_missing_on_disk'])}, "
            f"not planned {len(inv['on_disk_not_planned'])}, "
            f"manifest only {len(inv['manifest_only'])}, disk only {len(inv['disk_only'])}, "
            f"unreadable {len(inv['unreadable'])}"
        )
        lines.append(f"| Inventory gaps | {gaps} |")
        lines.append(f"| Projection | {v['crs']} EPSG {v['epsg']} |")
        lines.append(f"| Shape and pixel size | {v['shape']} px, {v['pixel_size_m']} m |")
        layout = (
            f"{len(v['transform'])} transform(s), nodata {v['nodata_flag']}, {x['compressions']}"
        )
        lines.append(f"| Transform, nodata flag, compression | {layout} |")
        tags = f"{x['tag_namespaces']}, default keys {x['default_tag_keys']}"
        lines.append(f"| Tag namespaces | {tags} |")
        consistent = f"grid {x['grid_consistent']}, collection {x['collection_consistent']}"
        lines.append(f"| Consistent | {consistent} |")
        lines.append(f"| Version tags | {x['version_tags']} |")
        lines.append(f"| Streams | {x['streams']} |")
        span = f"{comp.get('temporal')} from {comp.get('first')} to {comp.get('last')}"
        bounds = f"bounds from {comp.get('bounds_from')}"
        present = f"{comp['present']} of {comp['expected']} expected dates readable"
        missing = f"missing {comp['missing'][:10]}"
        if comp.get("missing_planned") is not None:
            missing = (
                f"never planned {comp['missing_not_planned'][:10]}, "
                f"planned but not readable {comp['missing_planned'][:10]}"
            )
        lines.append(f"| Completeness | {span}, {bounds}: {present}, {missing} |")
        if man.get("records"):
            age = man.get("age_at_retrieval_days") or {}
            counts = f"fetched {man['fetched']}, cached {man['cached']}"
            events = f"integrity {man['integrity']}, routes {man['routes']}"
            size = f"{man['records']} records, {man['bytes_total']:,} bytes"
            lines.append(f"| Manifest | {size}, {counts}, {events} |")
            spread = f"min {age.get('min')}, median {age.get('median')}, max {age.get('max')}"
            newest_age, newest_end = age.get("newest_file"), age.get("newest_file_window_end")
            newest = f"newest file {newest_age} at window end {newest_end}"
            bound = "The newest file's age bounds the publication delay from above"
            lines.append(f"| Age at retrieval, days | {spread}. {newest}. {bound} |")
        lines.append("")
        head = "| File | Start | End | Stream | % data | % below detection | % land | % no data "
        lines.append(head + "| DN max | Version | Flags |")
        lines.append("|---|---|---|---|---|---|---|---|---|---|---|")
        for r in s["per_file"]:
            p, pct, dv = r.get("parsed") or {}, r.get("class_pct") or {}, r.get("dn_valid") or {}
            flag_text = ", ".join(r.get("flags", [])) or "ok"
            if "error" in r:
                flag_text += f" {r['error']}"
            cells = [
                r["filename"][:31],
                p.get("start_date", ""),
                p.get("end_date", ""),
                p.get("stream", ""),
                pct.get("valid", ""),
                pct.get("below_detection", ""),
                pct.get("land", ""),
                pct.get("nodata", ""),
                dv.get("max", ""),
                r.get("processing_version_tag") or "",
                flag_text,
            ]
            lines.append("| " + " | ".join(str(c) for c in cells) + " |")
        lines.append("")
    lines.append(
        "Composition is counted under the documented encoding: 0 below detection is a "
        "measurement, 1 to 253 data, 254 land, 255 no data. Those four classes partition every "
        "uint8 value, so the counts describe the files and do not validate the codes. "
        "Percentages are of the whole canvas, not of any lake. Version tags come from file "
        "metadata. See `../METADATA.md` sections 4 and 10."
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--raw", action="append", required=True, help="raw directory, repeatable")
    ap.add_argument(
        "--plan", action="append", default=[], help="approved plan JSON, one per --raw, in order"
    )
    ap.add_argument("--outdir", default=str(DEFAULT_OUT))
    ap.add_argument("--stamp", default=None, help="run stamp, default the current UTC time")
    args = ap.parse_args(argv)
    if args.plan and len(args.plan) != len(args.raw):
        print("[qa] give one --plan per --raw, in the same order, or none", file=sys.stderr)
        return 2
    out = Path(args.outdir)
    out.mkdir(parents=True, exist_ok=True)
    started = net.utc_now_iso()
    stamp = args.stamp or started.replace(":", "")[:15] + "Z"
    summaries, fatal = [], False
    for i, raw in enumerate(args.raw):
        raw_path = Path(raw) if Path(raw).is_absolute() else REPO / raw
        plan_path = Path(args.plan[i]) if args.plan else None
        if plan_path and not plan_path.is_absolute():
            plan_path = REPO / plan_path
        if not list(raw_path.glob("*.tif")):
            print(f"[qa] no .tif in {raw_path}", file=sys.stderr)
            return 2
        print(f"[qa] {raw_path}")
        s = qa_directory(raw_path, load_plan(plan_path))
        s["measured_at"] = started
        s["finished_at"] = net.utc_now_iso()
        s["code"] = provenance.code_provenance(
            [Path(__file__), Path(c.__file__), Path(net.__file__)],
            [raw_path / "manifest.jsonl"] + ([plan_path] if plan_path else []),
        )
        s["plan"] = provenance.rel(plan_path) if plan_path else None
        summaries.append(s)
        fatal = fatal or s["fatal"]
        jpath = out / f"qa-{raw_path.name}-{stamp}.json"
        jpath.write_text(json.dumps(s, indent=1), encoding="utf-8")
        print(
            f"[qa] {s['n_files']} files, {s['n_files_with_flags']} flagged, collection flags "
            f"{len(s['collection']['collection_flags'])}, completeness "
            f"{s['completeness']['present']}/{s['completeness']['expected']}, "
            f"{'FAIL' if s['fatal'] else 'pass'}, wrote {jpath.name}"
        )
    write_report(summaries, out / f"qa-report-{stamp}.md", stamp)
    print(f"[qa] wrote qa-report-{stamp}.md. Exit {1 if fatal else 0}")
    return 1 if fatal else 0


if __name__ == "__main__":
    raise SystemExit(main())
