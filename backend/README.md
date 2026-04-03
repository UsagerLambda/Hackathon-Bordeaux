# Résili-Score — Backend API

API FastAPI pour le calcul et la restitution des scores de résilience sur la métropole bordelaise.

## Stack technique

- **Python** 3.9+
- **FastAPI** + **Uvicorn**
- **GeoPandas** / **Shapely** — manipulation de données géospatiales
- **scikit-learn** — normalisation des features (MinMaxScaler)
- **httpx** — appels HTTP asynchrones vers l'API BAN

## Structure du projet

```
backend/
├── main.py                  # Point d'entrée (placeholder)
├── pyproject.toml
├── requirements.txt
├── scores.geojson           # Données sources (~18.5 MB, ~1000+ mailles)
└── src/api/
    ├── main.py              # Application FastAPI, CORS, routeurs
    ├── data_loader.py       # Chargement du GeoDataFrame au démarrage
    ├── scoring.py           # Algorithme de scoring et recommandations
    ├── poi_loader.py        # Base de refuges/gymnases et calcul de distance
    └── routes/
        ├── address.py       # GET /api/address
        ├── cell.py          # GET /api/cell/{cell_id}
        └── map.py           # GET /api/map
```

## Installation

```bash
cd backend

# Avec pip
pip install -r requirements.txt

# Ou avec uv
uv sync
```

## Lancement

```bash
uvicorn src.api.main:app --reload --port 9456
```

La documentation interactive (Swagger) est disponible sur `http://localhost:9456/docs`.

## Endpoints

| Méthode | Route | Description |
|---------|-------|-------------|
| `GET` | `/` | Health check |
| `GET` | `/api/address?q={adresse}` | Géocode une adresse et retourne le score de la maille correspondante |
| `GET` | `/api/cell/{cell_id}` | Données détaillées d'une maille (score, cluster, recommandations, refuges proches) |
| `GET` | `/api/map` | GeoJSON complet de toutes les mailles enrichi des scores et labels |

## Algorithme de scoring

Le score de résilience est calculé à partir de 11 variables environnementales normalisées (MinMaxScaler), regroupées en trois catégories pondérées :

| Catégorie | Poids | Variables |
|-----------|-------|-----------|
| Risques | 50 % | Risque inondation, nappe phréatique, présence d'argile, îlot de chaleur urbain (ICU), zone PPRT, zones humides |
| Capacités | 25 % | Distance aux industries et sites pollués (inversé) |
| Résilience | 25 % | Couverture végétale, capacité d'infiltration (inversé) |

Le score composite est discrétisé en quintiles et converti en lettre de **A** (excellent, faible risque) à **E** (mauvais, risque élevé). Un clustering en 6 groupes caractérise les profils de risque dominants.

## Dépendances externes

- **API BAN** (`api-adresse.data.gouv.fr`) — géocodage d'adresses, sans authentification

## Notes

- Aucune variable d'environnement requise ; la configuration est entièrement en dur (adapté hackathon).
- Le CORS est ouvert (`*`) pour faciliter l'intégration frontend.
- Le fichier `scores.geojson` doit être présent à la racine du dossier `backend/`.
