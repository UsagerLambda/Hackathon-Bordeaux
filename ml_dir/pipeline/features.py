"""
features.py — Étape 1 : Feature engineering sur la grille 250m × 250m.

Lecture  : ../data/
Écriture : ml_pipeline/features.geojson

Usage autonome : python pipeline/features.py
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import time
import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import box
from config import config


# ── Helpers ───────────────────────────────────────────────────────────────────

def sjoin_flag(grid, path, crs_override=None):
    """Présence / absence d'une couche polygone dans chaque cellule → 0/1."""
    layer = gpd.read_file(path)
    if crs_override:
        layer = layer.set_crs(crs_override, allow_override=True)
    layer = layer.to_crs(config.CRS_LAMBERT93)
    joined = gpd.sjoin(grid[["cell_id", "geometry"]], layer[["geometry"]],
                       how="left", predicate="intersects")
    present = joined.groupby("cell_id")["index_right"].any().astype(int)
    return grid["cell_id"].map(present).fillna(0).astype(int)


def sjoin_flag_multi(grid, paths):
    """Fusionne plusieurs shapefiles puis spatial join → 0/1."""
    parts = [gpd.read_file(p).to_crs(config.CRS_LAMBERT93) for p in paths]
    layer = gpd.GeoDataFrame(pd.concat(parts, ignore_index=True), crs=config.CRS_LAMBERT93)
    joined = gpd.sjoin(grid[["cell_id", "geometry"]], layer[["geometry"]],
                       how="left", predicate="intersects")
    present = joined.groupby("cell_id")["index_right"].any().astype(int)
    return grid["cell_id"].map(present).fillna(0).astype(int)


def sjoin_max(grid, path, col, crs_override=None):
    """Valeur max d'un attribut d'une couche polygone par cellule."""
    layer = gpd.read_file(path)
    if crs_override:
        layer = layer.set_crs(crs_override, allow_override=True)
    layer = layer.to_crs(config.CRS_LAMBERT93)
    joined = gpd.sjoin(grid[["cell_id", "geometry"]], layer[["geometry", col]],
                       how="left", predicate="intersects")
    maxvals = joined.groupby("cell_id")[col].max()
    return grid["cell_id"].map(maxvals).fillna(0)


def dist_nearest(grid, path, crs_override=None):
    """Distance en mètres du centroïde de chaque cellule au point le plus proche."""
    pts = gpd.read_file(path)
    if crs_override:
        pts = pts.set_crs(crs_override, allow_override=True)
    pts = pts.to_crs(config.CRS_LAMBERT93)
    pts_union = pts.geometry.union_all()
    centroids = grid.geometry.centroid
    return centroids.apply(lambda c: c.distance(pts_union))


# ── Pipeline ──────────────────────────────────────────────────────────────────

