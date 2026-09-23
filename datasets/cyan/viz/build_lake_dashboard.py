#!/usr/bin/env python
"""Build the user-facing CyAN lake dashboard from the per-lake table of decision 0002.

Reads local files only. Contacts nothing. Outputs under docs/dashboards/cyan-lakes/:
  data/lakes.js       one record per lake with its centroid, size, the newest week's state,
                      the run of consecutive weeks at or above the threshold, and coverage
  data/lakes/<comid>.js   the lake's full weekly and daily series, loaded on demand
  data/pixels/<comid>.js  the lake's pixels from the newest weekly file, a coloured PNG in Web
                          Mercator with its bounds, a grey PNG carrying the raw codes for the
                          hover readout, and the lake's exact outline in WGS84, loaded on demand
It also writes the companion attribute table under data/cyan/derived/: one row per lake with
centroid, bounds, pixel window, and the interior cell indices of decision 0002.

The threshold is the EPA forecast code's operationalization, a median code of 130, quoted in
the probe record of 2026-09-23. The page lets the reader move it. Nothing here is a forecast.

Usage:
  uv run python datasets/cyan/viz/build_lake_dashboard.py --table data/cyan/derived/<table>.parquet
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[3]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from datasets._common import net, provenance  # noqa: E402
from datasets.cyan.access import cyan_api as c  # noqa: E402
from datasets.cyan.derive import build_lake_table as lt  # noqa: E402

OUT = REPO / "docs" / "dashboards" / "cyan-lakes"
DERIVED = REPO / "data" / "cyan" / "derived"
LAKES_ZIP = REPO / "data" / "cyan_lakes" / "raw" / "MERIS_OLCI_Lakes.zip"
NAMES_DIR = REPO / "datasets" / "cyan_lakes" / "outputs"
STATES = REPO / "docs" / "dashboards" / "cyan" / "data" / "basemap_states.geojson"
WEEKLY_RAW = REPO / "data" / "cyan" / "raw" / "weekly_conus_mosaic"
PIXEL_OVERSAMPLE = 2
RAMP = [
    (0.0, "#1f4e79"),
    (0.2, "#2a9d8f"),
    (0.4, "#e9c46a"),
    (0.6, "#f4a261"),
    (0.8, "#d1495b"),
    (1.0, "#6a0c0c"),
]
LAND_RGB = (191, 201, 203)
NODATA_RGB = (232, 236, 236)
ALPHA_INTERIOR = 235
ALPHA_TOUCHED = 120
THRESHOLD = 130
WINDOW_WEEKS = 104


def newest_table() -> Path:
    tables = sorted(DERIVED.glob("cyan_lake_table-*.parquet"))
    if not tables:
        raise SystemExit("no per-lake table under data/cyan/derived. Run build_lake_table.py")
    return tables[-1]


def newest_names() -> Path | None:
    files = sorted(NAMES_DIR.glob("lake-names-*.csv"))
    return files[-1] if files else None


def load_names(path: Path | None) -> dict[int, tuple[str, str, str | None]]:
    """COMID to (name, source, alternatives) from the crosswalk CSV. Empty without a file."""
    if path is None:
        return {}
    import pandas as pd

    df = pd.read_csv(path, dtype=str, keep_default_na=False)
    out = {}
    for r in df.itertuples():
        if r.name.strip():
            alt = getattr(r, "alternatives", "") or None
            out[int(r.comid)] = (r.name.strip(), r.name_source, alt)
    return out


def lake_states(lakes5070, states_path: Path) -> dict[int, str]:
    """State postal code per COMID by the centroid, nearest state when the centroid is outside."""
    import geopandas as gpd

    states = gpd.read_file(states_path)[["STUSPS", "geometry"]]
    pts = gpd.GeoDataFrame(
        {"COMID": lakes5070["COMID"].to_numpy()},
        geometry=lakes5070.geometry.centroid,
        crs=lakes5070.crs,
    ).to_crs(states.crs)
    inside = gpd.sjoin(pts, states, how="left", predicate="within")
    inside = inside[~inside.index.duplicated()]
    out = {
        int(c): (None if s != s else str(s))
        for c, s in zip(inside["COMID"], inside["STUSPS"], strict=True)
    }
    missing = [c for c, s in out.items() if s is None]
    if missing:
        rest = pts[pts["COMID"].isin(missing)].to_crs(lakes5070.crs)
        near = gpd.sjoin_nearest(rest, states.to_crs(lakes5070.crs), how="left")
        near = near[~near.index.duplicated()]
        for c, st in zip(near["COMID"], near["STUSPS"], strict=True):
            out[int(c)] = str(st)
    return out


def ramp_lut() -> np.ndarray:
    """RGB for codes 0 to 255: the ramp for 0 to 253, land grey, no data lighter grey."""
    lut = np.zeros((256, 3), np.uint8)
    stops = [(t, tuple(int(h[i : i + 2], 16) for i in (1, 3, 5))) for t, h in RAMP]
    for code in range(254):
        t = code / 253.0
        for (t0, c0), (t1, c1) in zip(stops[:-1], stops[1:], strict=True):
            if t <= t1:
                u = 0.0 if t1 == t0 else (t - t0) / (t1 - t0)
                lut[code] = [round(c0[i] + (c1[i] - c0[i]) * u) for i in range(3)]
                break
    lut[254] = LAND_RGB
    lut[255] = NODATA_RGB
    return lut


def pixel_overlay(codes: np.ndarray, interior: np.ndarray, touched: np.ndarray, window_transform):
    """Warp one lake window to Web Mercator and colour it.

    Returns the coloured PNG data URL, a grey PNG data URL whose value is the code, and the
    lat/lon bounds.
    """
    from PIL import Image
    from rasterio.transform import array_bounds
    from rasterio.warp import Resampling, calculate_default_transform, reproject, transform_bounds

    h, w = codes.shape
    bounds = array_bounds(h, w, window_transform)
    dst_transform, dw, dh = calculate_default_transform(
        "EPSG:5070", "EPSG:3857", w * PIXEL_OVERSAMPLE, h * PIXEL_OVERSAMPLE, *bounds
    )
    kwargs = {
        "src_transform": window_transform,
        "src_crs": "EPSG:5070",
        "dst_transform": dst_transform,
        "dst_crs": "EPSG:3857",
        "resampling": Resampling.nearest,
        "src_nodata": None,
        "dst_nodata": None,
        "init_dest_nodata": False,
    }
    out_codes = np.zeros((dh, dw), np.uint8)
    out_alpha = np.zeros((dh, dw), np.uint8)
    alpha_src = np.where(interior, ALPHA_INTERIOR, np.where(touched, ALPHA_TOUCHED, 0)).astype(
        np.uint8
    )
    reproject(codes, out_codes, **kwargs)
    reproject(alpha_src, out_alpha, **kwargs)
    rgb = ramp_lut()[out_codes]
    url = png_url(Image.fromarray(np.dstack([rgb, out_alpha]), mode="RGBA"))
    codes_url = png_url(Image.fromarray(out_codes, mode="L"))
    west, south, east, north = array_bounds(dh, dw, dst_transform)
    w4, s4, e4, n4 = transform_bounds("EPSG:3857", "EPSG:4326", west, south, east, north)
    return url, codes_url, [[round(s4, 5), round(w4, 5)], [round(n4, 5), round(e4, 5)]]


def png_url(img) -> str:
    import base64
    import io

    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode("ascii")


def newest_weekly_file() -> Path | None:
    files = sorted(WEEKLY_RAW.glob("*.tif"))
    return files[-1] if files else None


def run_length_at_end(flags: np.ndarray) -> int:
    """Consecutive True values at the end of a boolean series."""
    n = 0
    for v in flags[::-1]:
        if not v:
            break
        n += 1
    return n


def weeks_since_last(flags: np.ndarray) -> int | None:
    """Positions from the end to the last True value, 0 when the last value is True."""
    idx = np.flatnonzero(flags)
    return int(len(flags) - 1 - idx[-1]) if idx.size else None


def lake_series(df) -> dict:
    """Compact per-cadence series for one lake, arrays aligned on start dates."""
    out = {}
    for temporal in ("7D", "DAY"):
        sub = df[df["temporal"] == temporal].sort_values("start_date")
        if sub.empty:
            continue
        detect = sub["n_detect"] / sub["n_valid"].replace(0, np.nan)
        out[temporal] = {
            "start": sub["start_date"].tolist(),
            "end": sub["end_date"].tolist(),
            "median": [None if np.isnan(v) else round(float(v), 1) for v in sub["dn_median"]],
            "p90": [None if np.isnan(v) else round(float(v), 1) for v in sub["dn_p90"]],
            "max": [None if np.isnan(v) else int(v) for v in sub["dn_max"]],
            "valid_frac": [round(float(v), 3) for v in sub["valid_frac"]],
            "detect_frac": [None if np.isnan(v) else round(float(v), 3) for v in detect],
            "n_valid": sub["n_valid"].astype(int).tolist(),
        }
    return out


def recent_window(weekly, weeks: list[str]) -> dict:
    """Median and valid fraction on the shared list of recent week starts, null when absent."""
    by_start = {r.start_date: r for r in weekly.itertuples()}
    med, vf = [], []
    for w in weeks:
        r = by_start.get(w)
        if r is None or r.n_valid == 0:
            med.append(None)
            vf.append(0.0 if r is None else round(float(r.valid_frac), 3))
        else:
            med.append(round(float(r.dn_median), 1))
            vf.append(round(float(r.valid_frac), 3))
    return {"m": med, "v": vf}


def lake_state(weekly, threshold: int) -> dict:
    """The newest week's state and the run lengths used on the map."""
    w = weekly.sort_values("start_date")
    med = w["dn_median"].to_numpy()
    seen = w["n_valid"].to_numpy() > 0
    above = np.where(np.isnan(med), False, med >= threshold)
    last = w.iloc[-1]
    detect_frac = (last["n_detect"] / last["n_valid"]) if last["n_valid"] else None
    if last["n_valid"] == 0:
        cls = "no_data"
    elif last["dn_median"] >= threshold:
        cls = "above"
    elif last["n_detect"] > 0:
        cls = "detecting"
    else:
        cls = "below"
    year = w.tail(52)
    return {
        "week": [last["start_date"], last["end_date"]],
        "class": cls,
        "median": None if np.isnan(last["dn_median"]) else round(float(last["dn_median"]), 1),
        "max": None if np.isnan(last["dn_max"]) else int(last["dn_max"]),
        "valid_frac": round(float(last["valid_frac"]), 3),
        "detect_frac": None if detect_frac is None else round(float(detect_frac), 3),
        "run_above": run_length_at_end(above),
        "run_seen": run_length_at_end(seen),
        "weeks_since_seen": weeks_since_last(seen),
        "seen_share_52": round(float((year["n_valid"] > 0).mean()), 3),
        "above_weeks_52": int(
            np.where(np.isnan(year["dn_median"]), False, year["dn_median"] >= threshold).sum()
        ),
        "peak_median": None if np.all(np.isnan(med)) else round(float(np.nanmax(med)), 1),
    }


