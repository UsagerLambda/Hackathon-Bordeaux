# Résili-Score

> **Le Nutri-Score de la résilience urbaine pour Bordeaux Métropole.**

Hackathon Bordeaux Métropole — 30 mars au 3 avril 2026
Équipe : Clément Chassemon (ML), Lucas Scianna (Backend), Mila Audu (Frontend)

---

## Problématique

Chaque risque est traité séparément par les outils officiels, alors qu'ils se cumulent sur un même territoire. Un habitant de Cenon peut être simultanément en zone inondable, sur argile instable, et à 3 km d'une installation industrielle — sans le savoir.

45% des Girondins citent les risques naturels comme préoccupation, mais se sentent moins bien informés sur les risques industriels. **Sur les 9 624 zones analysées de Bordeaux Métropole, 100% présentent au moins un risque naturel ou industriel non nul.**

La Garonne a récemment débordé sur les quais de Bordeaux — preuve que le risque inondation n'est pas théorique.

## Solution

Résili-Score est un outil citoyen : n'importe quel Girondin peut taper son adresse et comprendre en 30 secondes à quoi il est exposé.

Le site agrège 12 sources de données open data sur une grille de 9 624 cellules de 250m × 250m, croise les risques via K-Means et un score pondéré, et traduit tout ça en une lettre (A à E) + un profil de risque lisible par n'importe qui.

## Message au jury

On veut que n'importe quel Girondin puisse taper son adresse et comprendre en 30 secondes à quoi il est exposé.

---

## Stack technique

| Composant | Technologies |
|---|---|
| Frontend | HTML/CSS/JS vanilla, MapLibre GL JS |
| Backend | Python, FastAPI, GeoPandas, Shapely |
| ML | K-Means (scikit-learn), SHAP, Ridge, MinMaxScaler |
| API externe | Base Adresse Nationale (géocodage) |

## Algorithme

1. **Pipeline de données** (`run.py`) — 11 features extraites par spatial join sur une grille 250m × 250m
2. **Clustering** (`kmeans.ipynb`) — K-Means avec k optimal (score silhouette), 9 clusters avec labels sémantiques
3. **Scoring** (`scoring.ipynb`) — deux scores 0–100 avec pondération expert + interactions entre features, explications générées par SHAP

| Catégorie | Poids | Variables |
|---|---|---|
| Risques | 50% | Inondation, nappe phréatique, argile, ICU, PPRT, zones humides |
| Capacités | 25% | Distance aux industries et sites pollués |
| Résilience | 25% | Couverture végétale, capacité d'infiltration |

Les poids sont arbitraires mais documentés et facilement ajustables.

## Sources de données (12 sources)

| Donnée | Source |
|---|---|
| Zonages inondation TRI 2020 | Géorisques |
| Remontée de nappes | Géorisques |
| Aléa retrait-gonflement argiles | DataHub Bordeaux Métropole |
| Îlot de chaleur/fraîcheur | DataHub Bordeaux Métropole |
| Zones PPRT | DataHub Bordeaux Métropole |
| Sites pollués BASOL | DataHub Bordeaux Métropole |
| Établissements polluants | DataHub Bordeaux Métropole |
| Capacité d'infiltration | DataHub Bordeaux Métropole |
| Zones boisées | DataHub Bordeaux Métropole |
| Zones humides | DataHub Bordeaux Métropole |
| Espaces verts | DataHub Bordeaux Métropole |
| Population carroyage 200m | INSEE 2015 |

## Lancer le projet

```bash
# Backend
cd backend
uv sync
uvicorn src.api.main:app --reload --port 8000

# Frontend
cd frontend
# Ouvrir index.html dans un navigateur
```
