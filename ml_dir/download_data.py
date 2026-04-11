"""
download_data.py – Télécharge toutes les sources nécessaires au pipeline ML.
À lancer depuis ml_dir/ : python download_data.py

Les données sont placées dans ../data/ (racine du repo).
Les fichiers déjà présents sont ignorés.
"""

import io
import sys
import zipfile
from pathlib import Path
import urllib.request

DATA_DIR = Path(__file__).parent.parent / "data"

# ── Helpers ──────────────────────────────────────────────────────────────────

def _progress(label: str, downloaded: int, total) -> None:
    """Affiche une barre de progression sur la même ligne."""
    dl_mb = downloaded / 1_000_000
    if total:
        pct = downloaded / total * 100
        total_mb = total / 1_000_000
        bar = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
        line = f"  ↓ {label}  [{bar}] {pct:5.1f}%  {dl_mb:.1f}/{total_mb:.1f} MB"
    else:
        line = f"  ↓ {label}  {dl_mb:.1f} MB téléchargés..."
    print(f"\r{line}", end="", flush=True)


def _fetch(url: str, label: str) -> bytes:
    """Télécharge url avec barre de progression, retourne les octets."""
    CHUNK = 64 * 1024
    with urllib.request.urlopen(url) as resp:
        total = int(resp.headers.get("Content-Length", 0)) or None
        chunks, downloaded = [], 0
        while True:
            chunk = resp.read(CHUNK)
            if not chunk:
                break
            chunks.append(chunk)
            downloaded += len(chunk)
            _progress(label, downloaded, total)
    print()  # saut de ligne après la barre
    return b"".join(chunks)


def download(url: str, dest: Path) -> None:
    """Télécharge url → dest. Skip si déjà présent."""
    if dest.exists():
        print(f"  ✓ {dest.name}")
        return
    dest.parent.mkdir(parents=True, exist_ok=True)
    data = _fetch(url, dest.name)
    dest.write_bytes(data)


def download_zip(url: str, extract_to: Path, keep, flatten: bool = False, strip_components: int = 0) -> None:
    """
    Télécharge un zip en mémoire et extrait les entrées filtrées par keep(name).
    flatten=True        : extrait tous les fichiers directement dans extract_to/ (ignore les sous-dossiers).
    strip_components=N  : supprime les N premiers niveaux de dossier du chemin zip avant extraction.
    """
    data = _fetch(url, url.split("/")[-1])

    extract_to.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(io.BytesIO(data)) as zf:
        entries = [e for e in zf.namelist() if keep(e) and not e.endswith("/")]
        print(f"     → {len(entries)} fichiers extraits vers {extract_to.name}/")
        for entry in entries:
            if flatten:
                rel = Path(entry).name
            elif strip_components:
                parts = Path(entry).parts[strip_components:]
                rel = Path(*parts) if parts else Path(entry).name
            else:
                rel = entry
            target = extract_to / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            if not target.exists():
                target.write_bytes(zf.read(entry))


# ── Sources GeoJSON directes ─────────────────────────────────────────────────

GEOJSON_SOURCES = {
    "fv_commu_s.geojson":
        "https://datahub.bordeaux-metropole.fr/api/explore/v2.1/catalog/datasets/fv_commu_s/exports/geojson?lang=fr&timezone=Europe%2FBerlin",
    "ri_pprt_s.geojson":
        "https://datahub.bordeaux-metropole.fr/api/explore/v2.1/catalog/datasets/ri_pprt_s/exports/geojson?lang=fr&timezone=Europe%2FBerlin",
    "ri_icu_ifu_s.geojson":
        "https://datahub.bordeaux-metropole.fr/api/explore/v2.1/catalog/datasets/ri_icu_ifu_s/exports/geojson?lang=fr&timezone=Europe%2FBerlin",
    "ri_basol_p.geojson":
        "https://datahub.bordeaux-metropole.fr/api/explore/v2.1/catalog/datasets/ri_basol_p/exports/geojson?lang=fr&timezone=Europe%2FBerlin",
    "ri_etab_pol_p.geojson":
        "https://datahub.bordeaux-metropole.fr/api/explore/v2.1/catalog/datasets/ri_etab_pol_p/exports/geojson?lang=fr&timezone=Europe%2FBerlin",
    "ri_alearga_s.geojson":
        "https://datahub.bordeaux-metropole.fr/api/explore/v2.1/catalog/datasets/ri_alearga_s/exports/geojson?lang=fr&timezone=Europe%2FBerlin",
    "ec_inv_protection_s.geojson":
        "https://datahub.bordeaux-metropole.fr/api/explore/v2.1/catalog/datasets/ec_inv_protection_s/exports/geojson?lang=fr&timezone=Europe%2FBerlin",
    "to_bois_s.geojson":
        "https://datahub.bordeaux-metropole.fr/api/explore/v2.1/catalog/datasets/to_bois_s/exports/geojson?lang=fr&timezone=Europe%2FBerlin",
    "ec_zone_humide_s.geojson":
        "https://datahub.bordeaux-metropole.fr/api/explore/v2.1/catalog/datasets/ec_zone_humide_s/exports/geojson?lang=fr&timezone=Europe%2FBerlin",
    "en_infiltration_s.geojson":
        "https://datahub.bordeaux-metropole.fr/api/explore/v2.1/catalog/datasets/en_infiltration_s/exports/geojson?lang=fr&timezone=Europe%2FBerlin",
    "population-bordeaux-metropole-donnees-carroyees-a-200-metres-millesime-2015.geojson":
        "https://datahub.bordeaux-metropole.fr/api/explore/v2.1/catalog/datasets/population-bordeaux-metropole-donnees-carroyees-a-200-metres-millesime-2015/exports/geojson?lang=fr&timezone=Europe%2FBerlin",
}

# ── Sources ZIP ───────────────────────────────────────────────────────────────

# TRI 2020 : seuls les fichiers d'aléa inondation (*inondable_*) sont utilisés
# par le pipeline. Les communes, enjeux, ouvrages, etc. sont ignorés.
# Structure extraite : data/ppri/n_tri_bord_inondable_*.shp
TRI_URL = "https://files.georisques.fr/di_2020/tri_2020_sig_di_33.zip"

# Remontée de nappes : seul Re_Nappe_fr.* est utilisé.
# Structure extraite : data/ppri_remonte/Re_Nappe_fr.*
NAPPES_URL = "https://files.georisques.fr/REMNAPPES/Dept_33.zip"


if __name__ == "__main__":
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    print("\n── GeoJSON (Bordeaux Métropole Open Data) ───────────────────────────")
    for filename, url in GEOJSON_SOURCES.items():
        download(url, DATA_DIR / filename)

    print("\n── Zonages inondation TRI 2020 (Géorisques) ────────────────────────")
    download_zip(
        TRI_URL,
        extract_to=DATA_DIR / "ppri",
        keep=lambda n: "inondable_" in n,
        flatten=True,  # extrait directement dans data/ppri/
    )

    print("\n── Remontée de nappes Dept 33 (Géorisques) ─────────────────────────")
    download_zip(
        NAPPES_URL,
        extract_to=DATA_DIR / "ppri_remonte",
        keep=lambda n: "Re_Nappe_fr" in n and Path(n).suffix in {".shp", ".dbf", ".prj", ".cpg", ".shx"},
        flatten=True,  # extrait directement dans data/ppri_remonte/
    )

    print(f"\n✅ Données prêtes dans {DATA_DIR.resolve()}")
