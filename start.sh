#!/usr/bin/env bash
set -e

ROOT="$(cd "$(dirname "$0")" && pwd)"

# ── Couleurs ──────────────────────────────────────────────────────────────────
G="\033[0;32m"; Y="\033[0;33m"; B="\033[0;34m"; R="\033[0;31m"; N="\033[0m"

usage() {
    echo ""
    echo "Usage: ./start.sh [commande]"
    echo ""
    echo "  backend       Lance l'API FastAPI            (port 9456)"
    echo "  frontend      Lance le serveur frontend      (port 8080)"
    echo "  all           Lance backend + frontend"
    echo "  pipeline      Lance le pipeline ML complet"
    echo "  download      Télécharge les données sources"
    echo ""
    exit 1
}

start_backend() {
    echo -e "${B}── Backend ───────────────────────────────────────────────────────────${N}"
    cd "$ROOT/backend"
    echo -e "${G}  → http://localhost:9456${N}  |  Swagger : http://localhost:9456/docs"
    uv run uvicorn src.api.main:app --reload --host 0.0.0.0 --port 9456
}

start_frontend() {
    echo -e "${B}── Frontend ──────────────────────────────────────────────────────────${N}"
    cd "$ROOT/frontend"
    echo -e "${G}  → http://localhost:8080${N}"
    if command -v npx &>/dev/null; then
        npx serve . -l 8080
    else
        python3 -m http.server 8080
    fi
}

run_pipeline() {
    echo -e "${B}── Pipeline ML ───────────────────────────────────────────────────────${N}"
    cd "$ROOT/ml_dir"
    uv run python main.py
}

run_download() {
    echo -e "${B}── Téléchargement des données ────────────────────────────────────────${N}"
    cd "$ROOT/ml_dir"
    uv run python download_data.py
}

case "${1:-}" in
    backend)
        start_backend
        ;;
    frontend)
        start_frontend
        ;;
    all)
        echo -e "${Y}Lancement backend + frontend (Ctrl+C pour arrêter)${N}"
        trap 'kill 0' INT
        start_backend &
        sleep 2
        start_frontend &
        wait
        ;;
    pipeline)
        run_pipeline
        ;;
    download)
        run_download
        ;;
    *)
        usage
        ;;
esac
