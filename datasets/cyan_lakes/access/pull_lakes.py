#!/usr/bin/env python
"""Pull the CyAN lake and tile shapefiles published on the NASA Earthdata CyAN project page.

Two public zip files, no login. Claims cl-cyan-lakes-shapefile-link and
cl-cyan-lakes-conus-tile-shapefile in datasets/cyan/METADATA.md. Cached and sha256-manifested
under data/cyan_lakes/raw/. Runs only when the owner invokes it.

Usage:
  uv run python datasets/cyan_lakes/access/pull_lakes.py [--dry-run]
"""

from __future__ import annotations

import argparse
import sys
import zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from datasets._common import net  # noqa: E402

RAW = REPO / "data" / "cyan_lakes" / "raw"
FILES = {
    "MERIS_OLCI_Lakes.zip": "https://www.earthdata.nasa.gov/s3fs-public/2026-01/MERIS_OLCI_Lakes.zip",
    "CONUS_tiles_shapefile.zip": (
        "https://www.earthdata.nasa.gov/s3fs-public/2026-01/CONUS_tiles_shapefile.zip"
    ),
}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--outdir", default=str(RAW))
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)
    out = Path(args.outdir)
    if args.dry_run:
        for name, url in FILES.items():
            print(f"[dry-run] would fetch {url} -> {out / name}")
        return 0
    session = net.make_session()
    manifest = out / "manifest.jsonl"
    prior = {m["filename"]: m for m in net.read_manifest(manifest)}
    for name, url in FILES.items():
        res = net.download_file(
            session, url, out / name, expected_sha256=(prior.get(name) or {}).get("sha256")
        )
        with zipfile.ZipFile(out / name) as z:
            members = [(i.filename, i.file_size) for i in z.infolist()]
        record = {
            "filename": name,
            "url": url,
            "bytes": res.bytes,
            "sha256": res.sha256,
            "cached": res.cached,
            "integrity": res.integrity,
            "accessed_utc": res.accessed_utc,
            "members": members,
        }
        if not prior.get(name) or prior[name].get("sha256") != res.sha256:
            net.append_manifest(manifest, record)
        tag = "cached" if res.cached else "fetched"
        print(f"[{tag}] {name} {res.bytes:,} B sha256 {res.sha256[:12]} {res.integrity}")
        for member, size in members:
            print(f"        {member} ({size:,} B)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
