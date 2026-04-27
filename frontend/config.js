// En développement local, pointer vers le backend sur le port 9456.
// En production (Render), laisser vide : frontend et backend sont sur la même origine.
const API_BASE_URL = (window.location.port === '9456' || window.location.port === '8080')
    ? `http://${window.location.hostname}:9456`
    : '';
