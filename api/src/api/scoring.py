"""
scoring.py – Calcul du score composite de résilience A-E.

Logique :
  1. Normalise chaque feature avec MinMaxScaler (0-1)
  2. Combine en un score composite :
     - Risques (mauvais si élevé) : flood_score, nappe, argile, icu, in_pprt
     - Capacités (bon si élevé) : dist_industrie, dist_sites_pol
     - Résilience (bon si élevé) : green_spaces, water_infiltration
  3. Discrétise en quintiles → lettres A (meilleur) à E (pire)
"""

from typing import List

import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler

# ── Colonnes utilisées pour le scoring ──────────────────────────────────────

# Features « risque » : plus c'est haut, plus c'est mauvais
RISK_COLS = ["flood_score", "nappe", "argile", "icu_transformed", "in_pprt", "zone_humide"]

# Features « capacité » : plus c'est loin, mieux c'est (on les inversera)
CAPACITY_COLS = ["dist_industrie", "dist_sites_pol"]

# Features « résilience » : plus c'est haut, mieux c'est (on les inversera)
RESILIENCE_COLS = ["green_cover", "water_infiltration"]

# Poids relatifs par catégorie (ajustables)
WEIGHT_RISK = 0.50
WEIGHT_CAPACITY = 0.25
WEIGHT_RESILIENCE = 0.25

# Labels de score
SCORE_LABELS = ["A", "B", "C", "D", "E"]


def compute_scores(gdf) -> None:
    """
    Calcule le score composite pour chaque cellule et l'ajoute
    directement dans le GeoDataFrame (colonnes 'score_value' et 'score').
    """
    df = gdf.copy(deep=False)

    # ── 1. Pré-traitement de ICU ─────────────────────────────────────────
    # ICU négatif = fraîcheur (bon), positif = chaleur (mauvais)
    # On transforme pour que les valeurs élevées = mauvais
    # Décalage pour rendre tout positif avant normalisation
    df["icu_transformed"] = df["icu"]  # les valeurs négatives resteront basses = bonnes

    # ── 2. Normalisation MinMaxScaler (0-1) ──────────────────────────────
    all_cols = RISK_COLS + CAPACITY_COLS + RESILIENCE_COLS
    # Remplacer icu_transformed dans le df original
    gdf["icu_transformed"] = df["icu_transformed"]

    scaler = MinMaxScaler()
    normalized = pd.DataFrame(
        scaler.fit_transform(df[all_cols].fillna(0)),
        columns=all_cols,
        index=df.index,
    )

    # ── 3. Calcul du score composite ─────────────────────────────────────
    # Risques : valeur normalisée élevée = mauvais → on garde tel quel
    risk_score = normalized[RISK_COLS].mean(axis=1)

    # Capacité : valeur normalisée élevée = loin = bon → on inverse (1 - x)
    # pour que score élevé = mauvais
    capacity_score = 1 - normalized[CAPACITY_COLS].mean(axis=1)

    # Résilience : valeur normalisée élevée = bon → on inverse (1 - x)
    # pour que score élevé = mauvais
    resilience_score = 1 - normalized[RESILIENCE_COLS].mean(axis=1)

    # Score composite (0 = excellent, 1 = très mauvais)
    composite = (
        WEIGHT_RISK * risk_score
        + WEIGHT_CAPACITY * capacity_score
        + WEIGHT_RESILIENCE * resilience_score
    )

    gdf["score_value"] = composite

    # ── 4. Discrétisation en quintiles A-E ───────────────────────────────
    try:
        gdf["score"] = pd.qcut(
            composite, q=5, labels=SCORE_LABELS, duplicates="drop"
        ).astype(str)
    except ValueError:
        # Fallback si pas assez de valeurs distinctes pour 5 quantiles
        gdf["score"] = pd.cut(
            composite, bins=5, labels=SCORE_LABELS, duplicates="drop"
        ).astype(str)

    # Nettoyage colonne temporaire
    if "icu_transformed" in gdf.columns:
        gdf.drop(columns=["icu_transformed"], inplace=True)

    print(f"✅ Scores calculés – distribution : {gdf['score'].value_counts().to_dict()}")


def get_recommendations(score: str, cluster: int) -> List[str]:
    """
    Génère une liste de recommandations textuelles
    en fonction du score de résilience et du cluster.
    """
    recs: List[str] = []

    # Recommandations par score
    if score in ("D", "E"):
        recs.append("⚠️ Zone à risque élevé – vigilance recommandée.")
        recs.append("Consultez le Plan de Prévention des Risques de votre commune.")
        recs.append("Vérifiez votre couverture d'assurance habitation.")
    elif score == "C":
        recs.append("Zone à risque modéré – restez informé des alertes météo.")
        recs.append("Pensez à souscrire une garantie catastrophe naturelle.")
    elif score in ("A", "B"):
        recs.append("✅ Zone bien résiliente – risque faible.")
        recs.append("Continuez à entretenir les espaces verts autour de votre habitation.")

    # Recommandations par cluster
    cluster_recs = {
        0: "Votre zone est exposée aux inondations. Prévoyez un kit d'urgence.",
        1: "Zone industrielle proche – surveillez la qualité de l'air.",
        2: "Risque de retrait/gonflement des argiles – vérifiez les fondations.",
        3: "Îlot de chaleur détecté – hydratez-vous et végétalisez votre espace.",
        4: "Zone avec bon potentiel de résilience – encouragez les initiatives locales.",
        5: "Zone mixte – plusieurs aléas modérés combinés.",
    }
    if cluster in cluster_recs:
        recs.append(cluster_recs[cluster])

    return recs
