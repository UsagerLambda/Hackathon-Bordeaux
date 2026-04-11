"""
kmeans.py — Étape 2 : Clustering KMeans des cellules.

Lecture  : ml_pipeline/features.geojson
Écriture : ml_pipeline/kmeans_clusters.geojson

Usage autonome : python pipeline/kmeans.py
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import geopandas as gpd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler
from config import config

FEATURES = [
    "flood_score", "nappe", "argile", "icu", "in_pprt",
    "green_cover", "zone_humide", "water_infiltration",
    "dist_industrie", "dist_sites_pol", "population",
]

# ── Labels des clusters ───────────────────────────────────────────────────────
# À mettre à jour manuellement après chaque re-clustering :
# relancer avec N_CLUSTERS=0, observer les profils, puis renseigner ici.
CLUSTER_LABELS = {
    0: "Zone humide / berges quasi-inhabitées",
    1: "Zone périurbaine argileuse dense",
    2: "Quartier dense inondable et chaud",
    3: "Zone urbaine périphérique chaude",
    4: "Zone inondable végétalisée",
    5: "Zone naturelle / agricole",
    6: "Cœur urbain chaud et dense",
    7: "Zone résidentielle verte périurbaine",
    8: "Zone industrielle pavillonnaire",
}


def _find_k(X_scaled: np.ndarray) -> int:
    """Sélectionne k optimal par score silhouette sur k ∈ [2, 10]."""
    print("  → Recherche du k optimal (silhouette)...")
    silhouettes = []
    K = range(2, 11)
    for k in K:
        km = KMeans(n_clusters=k, random_state=config.KMEANS_RANDOM_STATE,
                    n_init=config.KMEANS_N_INIT)
        km.fit(X_scaled)
        silhouettes.append(silhouette_score(X_scaled, km.labels_))
    best_k = list(K)[silhouettes.index(max(silhouettes))]
    print(f"  → k optimal : {best_k} (silhouette={max(silhouettes):.3f})")
    return best_k


def run_kmeans() -> gpd.GeoDataFrame:
    input_path = config.OUTPUT_DIR / "features.geojson"
    if not input_path.exists():
        raise FileNotFoundError(f"features.geojson introuvable : {input_path}\nLancer d'abord pipeline/features.py")

    print(f"  → Chargement de {input_path.name}...")
    gdf = gpd.read_file(input_path)

    X = gdf[FEATURES].copy()
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # ── Choix de k ────────────────────────────────────────────────────────────
    k = config.N_CLUSTERS if config.N_CLUSTERS > 0 else _find_k(X_scaled)

    # ── KMeans ────────────────────────────────────────────────────────────────
    print(f"  → KMeans k={k}...")
    kmeans_model = KMeans(n_clusters=k, random_state=config.KMEANS_RANDOM_STATE,
                          n_init=config.KMEANS_N_INIT)
    kmeans_model.fit(X_scaled)

    gdf["cluster"] = kmeans_model.labels_
    gdf["cluster_label"] = gdf["cluster"].map(CLUSTER_LABELS).fillna(
        gdf["cluster"].apply(lambda c: f"Cluster {c}")
    )

    # ── Sauvegarde ────────────────────────────────────────────────────────────
    output = config.OUTPUT_DIR / "kmeans_clusters.geojson"
    gdf.to_crs(config.CRS_WGS84).to_file(output, driver="GeoJSON")
    print(f"  ✓ {len(gdf)} cellules, {k} clusters → {output}")
    return gdf


if __name__ == "__main__":
    print("\n── Étape 2 : Clustering KMeans ──────────────────────────────────────")
    run_kmeans()
