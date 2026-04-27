#!/usr/bin/env bash
# Script de build pour Render (static site) – génère frontend/config.js avec l'URL du backend.
# Définir API_BASE_URL dans les variables d'environnement du projet Render.
set -e

if [ -z "${API_BASE_URL:-}" ]; then
    echo "⚠️  WARNING: API_BASE_URL n'est pas définie. Le frontend ne pourra pas contacter le backend."
    echo "   → Ajoute API_BASE_URL dans les variables d'environnement Render."
    API_URL=""
else
    echo "✅ API_BASE_URL = ${API_BASE_URL}"
    API_URL="${API_BASE_URL}"
fi

cat > frontend/config.js <<EOF
// Généré automatiquement par build.sh lors du déploiement.
// En local, ce fichier est remplacé par la version de développement (voir config.local.js).
const API_BASE_URL = '${API_URL}';
EOF

echo "✅ frontend/config.js généré."
