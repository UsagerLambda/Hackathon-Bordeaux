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

## Sources de données

Toutes les données sont issues de sources ouvertes sous **Licence Ouverte v2.0** (Etalab) ou **ODbL** :

| Donnée | Source |
|--------|--------|
| Risques inondation (PPRI / nappes) | [Géorisques — georisques.gouv.fr](https://www.georisques.gouv.fr) |
| Sites et sols pollués (BASOL) | [Bordeaux Métropole Open Data](https://datahub.bordeaux-metropole.fr) |
| Établissements industriels polluants | [Bordeaux Métropole Open Data](https://datahub.bordeaux-metropole.fr) |
| PPRT (risques technologiques) | [Bordeaux Métropole Open Data](https://datahub.bordeaux-metropole.fr) |
| Îlots de chaleur / fraîcheur (ICU) | [Bordeaux Métropole Open Data](https://datahub.bordeaux-metropole.fr) |
| Aléa retrait/gonflement des argiles | [Bordeaux Métropole Open Data](https://datahub.bordeaux-metropole.fr) |
| Capacité d'infiltration | [Bordeaux Métropole Open Data](https://datahub.bordeaux-metropole.fr) |
| Équipements collectifs (refuges/gymnases) | [Base Permanente des Équipements — INSEE](https://www.insee.fr/fr/statistiques/8217527) |
| Géocodage adresses | [API BAN — adresse.data.gouv.fr](https://adresse.data.gouv.fr/api-doc/adresse) |

## Données requises

Les fichiers GeoJSON ne sont pas versionnés (taille). Ils doivent être placés à la racine du dossier `backend/` avant de lancer l'API :

Ces fichiers sont générés/téléchargés par le pipeline ML (`ml_dir/`). Structure attendue à la racine du repo :

```
scores/
└── scores.geojson          ← généré par le pipeline ML
data/
├── ri_etab_pol_p.geojson   ← téléchargé depuis Bordeaux Métropole Open Data
└── ri_basol_p.geojson      ← téléchargé depuis Bordeaux Métropole Open Data
```

| Fichier | Source |
|---------|--------|
| `scores/scores.geojson` | Généré par le pipeline ML (`ml_dir/`) |
| `data/ri_etab_pol_p.geojson` | [Bordeaux Métropole — Établissements industriels polluants](https://datahub.bordeaux-metropole.fr/explore/dataset/ri_etab_pol_p) |
| `data/ri_basol_p.geojson` | [Bordeaux Métropole — Sites et sols pollués BASOL](https://datahub.bordeaux-metropole.fr/explore/dataset/ri_basol_p) |

## Notes

- Définir la variable d'environnement `ALLOWED_ORIGINS` pour restreindre le CORS en production (ex. `ALLOWED_ORIGINS=https://mondomaine.fr`). Par défaut ouvert (`*`) pour le développement local.