def run_features() -> gpd.GeoDataFrame:
    DATA = config.DATA_DIR
    PPRI = DATA / "ppri"

    # ── 1. Grille ─────────────────────────────────────────────────────────────
    print("  → Chargement des communes...")
    communes = gpd.read_file(DATA / "fv_commu_s.geojson")
    metropole_m = communes.dissolve().to_crs(config.CRS_LAMBERT93)
    bounds = metropole_m.total_bounds
    metro_poly = metropole_m.geometry.iloc[0]

    t0 = time.time()
    x_coords = np.arange(bounds[0], bounds[2], config.CELL_SIZE)
    y_coords = np.arange(bounds[1], bounds[3], config.CELL_SIZE)

    cells, cell_ids = [], []
    for i, x in enumerate(x_coords):
        for j, y in enumerate(y_coords):
            cells.append(box(x, y, x + config.CELL_SIZE, y + config.CELL_SIZE))
            cell_ids.append(f"cell_{i}_{j}")

    grid = gpd.GeoDataFrame({"cell_id": cell_ids}, geometry=cells, crs=config.CRS_LAMBERT93)
    grid = grid[grid.geometry.intersects(metro_poly)].copy().reset_index(drop=True)
    grid["centroid_x"] = grid.geometry.centroid.x
    grid["centroid_y"] = grid.geometry.centroid.y
    print(f"  → {len(grid)} cellules ({time.time() - t0:.1f}s)")

    # ── 2. Inondations ────────────────────────────────────────────────────────
    print("  → Inondations (PPRI TRI 2020)...")
    grid["_flood_fort"] = sjoin_flag_multi(grid, PPRI.glob("*inondable_*_01for_*.shp"))
    grid["_flood_moy"]  = sjoin_flag_multi(grid, PPRI.glob("*inondable_*_02moy_*.shp"))
    grid["_flood_mcc"]  = sjoin_flag_multi(grid, PPRI.glob("*inondable_*_03mcc_*.shp"))
    grid["_flood_fai"]  = sjoin_flag_multi(grid, PPRI.glob("*inondable_*_04fai_*.shp"))
    grid["flood_score"] = (
        grid["_flood_fort"] * 4 +
        (grid["_flood_moy"] - grid["_flood_fort"]) * 3 +
        (grid["_flood_mcc"] - grid["_flood_moy"])  * 2 +
        (grid["_flood_fai"] - grid["_flood_mcc"])  * 1
    ).clip(0, 4)
    grid.drop(columns=["_flood_fort", "_flood_moy", "_flood_mcc", "_flood_fai"], inplace=True)

    # ── 3. Remontée de nappes ─────────────────────────────────────────────────
    print("  → Remontée de nappes...")
    grid["nappe"] = sjoin_max(grid, DATA / "ppri_remonte" / "Re_Nappe_fr.shp", "gridcode")

    # ── 4. Argile ─────────────────────────────────────────────────────────────
    print("  → Aléa argile...")
    argile = gpd.read_file(DATA / "ri_alearga_s.geojson").to_crs(config.CRS_LAMBERT93)
    argile["_val"] = argile["alea"].map({"MOYEN": 2, "FORT": 3}).fillna(0)
    joined = gpd.sjoin(grid[["cell_id", "geometry"]], argile[["geometry", "_val"]],
                       how="left", predicate="intersects")
    grid["argile"] = grid["cell_id"].map(joined.groupby("cell_id")["_val"].max()).fillna(0)

    # ── 5. ICU ────────────────────────────────────────────────────────────────
    print("  → Îlots de chaleur (ICU)...")
    grid["icu"] = sjoin_max(grid, DATA / "ri_icu_ifu_s.geojson", "delta")

    # ── 6. PPRT ───────────────────────────────────────────────────────────────
    print("  → Zones PPRT...")
    grid["in_pprt"] = sjoin_flag(grid, DATA / "ri_pprt_s.geojson")

    # ── 7. Couverture végétale ────────────────────────────────────────────────
    print("  → Couverture végétale...")
    gs   = gpd.read_file(DATA / "ec_inv_protection_s.geojson").to_crs(config.CRS_LAMBERT93)
    bois = gpd.read_file(DATA / "to_bois_s.geojson").to_crs(config.CRS_LAMBERT93)
    green_layer = gpd.GeoDataFrame(pd.concat([gs, bois], ignore_index=True), crs=config.CRS_LAMBERT93)
    joined_green = gpd.sjoin(grid[["cell_id", "geometry"]], green_layer[["geometry"]],
                             how="left", predicate="intersects")
    grid["green_cover"] = grid["cell_id"].map(
        joined_green.groupby("cell_id")["index_right"].any().astype(int)
    ).fillna(0).astype(int)

    # ── 8. Zones humides ──────────────────────────────────────────────────────
    print("  → Zones humides...")
    grid["zone_humide"] = sjoin_flag(grid, DATA / "ec_zone_humide_s.geojson")

    # ── 9. Infiltration d'eau ─────────────────────────────────────────────────
    print("  → Capacité d'infiltration...")
    grid["water_infiltration"] = sjoin_max(grid, DATA / "en_infiltration_s.geojson", "note_finale")

    # ── 10. Distance industries / sites pollués ───────────────────────────────
    print("  → Distance industries et sites pollués...")
    grid["dist_industrie"] = dist_nearest(grid, DATA / "ri_etab_pol_p.geojson")
    grid["dist_sites_pol"] = dist_nearest(grid, DATA / "ri_basol_p.geojson")

    # ── 11. Population ────────────────────────────────────────────────────────
    print("  → Population (carroyage 200m)...")
    pop = gpd.read_file(
        DATA / "population-bordeaux-metropole-donnees-carroyees-a-200-metres-millesime-2015.geojson"
    ).to_crs(config.CRS_LAMBERT93)
    joined_pop = gpd.sjoin(grid[["cell_id", "geometry"]], pop[["ind", "geometry"]],
                           how="left", predicate="intersects")
    grid["population"] = grid["cell_id"].map(
        joined_pop.groupby("cell_id")["ind"].sum()
    ).fillna(0)

    # ── Sauvegarde ────────────────────────────────────────────────────────────
    output = config.OUTPUT_DIR / "features.geojson"
    grid.to_file(output, driver="GeoJSON")
    print(f"  ✓ {len(grid)} cellules × {len(grid.columns) - 3} features → {output}")
    return grid


if __name__ == "__main__":
    print("\n── Étape 1 : Feature engineering ───────────────────────────────────")
    run_features()