def build(args) -> dict:
    import geopandas as gpd
    import pandas as pd
    import rasterio

    table = Path(args.table) if args.table else newest_table()
    df = pd.read_parquet(table)
    lakes = gpd.read_file(f"zip://{args.lakes}")
    lakes["COMID"] = lakes["COMID"].astype("int64")
    with rasterio.open(args.grid_file) as ds:
        lakes5070 = lakes.to_crs(ds.crs)
        transform, width, height = ds.transform, ds.width, ds.height
    masks = lt.lake_masks(
        lakes5070,
        transform,
        width,
        height,
        lt.RECIPE["oversample"],
        lt.RECIPE["interior_min_coverage"],
    )
    cent = lakes5070.geometry.centroid.to_crs(4326)
    bounds = lakes5070.geometry.bounds
    wgs = lakes5070.geometry.to_crs(4326)

    names_path = Path(args.names) if args.names else newest_names()
    names = load_names(names_path)
    states = lake_states(lakes5070, Path(args.states)) if args.states else {}
    out = Path(args.out)
    (out / "data" / "lakes").mkdir(parents=True, exist_ok=True)
    chosen = args.newest_file or newest_weekly_file()
    pixel_file = None if (args.no_pixels or not chosen) else Path(chosen)
    pixel_info = None
    if pixel_file:
        (out / "data" / "pixels").mkdir(parents=True, exist_ok=True)
        with rasterio.open(pixel_file) as ds:
            newest_codes = ds.read(1)
        parsed = c.parse_cyan_filename(pixel_file.name)
        pixel_info = {
            "file": pixel_file.name,
            "start": parsed.start_date,
            "end": parsed.end_date,
            "n_files": 0,
            "bytes": 0,
        }
    threshold = args.threshold
    records, attr_rows = [], []
    weeks = sorted(df.loc[df["temporal"] == "7D", "start_date"].unique().tolist())
    recent = weeks[-WINDOW_WEEKS:]
    by_lake = {k: g for k, g in df.groupby("comid")}
    for i, row in enumerate(lakes.itertuples(), 1):
        comid = int(row.COMID)
        g = by_lake.get(comid)
        if g is None:
            continue
        weekly = g[g["temporal"] == "7D"]
        state = lake_state(weekly, threshold) if not weekly.empty else None
        m = masks[comid]
        shp_name = None if pd.isna(row.GNIS_NAME) else str(row.GNIS_NAME)
        alternatives = None
        if shp_name:
            name, source = shp_name, "shapefile"
        elif comid in names:
            name, source, alternatives = names[comid]
        else:
            name, source = None, "none"
        rec = {
            "c": comid,
            "n": name,
            "ns": source,
            "na": alternatives,
            "st": states.get(comid),
            "a": round(float(row.AREASQKM), 2),
            "y": round(float(cent.iloc[i - 1].y), 4),
            "x": round(float(cent.iloc[i - 1].x), 4),
            "ni": int(m["interior"].size),
            "nt": int(m["touched"].size),
            "s": state,
            **recent_window(weekly, recent),
        }
        records.append(rec)
        series = lake_series(g)
        (out / "data" / "lakes" / f"{comid}.js").write_text(
            f"CYAN_LAKE({comid}, {json.dumps(series, separators=(',', ':'))});\n", encoding="utf-8"
        )
        if pixel_info and m["window"]:
            col0, row0, ww, hh = m["window"]
            win = newest_codes[row0 : row0 + hh, col0 : col0 + ww]
            interior = np.zeros(win.shape, bool)
            touched = np.zeros(win.shape, bool)
            ri, ci = np.divmod(m["interior"], width)
            rt, ct = np.divmod(m["touched"], width)
            interior[ri - row0, ci - col0] = True
            touched[rt - row0, ct - col0] = True
            from rasterio.windows import Window
            from rasterio.windows import transform as win_transform

            wtr = win_transform(Window(col0, row0, ww, hh), transform)
            url, codes_url, pbounds = pixel_overlay(win, interior, touched, wtr)
            geo = json.dumps(wgs.iloc[i - 1].__geo_interface__)
            outline = json.loads(re.sub(r"(\d+\.\d{6})\d+", r"\1", geo))
            body = json.dumps(
                {"bounds": pbounds, "png": url, "codes": codes_url, "outline": outline},
                separators=(",", ":"),
            )
            ptext = f"CYAN_PIXELS({comid}, {body});\n"
            (out / "data" / "pixels" / f"{comid}.js").write_text(ptext, encoding="utf-8")
            pixel_info["n_files"] += 1
            pixel_info["bytes"] += len(ptext)
        b = bounds.iloc[i - 1]
        attr_rows.append(
            {
                "comid": comid,
                "gnis_name": shp_name,
                "name": name,
                "name_source": source,
                "name_alternatives": alternatives,
                "state": states.get(comid),
                "area_sqkm": rec["a"],
                "centroid_lat": rec["y"],
                "centroid_lon": rec["x"],
                "minx_5070": float(b.minx),
                "miny_5070": float(b.miny),
                "maxx_5070": float(b.maxx),
                "maxy_5070": float(b.maxy),
                "window_col": m["window"][0] if m["window"] else None,
                "window_row": m["window"][1] if m["window"] else None,
                "window_width": m["window"][2] if m["window"] else None,
                "window_height": m["window"][3] if m["window"] else None,
                "n_interior": rec["ni"],
                "n_touched": rec["nt"],
                "interior_cells": m["interior"].tolist(),
            }
        )
        if i % 500 == 0:
            print(f"  [{i}/{len(lakes)}]")

    started = net.utc_now_iso()
    stamp = started.replace(":", "")[:15] + "Z"
    attrs = pd.DataFrame(attr_rows)
    attr_path = DERIVED / f"cyan_lake_attributes-{stamp}.parquet"
    attrs.to_parquet(attr_path, index=False)

    classes = {}
    name_sources = {}
    for r in records:
        if r["s"]:
            classes[r["s"]["class"]] = classes.get(r["s"]["class"], 0) + 1
        name_sources[r["ns"]] = name_sources.get(r["ns"], 0) + 1
    summary = {
        "measured_at": started,
        "built_at": started,
        "table": provenance.rel(table),
        "table_sha256": net.sha256_file(table),
        "attributes": provenance.rel(attr_path),
        "recipe": lt.RECIPE,
        "threshold": threshold,
        "threshold_source": (
            "EPA INLA_CONUS_forecast deposit, cyan_processing_conus.R line 170, "
            "DOI 10.23719/1529140"
        ),
        "outlines": "exact polygons in WGS84 to 6 decimals, one per pixel file",
        "weeks": weeks,
        "recent_weeks": recent,
        "newest_week": weeks[-1] if weeks else None,
        "n_lakes": len(records),
        "classes_newest_week": classes,
        "names": provenance.rel(names_path) if names_path else None,
        "name_sources": name_sources,
        "states": provenance.rel(Path(args.states)) if args.states else None,
        "pixels": pixel_info,
        "encoding": {
            "threshold_note": "median code 130 is the EPA code's 12 ug/L chlorophyll-a equivalent"
        },
        "code": provenance.code_provenance(
            [Path(__file__), Path(lt.__file__), Path(c.__file__)],
            [table, Path(args.lakes)] + ([names_path] if names_path else []),
        ),
    }
    payload = {**summary, "lakes": records}
    (out / "data" / "lakes.js").write_text(
        "window.CYAN_LAKES = " + json.dumps(payload, separators=(",", ":")) + ";\n",
        encoding="utf-8",
    )
    (REPO / "datasets" / "cyan" / "outputs" / f"lake-dashboard-{stamp}.json").write_text(
        json.dumps(summary, indent=1), encoding="utf-8"
    )
    print(f"[lake-dashboard] {len(records)} lakes, newest week {weeks[-1]}, classes {classes}")
    print(f"[lake-dashboard] wrote lakes.js and {len(records)} series files")
    print(f"[lake-dashboard] attributes {attr_path.name}")
    return summary


def parse_args(argv=None):
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--table", default=None, help="per-lake table, default the newest")
    ap.add_argument("--lakes", default=str(LAKES_ZIP))
    ap.add_argument("--grid-file", default=None, help="any pulled mosaic, for the grid")
    ap.add_argument("--out", default=str(OUT))
    ap.add_argument("--threshold", type=int, default=THRESHOLD)
    ap.add_argument("--names", default=None, help="name crosswalk CSV, default the newest")
    ap.add_argument("--states", default=str(STATES), help="state outlines GeoJSON, '' for none")
    ap.add_argument("--newest-file", default=None, help="weekly file for the pixel overlays")
    ap.add_argument("--no-pixels", action="store_true", help="skip the pixel overlays")
    args = ap.parse_args(argv)
    if not args.grid_file:
        first = sorted((REPO / "data" / "cyan" / "raw" / "weekly_conus_mosaic").glob("*.tif"))
        args.grid_file = str(first[0]) if first else None
    return args


def main(argv=None) -> int:
    build(parse_args(argv))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
