"""
main.py – Point d'entrée de l'API FastAPI Résili-Score.
Monte les routers, configure CORS, et charge les données au démarrage.
"""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.data_loader import load_data
from src.api.scoring import compute_scores
from src.api.routes import cell, address, map


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan : charge les données et calcule les scores au démarrage.
    """
    # ── Startup ──────────────────────────────────────────────────────────
    print("🚀 Démarrage de l'API Résili-Score...")
    gdf = load_data()
    compute_scores(gdf)

    # Charger les données industrielles
    from src.api.industries_loader import load_industries
    load_industries()

    print("🟢 API prête !")

    yield

    # ── Shutdown ─────────────────────────────────────────────────────────
    print("🔴 Arrêt de l'API Résili-Score.")


# ── Application FastAPI ──────────────────────────────────────────────────────

app = FastAPI(
    title="Résili-Score API",
    description=(
        "API du projet Résili-Score – Hackathon Bordeaux Métropole.\n"
        "Attribue un score de résilience A à E à chaque zone géographique."
    ),
    version="0.1.0",
    lifespan=lifespan,
)

# ── CORS ─────────────────────────────────────────────────────────────────────
# Définir ALLOWED_ORIGINS en variable d'environnement pour restreindre en prod.
# Exemple : ALLOWED_ORIGINS="https://mondomaine.fr,https://www.mondomaine.fr"
# Par défaut : ouvert (*) pour le développement local.

_origins_env = os.getenv("ALLOWED_ORIGINS", "")
ALLOWED_ORIGINS = _origins_env.split(",") if _origins_env else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Montage des routers ─────────────────────────────────────────────────────

app.include_router(cell.router, prefix="/api")
app.include_router(address.router, prefix="/api")
app.include_router(map.router, prefix="/api")


# ── Route santé ──────────────────────────────────────────────────────────────

@app.get("/", tags=["Santé"])
def health():
    """Health check."""
    return {"status": "ok", "project": "Résili-Score"}
