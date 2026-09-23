#!/usr/bin/env python
"""Pull Natural Earth land and lake outlines for the dashboard's context layer.

Two public-domain zips at 1:50,000,000 from the Natural Earth bucket, no login. Cached and
sha256-manifested under data/basemap/raw/. Clipped to North America and written as one script
for file:// loading. Runs only when the owner invokes it.

Usage:
  uv run python datasets/cyan/viz/pull_basemap.py [--dry-run]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from datasets._common import net  # noqa: E402

RAW = REPO / "data" / "basemap" / "raw"
OUT = REPO / "docs" / "dashboards" / "cyan-lakes" / "data" / "basemap_land.js"
BASE = "https://naturalearth.s3.amazonaws.com/"
FILES = {
    "ne_50m_admin_0_countries.zip": BASE + "50m_cultural/ne_50m_admin_0_countries.zip",
    "ne_50m_lakes.zip": BASE + "50m_physical/ne_50m_lakes.zip",
}
BBOX = (-170.0, 5.0, -50.0, 85.0)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--outdir", default=str(RAW))
    ap.add_argument("--out", default=str(OUT))
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)
    out = Path(args.outdir)
    if args.dry_run:
        for name, url in FILES.items():
            print(f"[dry-run] would fetch {url} -> {out / name}")
        print(f"[dry-run] would write {args.out}")
        return 0
    import geopandas as gpd
    from shapely.geometry import box

    session = net.make_session()
    manifest = out / "manifest.jsonl"
    prior = {m["filename"]: m for m in net.read_manifest(manifest)}
    digests = {}
    for name, url in FILES.items():
        res = net.download_file(
            session, url, out / name, expected_sha256=(prior.get(name) or {}).get("sha256")
        )
        record = {
            "filename": name,
            "url": url,
            "bytes": res.bytes,
            "sha256": res.sha256,
            "cached": res.cached,
            "integrity": res.integrity,
            "accessed_utc": res.accessed_utc,
        }
        if not prior.get(name) or prior[name].get("sha256") != res.sha256:
            net.append_manifest(manifest, record)
        digests[name] = res.sha256
        print(f"[{'cached' if res.cached else 'fetched'}] {name} {res.bytes:,} B {res.sha256[:12]}")
    clip = box(*BBOX)
    countries = gpd.read_file(f"zip://{out / 'ne_50m_admin_0_countries.zip'}")
    countries = countries[countries.intersects(clip)][["NAME", "geometry"]].copy()
    countries["geometry"] = countries.geometry.intersection(clip)
    lakes = gpd.read_file(f"zip://{out / 'ne_50m_lakes.zip'}")
    lakes = lakes[lakes.intersects(clip)][["name", "geometry"]].copy()
    lakes["geometry"] = lakes.geometry.intersection(clip)
    payload = {
        "source": "Natural Earth 1:50m, public domain, admin 0 countries and lakes",
        "accessed_utc": net.utc_now_iso(),
        "sha256": digests,
        "bbox": list(BBOX),
        "countries": json.loads(countries.to_json(drop_id=True)),
        "lakes": json.loads(lakes.to_json(drop_id=True)),
    }
    text = "window.CYAN_LAND = " + json.dumps(payload, separators=(",", ":")) + ";\n"
    import re

    text = re.sub(r"(\d+\.\d{3})\d+", r"\1", text)
    Path(args.out).write_text(text, encoding="utf-8")
    print(f"[basemap] {len(countries)} countries, {len(lakes)} lakes -> {args.out} {len(text):,} B")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
