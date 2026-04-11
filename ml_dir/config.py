from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv(Path(__file__).parent / ".env")

class Config:
    # ── Chemins absolus ───────────────────────────────────────────────────────
    ROOT_DIR   = Path(__file__).parent
    DATA_DIR   = ROOT_DIR.parent / "data"
    OUTPUT_DIR = ROOT_DIR / "ml_pipeline"
    SCORES_DIR = ROOT_DIR.parent / "scores"

    # ── CRS ───────────────────────────────────────────────────────────────────
    CRS_WGS84     = "EPSG:4326"
    CRS_LAMBERT93 = "EPSG:2154"

    # ── Grille ────────────────────────────────────────────────────────────────
    CELL_SIZE = int(os.getenv("CELL_SIZE", 250))

    # ── KMeans ────────────────────────────────────────────────────────────────
    N_CLUSTERS          = int(os.getenv("N_CLUSTERS", 0))   # 0 = auto (silhouette)
    KMEANS_RANDOM_STATE = int(os.getenv("KMEANS_RANDOM_STATE", 42))
    KMEANS_N_INIT       = int(os.getenv("KMEANS_N_INIT", 10))

    # ── SHAP ──────────────────────────────────────────────────────────────────
    SHAP_TOP_N = int(os.getenv("SHAP_TOP_N", 3))

    # ── Poids scoring — particulier ───────────────────────────────────────────
    WEIGHTS_PARTICULIER = {
        "flood_score":        float(os.getenv("W_PART_FLOOD",              0.25)),
        "icu":                float(os.getenv("W_PART_ICU",                0.13)),
        "nappe":              float(os.getenv("W_PART_NAPPE",              0.12)),
        "argile":             float(os.getenv("W_PART_ARGILE",             0.10)),
        "zone_humide":        float(os.getenv("W_PART_ZONE_HUMIDE",        0.08)),
        "in_pprt":            float(os.getenv("W_PART_IN_PPRT",            0.08)),
        "dist_sites_pol":     float(os.getenv("W_PART_DIST_SITES_POL",     0.08)),
        "dist_industrie":     float(os.getenv("W_PART_DIST_INDUSTRIE",     0.06)),
        "water_infiltration": float(os.getenv("W_PART_WATER_INFILTRATION", 0.05)),
        "green_cover":        float(os.getenv("W_PART_GREEN_COVER",        0.05)),
    }

    # ── Poids scoring — élu ───────────────────────────────────────────────────
    WEIGHTS_ELU = {
        "flood_score":        float(os.getenv("W_ELU_FLOOD",              0.20)),
        "population":         float(os.getenv("W_ELU_POPULATION",         0.18)),
        "icu":                float(os.getenv("W_ELU_ICU",                0.11)),
        "nappe":              float(os.getenv("W_ELU_NAPPE",              0.10)),
        "zone_humide":        float(os.getenv("W_ELU_ZONE_HUMIDE",        0.08)),
        "argile":             float(os.getenv("W_ELU_ARGILE",             0.08)),
        "in_pprt":            float(os.getenv("W_ELU_IN_PPRT",            0.07)),
        "dist_sites_pol":     float(os.getenv("W_ELU_DIST_SITES_POL",     0.07)),
        "dist_industrie":     float(os.getenv("W_ELU_DIST_INDUSTRIE",     0.05)),
        "water_infiltration": float(os.getenv("W_ELU_WATER_INFILTRATION", 0.04)),
        "green_cover":        float(os.getenv("W_ELU_GREEN_COVER",        0.02)),
    }

    # ── Codes INSEE des 28 communes de Bordeaux Métropole ─────────────────────
    COMMUNES_BM = {
        "33003": "Ambarès-et-Lagrave", "33004": "Ambès",
        "33013": "Bassens",            "33032": "Bègles",
        "33039": "Blanquefort",        "33063": "Bordeaux",
        "33065": "Bouliac",            "33069": "Le Bouscat",
        "33075": "Bruges",             "33096": "Carbon-Blanc",
        "33119": "Cenon",              "33162": "Eysines",
        "33167": "Floirac",            "33185": "Gradignan",
        "33192": "Le Haillan",         "33249": "Lormont",
        "33273": "Martignas-sur-Jalle","33281": "Mérignac",
        "33312": "Parempuyre",         "33318": "Pessac",
        "33376": "Saint-Aubin-de-Médoc","33434": "Saint-Louis-de-Montferrand",
        "33449": "Saint-Médard-en-Jalles","33487": "Saint-Vincent-de-Paul",
        "33519": "Le Taillan-Médoc",   "33522": "Talence",
        "33550": "Villenave-d'Ornon",
    }


config = Config()
config.OUTPUT_DIR.mkdir(exist_ok=True)
config.SCORES_DIR.mkdir(exist_ok=True)
