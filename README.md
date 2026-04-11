# Résili-Score

> **Le Nutri-Score de la résilience urbaine pour Bordeaux Métropole.**

Hackathon Bordeaux Métropole — 30 mars au 3 avril 2026
Équipe : Clément Chassemon (ML), Lucas Scianna (Backend), Mila Audu (Frontend)

---

## Problématique

Chaque risque est traité séparément par les outils officiels, alors qu'ils se cumulent sur un même territoire. Un habitant de Cenon peut être simultanément en zone inondable, sur argile instable, et à 3 km d'une installation industrielle — sans le savoir.

**Sur les 9 624 zones analysées de Bordeaux Métropole, 100% présentent au moins un risque naturel ou industriel non nul.**

Résili-Score agrège 12 sources de données open data sur une grille de 9 624 cellules de 250m × 250m et traduit tout ça en une lettre (A à F) + un profil de risque lisible par n'importe qui.

---

## Démarrage rapide

```bash
git clone <repo>
cd Hackathon-Bordeaux
```

### 1. Données (première fois uniquement)

```bash
cd ml_dir
uv sync
python download_data.py   # télécharge ~500 MB depuis data.gouv.fr / Géorisques
```

### 2. Pipeline ML (première fois, ou si les données changent)

```bash
python main.py            # features → kmeans → scoring → scores/scores.geojson
```

### 3. Lancer l'application

```bash
cd ..
./start.sh all            # backend (port 9456) + frontend (port 8080)
```

Puis ouvrir **http://localhost:8080**.

---

## Commandes disponibles

```bash
./start.sh backend    # API FastAPI uniquement        → http://localhost:9456
./start.sh frontend   # Serveur frontend uniquement   → http://localhost:8080
./start.sh all        # Les deux en parallèle
./start.sh pipeline   # Relancer le pipeline ML
./start.sh download   # Re-télécharger les données sources
```

---

## Architecture

```
Hackathon-Bordeaux/
├── start.sh              # script de lancement
│
├── ml_dir/               # pipeline ML
│   ├── download_data.py  # téléchargement des sources open data
│   ├── main.py           # orchestrateur (features → kmeans → scoring)
│   ├── config.py         # paramètres (charge .env)
│   ├── .env.example      # template de configuration
│   └── pipeline/
│       ├── features.py   # feature engineering sur grille 250m
│       ├── kmeans.py     # clustering KMeans
│       └── scoring.py    # scores pondérés + explications SHAP
│
├── scores/
│   └── scores.geojson    # output ML → lu par le backend
│
├── data/                 # données sources (gitignorées, voir download_data.py)
│
├── backend/              # API FastAPI
│   └── src/api/
│       ├── main.py       # app + CORS (configurer ALLOWED_ORIGINS en prod)
│       ├── routes/       # /api/map  /api/cell/{id}  /api/address
│       ├── data_loader.py
│       ├── scoring.py
│       ├── industries_loader.py
│       └── poi_loader.py
│
└── frontend/             # carte interactive
    ├── config.js         # URL du backend (dérivée automatiquement depuis window.location)
    ├── app.js
    ├── index.html
    └── style.css
```

---

## Configuration

### Frontend — `frontend/config.js`

L'URL du backend est dérivée automatiquement depuis le hostname du navigateur. En production, modifier :

```js
const API_BASE_URL = 'https://mon-backend.fr';
```

### Backend — variable d'environnement

```bash
ALLOWED_ORIGINS=https://mon-frontend.fr uvicorn src.api.main:app --port 9456
```

Par défaut le CORS est ouvert (`*`) pour le développement local.

### ML — `ml_dir/.env`

Copier `.env.example` → `.env` et ajuster les poids ou le nombre de clusters :

```bash
cp ml_dir/.env.example ml_dir/.env
```

---

## Stack technique

| Composant | Technologies |
|---|---|
| Frontend | HTML/CSS/JS vanilla, MapLibre GL JS |
| Backend | Python, FastAPI, GeoPandas, Shapely |
| ML | KMeans (scikit-learn), Ridge, SHAP, MinMaxScaler |
| Géocodage | Base Adresse Nationale — api-adresse.data.gouv.fr |
| Données | Bordeaux Métropole Open Data, Géorisques, INSEE — Licence Ouverte v2.0 |

---

*Projet réalisé dans le cadre du défi [Prévention des risques à Bordeaux Métropole](https://defis.data.gouv.fr/defis/prevention-des-risques-a-bordeaux-metropole) — Open Data University / data.gouv.fr*
