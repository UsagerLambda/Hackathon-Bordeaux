from pathlib import Path

class Config:
    # ── Chemins ───────────────────────────────────────────────────────────────
    DATA_DIR   = Path("./data")
    OUTPUT_DIR = Path("./ml_pipeline")

    # ── Grille ────────────────────────────────────────────────────────────────
    CELL_SIZE = 250  # mètres (Lambert93)

    # ── CRS ───────────────────────────────────────────────────────────────────
    CRS_WGS84     = "EPSG:4326"
    CRS_LAMBERT93 = "EPSG:2154"

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
