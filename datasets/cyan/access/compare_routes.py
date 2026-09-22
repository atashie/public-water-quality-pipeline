#!/usr/bin/env python
"""Compare the two CyAN access routes: the OB.DAAC archive and the Earthdata Cloud bucket.

The question, from docs/aws/cyan.md: does the cloud bucket hold the same files as the archive?
The comparison, per weekly whole-region file listed by the file search for a date range:
  1. HEAD the file through the cloud HTTPS endpoint with the Earthdata token. Present or not,
     and its byte count.
  2. Ask the temporary-credentials endpoint and try one bucket listing. Outside us-west-2 this
     is expected to be refused. The refusal is itself a measurement.
  3. Count the matching granules in the cloud catalog and note its newest one.
  4. Download a small sample of files that both routes hold, through both routes, and compare
     sha256. Identical digests mean identical bytes.

Writes one JSON result. Never edit it by hand. Rerun the script.
Contacts providers. Runs only when the owner invokes it. --dry-run enumerates only.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from datasets._common import net  # noqa: E402
from datasets.cyan.access import cyan_api as c  # noqa: E402

DEFAULT_OUT = REPO / "datasets" / "cyan" / "outputs" / "route-comparison.json"
DEFAULT_SAMPLE_DIR = REPO / "data" / "cyan" / "route-comparison"


def parse_args(argv=None):
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    p.add_argument("--sdate", required=True)
    p.add_argument("--edate", required=True)
    p.add_argument("--period", default="weekly", choices=["daily", "weekly"])
    p.add_argument("--tiles", default="all")
    p.add_argument("--sample", type=int, default=2, help="files to download through both routes")
    p.add_argument("--workers", type=int, default=8, help="parallel HEAD requests")
    p.add_argument("--out", default=str(DEFAULT_OUT))
    p.add_argument("--sample-dir", default=str(DEFAULT_SAMPLE_DIR))
    p.add_argument("--skip-s3", action="store_true", help="skip the credentials and listing test")
    p.add_argument("--dry-run", action="store_true")
    return p.parse_args(argv)


def git_revision() -> str | None:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"], cwd=REPO, text=True
        ).strip()
    except Exception:  # noqa: BLE001
        return None


def summarize_presence(files: list[c.CyanFile], heads: list[dict]) -> dict:
    """Which listed files the cloud endpoint holds. Pure function, tested offline."""
    by_name = {h["filename"]: h for h in heads}
    present, missing, statuses = [], [], {}
    for f in files:
        h = by_name.get(f.filename)
        status = h["status"] if h else None
        statuses[str(status)] = statuses.get(str(status), 0) + 1
        if h and h["status"] == 200 and h.get("bytes"):
            present.append(f)
        else:
            missing.append(f)
    newest_present = max((f.end_date for f in present), default=None)
    newest_listed = max((f.end_date for f in files), default=None)
    return {
        "listed": len(files),
        "present": len(present),
        "missing": len(missing),
        "status_counts": statuses,
        "newest_listed_window_end": newest_listed,
        "newest_present_window_end": newest_present,
        "missing_files": [f.filename for f in missing],
        "present_files": [f.filename for f in present],
    }


def cmr_count(session, pattern: str) -> dict:
    params = {
        "collection_concept_id": c.CMR_COLLECTION_OLCI,
        "readable_granule_name": pattern,
        "options[readable_granule_name][pattern]": "true",
        "sort_key": "-start_date",
        "page_size": 1,
    }
    r = session.get(c.CMR_GRANULES_URL, params=params, timeout=60)
    entries = r.json()["feed"]["entry"] if r.status_code == 200 else []
    return {
        "status": r.status_code,
        "hits": int(r.headers.get("CMR-Hits", 0) or 0),
        "newest": entries[0]["title"] if entries else None,
        "newest_time_end": entries[0].get("time_end") if entries else None,
    }


def try_s3(session, token: str) -> dict:
    """Ask for temporary credentials and try one listing. Records outcomes, never secrets."""
    status, creds = c.get_s3_credentials(session, token)
    out = {"credentials_status": status, "credentials_received": bool(creds)}
    if not creds:
        return out
    out["credentials_expiration"] = creds.get("expiration")
    try:
        import boto3
        from botocore.exceptions import ClientError

        s3 = boto3.client(
            "s3",
            region_name=c.S3_REGION,
            aws_access_key_id=creds["accessKeyId"],
            aws_secret_access_key=creds["secretAccessKey"],
            aws_session_token=creds["sessionToken"],
        )
        try:
            resp = s3.list_objects_v2(Bucket=c.S3_BUCKET, Prefix="L2026", MaxKeys=5)
            keys = [o["Key"] for o in resp.get("Contents", [])]
            out["listing"] = {"ok": True, "sample_keys": keys, "key_count": resp.get("KeyCount")}
        except ClientError as e:
            out["listing"] = {"ok": False, "error_code": e.response["Error"].get("Code")}
    except Exception as e:  # noqa: BLE001
        out["listing"] = {"ok": False, "error": type(e).__name__}
    return out


def sample_compare(session, token: str, files: list[c.CyanFile], sample_dir: Path) -> list[dict]:
    results = []
    for f in files:
        rec = {"filename": f.filename}
        for route, url in (("getfile", f.url), ("tea", c.tea_url(f.filename))):
            dest = sample_dir / route / f.filename
            try:
                res = net.download_file(session, url, dest, bearer_token=token)
                rec[route] = {"bytes": res.bytes, "sha256": res.sha256}
            except Exception as e:  # noqa: BLE001
                rec[route] = {"error": f"{type(e).__name__}: {e}"[:200]}
        a, b = rec.get("getfile", {}).get("sha256"), rec.get("tea", {}).get("sha256")
        rec["identical"] = bool(a and b and a == b)
        results.append(rec)
    return results


def main(argv=None) -> int:
    args = parse_args(argv)
    session = net.make_session()
    started = net.utc_now_iso()
    urls = c.search_files(session, "conus", args.period, "ci", args.tiles, args.sdate, args.edate)
    cats = c.categorize_search_results(urls)
    files = sorted(cats["merged"], key=lambda f: (f.start_date, f.stream))
    print(f"[search] {len(urls)} URLs, {len(files)} merged files, {args.sdate}..{args.edate}")
    if args.dry_run:
        print(f"[dry-run] would HEAD {len(files)} files and download {args.sample} samples twice")
        return 0

    token = net.resolve_edl_token()
    if not token:
        print("[error] OB_DAAC_EDL_TOKEN is required. See .env.example.", file=sys.stderr)
        return 2

    print(f"[tea] HEAD {len(files)} files with {args.workers} workers")
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        heads = list(pool.map(lambda f: c.tea_head(session, f.filename, token), files))
    presence = summarize_presence(files, heads)
    print(
        f"[tea] present={presence['present']} missing={presence['missing']} "
        f"newest present window end={presence['newest_present_window_end']} "
        f"newest listed={presence['newest_listed_window_end']}"
    )

    pattern = (
        "*7D_CYAN_CI_cyano_CYAN_CONUS_300m.tif"
        if args.period == "weekly"
        else "*DAY_CYAN_CI_cyano_CYAN_CONUS_300m.tif"
    )
    cmr = cmr_count(session, pattern)
    print(f"[cmr] hits={cmr['hits']} newest={cmr['newest']}")

    s3 = None if args.skip_s3 else try_s3(session, token)
    if s3 is not None:
        print(f"[s3] credentials status={s3['credentials_status']} listing={s3.get('listing')}")

    present_files = [f for f in files if f.filename in set(presence["present_files"])]
    chosen = sorted(present_files, key=lambda f: f.end_date)[-args.sample :] if args.sample else []
    samples = sample_compare(session, token, chosen, Path(args.sample_dir)) if chosen else []
    for s in samples:
        print(f"[sample] {s['filename']} identical={s['identical']}")

    result = {
        "measured_at": started,
        "finished_at": net.utc_now_iso(),
        "code_version": git_revision(),
        "search": {
            "period": args.period,
            "tiles": args.tiles,
            "sdate": args.sdate,
            "edate": args.edate,
            "urls": len(urls),
            "merged": len(files),
            "per_satellite_excluded": len(cats["per_satellite"]),
            "other_excluded": len(cats["other"]),
            "first": files[0].filename if files else None,
            "last": files[-1].filename if files else None,
            "streams": sorted({f.stream for f in files}),
        },
        "tea": presence,
        "cmr": cmr,
        "s3": s3,
        "samples": samples,
        "head_details": heads,
        "limitations": [
            "One day of measurement. Presence and newest dates drift as the archive grows.",
            "A HEAD through the HTTPS endpoint tests one object. It does not list the bucket.",
            "The credentials and listing test runs from outside us-west-2 unless stated otherwise.",
            "Byte comparison covers only the sampled files.",
        ],
    }
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"[done] result written to {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
