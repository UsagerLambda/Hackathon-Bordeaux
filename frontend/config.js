// En développement local, l'URL pointe vers le backend sur le port 9456.
// En production (Vercel), ce fichier est remplacé par build.sh avec la variable API_BASE_URL.
const API_BASE_URL = `http://${window.location.hostname}:9456`;
