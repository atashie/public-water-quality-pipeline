#!/usr/bin/env python
"""Acquire CyAN CI_cyano files for a region, period, tile set, and date range.

Reproducible, cached, and auditable:
  * Enumerates files through the no-login file search.
  * Reports the merged versus per-satellite split with counts. Nothing is dropped silently.
  * Collapses the two name streams to one file per date, preferring the CYAN stream.
  * Downloads only what is missing, through the archive (getfile) or the cloud HTTPS
    endpoint (tea). Every file lands in a JSONL manifest with sha256, bytes, the version tag
    read from the file, the age at retrieval, and the access time.

Downloads need OB_DAAC_EDL_TOKEN or OB_DAAC_APPKEY in the repository's .env. --dry-run needs
nothing and contacts only the search endpoint. This script runs only when the owner invokes it.

Examples
--------
  uv run python datasets/cyan/access/pull_cyan.py --period weekly --tiles all \
      --sdate 2016-01-01 --edate 2026-09-22 --dry-run
  uv run python datasets/cyan/access/pull_cyan.py --period daily --tiles all \
      --sdate 2026-07-28 --edate 2026-09-22 --limit 3
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from datasets._common import net, provenance  # noqa: E402
from datasets.cyan.access import cyan_api as c  # noqa: E402

DEFAULT_RAW = REPO / "data" / "cyan" / "raw"


def parse_args(argv=None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    p.add_argument("--region", default="conus", choices=["conus", "alaska", "ak"])
    p.add_argument("--period", default="weekly", choices=["daily", "weekly"])
    p.add_argument("--product", default="ci", choices=["ci", "truecolor"])
    p.add_argument(
        "--tiles",
        default="all",
        help="'all' for the whole-region file, one tile '7_2', or tiles joined with '+'",
    )
    p.add_argument("--sdate", required=True, help="start date YYYY-MM-DD")
    p.add_argument("--edate", required=True, help="end date YYYY-MM-DD")
    p.add_argument("--stream", default="CYAN", help="preferred name stream, default CYAN")
    p.add_argument("--route", default="getfile", choices=["getfile", "tea"])
    p.add_argument("--outdir", default=None, help="download directory")
    p.add_argument(
        "--manifest", default=None, help="manifest path, default <outdir>/manifest.jsonl"
    )
    p.add_argument("--limit", type=int, default=0, help="cap the number of files, 0 for no cap")
    p.add_argument("--dry-run", action="store_true", help="enumerate and plan only")
    p.add_argument("--plan-json", default=None, help="write the plan summary to this path")
    p.add_argument(
        "--plan",
        default=None,
        help="an approved plan JSON to execute. The fresh search must list the same files",
    )
    p.add_argument(
        "--accept-drift",
        action="store_true",
        help="continue when the fresh search differs from the approved plan",
    )
    return p.parse_args(argv)


def default_outdir(region: str, period: str, tiles: str) -> Path:
    scope = "mosaic" if tiles == "all" else tiles.replace("+", "-")
    return DEFAULT_RAW / f"{period}_{region}_{scope}"


def build_plan(urls: list[str], preferred_stream: str, limit: int = 0) -> dict:
    """Categorize search results, collapse streams, and cap. Pure function, tested offline."""
    cats = c.categorize_search_results(urls)
    plan = c.prefer_stream(cats["merged"], preferred=preferred_stream)
    n_pref = sum(1 for f in plan if f.stream == preferred_stream)
    capped = plan[:limit] if limit and len(plan) > limit else plan
    return {
        "urls": len(urls),
        "merged": len(cats["merged"]),
        "per_satellite_excluded": len(cats["per_satellite"]),
        "other_excluded": len(cats["other"]),
        "after_stream_collapse": len(plan),
        "preferred_stream": preferred_stream,
        "preferred_stream_count": n_pref,
        "fallback_stream_count": len(plan) - n_pref,
        "limit": limit,
        "planned": len(capped),
        "first": capped[0].filename if capped else None,
        "last": capped[-1].filename if capped else None,
        "files": capped,
    }


def plan_drift(approved: list[str], fresh: list[str]) -> dict:
    """Files the fresh search added or removed against an approved selection."""
    a, f = set(approved), set(fresh)
    return {"added": sorted(f - a), "removed": sorted(a - f), "same": a == f}


def age_at_retrieval_days(end_date: str, accessed_utc: str) -> int:
    """Whole days from the composite's window end to the access time.

    This is the file's age when retrieved, not the provider's publication delay. For the
    newest file it bounds the publication delay from above. For an old file it is history.
    """
    end = dt.date.fromisoformat(end_date)
    accessed = dt.datetime.strptime(accessed_utc, "%Y-%m-%dT%H:%M:%SZ").date()
    return (accessed - end).days


def main(argv=None) -> int:
    args = parse_args(argv)
    outdir = (
        Path(args.outdir) if args.outdir else default_outdir(args.region, args.period, args.tiles)
    )
    manifest = Path(args.manifest) if args.manifest else outdir / "manifest.jsonl"
    session = net.make_session()

    print(
        f"[search] region={args.region} period={args.period} product={args.product} "
        f"tiles={args.tiles} {args.sdate}..{args.edate}"
    )
    searched_at = net.utc_now_iso()
    urls = c.search_files(
        session, args.region, args.period, args.product, args.tiles, args.sdate, args.edate
    )
    plan = build_plan(urls, args.stream, args.limit)
    files = plan.pop("files")
    print(
        f"[search] {plan['urls']} URLs: merged={plan['merged']}, "
        f"per-satellite excluded={plan['per_satellite_excluded']}, "
        f"other excluded={plan['other_excluded']}"
    )
    print(
        f"[plan]   {plan['after_stream_collapse']} files after collapsing streams "
        f"({plan['preferred_stream_count']} {args.stream}, "
        f"{plan['fallback_stream_count']} fallback)"
    )
    if plan["limit"] and plan["after_stream_collapse"] > plan["limit"]:
        print(f"[plan]   LIMIT: first {plan['planned']} of {plan['after_stream_collapse']} files")
    summary = {
        **plan,
        "filenames": [f.filename for f in files],
        "searched_at": searched_at,
        "region": args.region,
        "period": args.period,
        "tiles": args.tiles,
        "sdate": args.sdate,
        "edate": args.edate,
        "route": args.route,
        "outdir": str(outdir),
        "streams": sorted({f.stream for f in files}),
        "years": sorted({f.start_date[:4] for f in files}),
        "code": provenance.code_provenance([Path(__file__), Path(c.__file__)]),
    }
    if args.plan:
        approved = json.loads(Path(args.plan).read_text(encoding="utf-8"))
        drift = plan_drift(approved.get("filenames", []), summary["filenames"])
        summary["approved_plan"] = {
            "path": args.plan,
            "sha256": net.sha256_file(Path(args.plan)),
            "planned": approved.get("planned"),
            "drift": drift,
        }
        if not drift["same"]:
            print(
                f"[plan]   DRIFT against {args.plan}: {len(drift['added'])} added, "
                f"{len(drift['removed'])} removed"
            )
            for name in drift["added"][:10]:
                print(f"           + {name}")
            for name in drift["removed"][:10]:
                print(f"           - {name}")
            if not (args.dry_run or args.accept_drift):
                print("[plan]   refusing to download. Pass --accept-drift to continue.")
                return 3
        else:
            print(f"[plan]   matches the approved plan {args.plan}")
    if args.plan_json:
        Path(args.plan_json).parent.mkdir(parents=True, exist_ok=True)
        Path(args.plan_json).write_text(json.dumps(summary, indent=2), encoding="utf-8")
        print(f"[plan]   summary written to {args.plan_json}")

    if args.dry_run:
        for f in files:
            print(
                f"          {f.start_date}..{f.end_date} {f.temporal:3s} {f.stream:8s} "
                f"{f.tile:14s} {f.filename}"
            )
        print(f"[dry-run] {len(files)} files would be downloaded to {outdir}. Nothing fetched.")
        return 0

    bearer = net.resolve_edl_token()
    appkey = net.resolve_appkey()
    if not (bearer or appkey):
        print(
            "[error] No credentials. Set OB_DAAC_EDL_TOKEN or OB_DAAC_APPKEY in .env, "
            "see .env.example. Use --dry-run to plan without them.",
            file=sys.stderr,
        )
        return 2
    if args.route == "tea" and not bearer:
        print("[error] The tea route needs OB_DAAC_EDL_TOKEN.", file=sys.stderr)
        return 2
    print(f"[auth] using {'bearer token' if bearer else 'appkey'}, route {args.route}")

    prior = {rec["filename"]: rec for rec in net.read_manifest(manifest) if rec.get("filename")}
    print(f"[download] -> {outdir}  (manifest: {manifest})")
    ok = skipped = failed = mismatched = 0
    for i, f in enumerate(files, 1):
        dest = outdir / f.filename
        url = c.tea_url(f.filename) if args.route == "tea" else f.url
        try:
            prior_rec = prior.get(f.filename)
            res = net.download_file(
                session,
                url,
                dest,
                appkey=None if args.route == "tea" else appkey,
                bearer_token=bearer,
                expected_sha256=(prior_rec or {}).get("sha256"),
            )
            version = c.read_processing_version(dest)
            record = {
                "filename": f.filename,
                "url": url,
                "route": args.route,
                "bytes": res.bytes,
                "sha256": res.sha256,
                "cached": res.cached,
                "integrity": res.integrity,
                "processing_version": version,
                "accessed_utc": res.accessed_utc,
                "age_at_retrieval_days": age_at_retrieval_days(f.end_date, res.accessed_utc),
                "approved_plan_sha256": summary.get("approved_plan", {}).get("sha256"),
                "sensor": f.sensor_code,
                "temporal": f.temporal,
                "stream": f.stream,
                "region": f.region,
                "tile": f.tile,
                "start_date": f.start_date,
                "end_date": f.end_date,
                "is_mosaic": f.is_mosaic,
            }
            if (
                not prior_rec
                or prior_rec.get("sha256") != res.sha256
                or res.integrity == "refetched_stale_cache"
            ):
                net.append_manifest(manifest, record)
            if res.integrity in ("mismatch", "refetched_stale_cache"):
                mismatched += 1
                print(
                    f"  [{i}/{len(files)}] integrity {res.integrity}: {f.filename}", file=sys.stderr
                )
            if res.cached:
                skipped += 1
            else:
                ok += 1
            tag = "cached" if res.cached else "fetched"
            print(f"  [{i}/{len(files)}] {tag} {f.filename} ({res.bytes:,} B, version {version})")
        except Exception as e:  # noqa: BLE001
            failed += 1
            print(f"  [{i}/{len(files)}] FAILED {f.filename}: {e}", file=sys.stderr)

    print(
        f"[done] fetched={ok} cached={skipped} failed={failed} "
        f"integrity_events={mismatched} planned={len(files)}"
    )
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
