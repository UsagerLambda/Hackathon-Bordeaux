"""
scoring.py — Étape 3 : Calcul des scores de résilience + explications SHAP.

Lecture  : ml_pipeline/kmeans_clusters.geojson
Écriture : ml_pipeline/scores.geojson
           ../scores/scores.geojson  (copie pour le backend)

Usage autonome : python pipeline/scoring.py
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import shap
import numpy as np
import pandas as pd
import geopandas as gpd
from sklearn.linear_model import Ridge
from sklearn.preprocessing import MinMaxScaler
from config import config

FEATURES_PARTICULIER = [
    "flood_score", "nappe", "argile", "icu", "in_pprt",
    "green_cover", "water_infiltration", "zone_humide",
    "dist_industrie", "dist_sites_pol",
]
FEATURES_ELU = FEATURES_PARTICULIER + ["population"]

# ── Labels SHAP ───────────────────────────────────────────────────────────────

_LABELS_RISK = {
    "flood_score":        "au risque de crue",
    "nappe":              "à la remontée de nappe phréatique",
    "argile":             "au retrait-gonflement des argiles",
    "icu":                "à l'îlot de chaleur urbain",
    "in_pprt":            "à un site industriel dangereux (PPRT)",
    "dist_sites_pol":     "à la proximité de sites pollués",
    "dist_industrie":     "à la proximité d'établissements polluants",
    "water_infiltration": "à une forte infiltration du sol",
    "green_cover":        "à l'absence de couverture végétale",
    "zone_humide":        "à une zone humide",
    "population":         "à une forte densité de population exposée",
}

_LABELS_PROTECT = {
    "flood_score":        "faible risque de crue",
    "nappe":              "faible risque de nappe",
    "argile":             "sol peu argileux",
    "icu":                "îlot de fraîcheur",
    "in_pprt":            "hors zone PPRT",
    "dist_sites_pol":     "éloignée des sites pollués",
    "dist_industrie":     "éloignée des établissements polluants",
    "water_infiltration": "sol peu perméable",
    "green_cover":        "présence de végétation / espaces verts",
    "zone_humide":        "hors zone humide",
    "population":         "faible densité de population",
}

_MESURES_PARTICULIER = {
    "flood_score":        "Surélever les équipements électriques, souscrire une assurance catastrophe naturelle, consulter le PPRI de votre commune.",
    "nappe":              "Éviter les sous-sols non étanchéifiés, installer un système de pompage préventif.",
    "argile":             "Faire réaliser une étude géotechnique avant travaux, surveiller les fissures en façade.",
    "icu":                "Végétaliser les abords, installer une isolation thermique performante, prévoir des protections solaires.",
    "in_pprt":            "Consulter le Plan de Prévention des Risques Technologiques de votre commune.",
    "dist_sites_pol":     "Consulter la base BASOL pour l'historique du site, faire analyser les sols si projet de jardin potager.",
    "dist_industrie":     "S'informer sur le Plan Particulier d'Intervention (PPI) local.",
    "water_infiltration": "Vérifier l'état des fondations, assurer un drainage périphérique efficace.",
    "green_cover":        "Planter des arbres et végétaux autour du logement pour réduire l'exposition thermique.",
    "zone_humide":        "Ne pas remblayer, préserver la capacité d'absorption naturelle du terrain.",
}

_MESURES_ELU = {
    "flood_score":        "Mettre à jour le PPRI, renforcer les digues et zones tampon, intégrer le risque inondation dans le PLU.",
    "nappe":              "Cartographier les zones vulnérables, réglementer les constructions en sous-sol dans les zones à risque.",
    "argile":             "Imposer des études géotechniques G2 obligatoires dans les zones argileuses du PLU.",
    "icu":                "Développer la trame verte urbaine, désimperméabiliser les sols, créer des îlots de fraîcheur.",
    "in_pprt":            "Réviser le PPRT, renforcer les plans d'évacuation et la communication auprès des riverains.",
    "dist_sites_pol":     "Mettre à jour l'inventaire BASOL, prévoir des servitudes d'utilité publique sur les sites pollués.",
    "dist_industrie":     "Renforcer le suivi des établissements Seveso, actualiser les PPI avec les services de l'État.",
    "water_infiltration": "Intégrer des noues et bassins de rétention dans les projets d'aménagement.",
    "green_cover":        "Protéger les espaces boisés classés, développer les corridors écologiques dans le PLU.",
    "zone_humide":        "Classer les zones humides en espaces naturels protégés, interdire tout remblaiement.",
    "population":         "Prioriser les actions de sensibilisation et d'évacuation dans les zones à forte densité exposées.",
}


# ── Fonctions scoring ─────────────────────────────────────────────────────────

def _normalize(gdf: gpd.GeoDataFrame, features: list) -> pd.DataFrame:
    scaler = MinMaxScaler()
    X = pd.DataFrame(scaler.fit_transform(gdf[features]), columns=features)
    for col in ["dist_industrie", "dist_sites_pol", "green_cover", "ind_snv"]:
        if col in X:
            X[col] = 1 - X[col]
    return X


def _compute_score(X_norm: pd.DataFrame, weights: dict, interactions: list = None) -> pd.Series:
    w = pd.Series(weights)
    w = w / w.sum()
    score = (X_norm[w.index] * w).sum(axis=1)
    if interactions:
        for (f1, f2, coef) in interactions:
            score += coef * X_norm[f1] * X_norm[f2]
    return ((score - score.min()) / (score.max() - score.min()) * 100).round(1)


def _explain_cell(idx: int, shap_df: pd.DataFrame, score: float) -> str:
    top_n = config.SHAP_TOP_N
    contribs = shap_df.iloc[idx].sort_values(ascending=False)
    positifs = contribs[contribs > 0].head(top_n)
    negatifs = contribs[contribs < 0].head(2)

    parties = []
    for feat, val in positifs.items():
        label = _LABELS_RISK.get(feat, feat)
        intensite = "fortement exposée " if val > 2 else "exposée "
        parties.append(intensite + label)

    phrase = "Cette zone est " + ", ".join(parties) if parties else "Cette zone présente peu de risques identifiés"

    if not negatifs.empty:
        prot = [_LABELS_PROTECT.get(f, f) for f in negatifs.index]
        phrase += f". Atténué par : {', '.join(prot)}."

    phrase += f" (score : {score:.0f}/100)"
    return phrase


def _conseils_cell(idx: int, shap_df: pd.DataFrame, mesures: dict) -> str:
    top_n = config.SHAP_TOP_N
    contribs = shap_df.iloc[idx].sort_values(ascending=False)
    positifs = contribs[contribs > 0].head(top_n)
    return " | ".join(mesures[f] for f in positifs.index if f in mesures)


def _shap_df(X_norm: pd.DataFrame, scores: pd.Series) -> pd.DataFrame:
    model = Ridge()
    model.fit(X_norm, scores)
    explainer = shap.LinearExplainer(model, X_norm)
    return pd.DataFrame(explainer.shap_values(X_norm), columns=X_norm.columns)


# ── Pipeline ──────────────────────────────────────────────────────────────────

def run_scoring() -> gpd.GeoDataFrame:
    input_path = config.OUTPUT_DIR / "kmeans_clusters.geojson"
    if not input_path.exists():
        raise FileNotFoundError(f"kmeans_clusters.geojson introuvable : {input_path}\nLancer d'abord pipeline/kmeans.py")

    print(f"  → Chargement de {input_path.name}...")
    gdf = gpd.read_file(input_path).to_crs(config.CRS_LAMBERT93)

    # ── Score particulier ─────────────────────────────────────────────────────
    print("  → Score particulier...")
    interactions_part = [
        ("argile",      "water_infiltration", 0.10),
        ("flood_score", "nappe",              0.10),
        ("zone_humide", "flood_score",        0.08),
    ]
    X_part = _normalize(gdf, FEATURES_PARTICULIER)
    gdf["score_particulier"] = _compute_score(X_part, config.WEIGHTS_PARTICULIER, interactions_part)

    # ── Score élu ─────────────────────────────────────────────────────────────
    print("  → Score élu...")
    interactions_elu = [
        ("flood_score", "population",         0.15),
        ("icu",         "population",         0.10),
        ("argile",      "water_infiltration", 0.08),
        ("zone_humide", "flood_score",        0.08),
    ]
    X_elu = _normalize(gdf, FEATURES_ELU)
    gdf["score_elu"] = _compute_score(X_elu, config.WEIGHTS_ELU, interactions_elu)

    # ── SHAP + explications ───────────────────────────────────────────────────
    print("  → Calcul SHAP et génération des explications...")
    shap_part = _shap_df(X_part, gdf["score_particulier"])
    shap_elu  = _shap_df(X_elu,  gdf["score_elu"])

    n = len(gdf)
    gdf["explication_particulier"] = [_explain_cell(i, shap_part, gdf["score_particulier"].iloc[i]) for i in range(n)]
    gdf["conseils_particulier"]    = [_conseils_cell(i, shap_part, _MESURES_PARTICULIER)             for i in range(n)]
    gdf["explication_elu"]         = [_explain_cell(i, shap_elu,  gdf["score_elu"].iloc[i])         for i in range(n)]
    gdf["conseils_elu"]            = [_conseils_cell(i, shap_elu,  _MESURES_ELU)                    for i in range(n)]

    # ── Sauvegarde ────────────────────────────────────────────────────────────
    gdf_out = gdf.to_crs(config.CRS_WGS84)

    output = config.OUTPUT_DIR / "scores.geojson"
    gdf_out.to_file(output, driver="GeoJSON")
    print(f"  ✓ scores.geojson → {output}")

    scores_copy = config.SCORES_DIR / "scores.geojson"
    gdf_out.to_file(scores_copy, driver="GeoJSON")
    print(f"  ✓ scores.geojson → {scores_copy}  (copie backend)")

    return gdf_out


if __name__ == "__main__":
    print("\n── Étape 3 : Scoring + SHAP ─────────────────────────────────────────")
    run_scoring()
