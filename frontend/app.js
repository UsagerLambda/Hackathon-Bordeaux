let map;

// =====================
// FONCTIONS UTILITAIRES
// =====================

function getLettre(score) {
    if (score >= 76) return "F";
    if (score >= 56) return "E";
    if (score >= 41) return "D";
    if (score >= 26) return "C";
    if (score >= 18) return "B";
    if (score >= 10) return "A";
    return "F";
}

function getCouleur(score) {
    if (score >= 76) return "#4C0035";
    if (score >= 56) return "#7D0033";
    if (score >= 41) return "#C74811";
    if (score >= 26) return "#dba339";
    if (score >= 18) return "#bbf534";
    if (score >= 10) return "#05852b";
    return "#8B0000";                     
}

function getDescriptionClasse(lettre) {
    const descriptions = {
        'F': 'Critique extrême',
        'E': 'Très fragile',
        'D': 'Fragile',
        'C': 'Moyen',
        'B': 'Résilient',
        'A': 'Très résilient',
    };
    return descriptions[lettre] || 'Inconnu';
}

// =====================
// INITIALISATION DE LA CARTE
// =====================

function initMap() {
    map = new maplibregl.Map({
        container: 'map',
        style: './satellite-style.json',
        center: [-0.5792, 44.8378],
        zoom: 12
    });

    map.on('load', () => {
        console.log('✅ Carte chargée');
        
        fetch('http://localhost:8000/api/map')
            .then(response => {
                if (!response.ok) throw new Error(`Erreur: ${response.status}`);
                return response.json();
            })
            .then(data => {
                console.log(`✅ ${data.features.length} zones chargées du backend`);
                
                map.addSource('kmeans', {
                    type: 'geojson',
                    data: data
                });
                
                map.addLayer({
                    id: 'kmeans-fill',
                    type: 'fill',
                    source: 'kmeans',
                    paint: {
                        'fill-color': [
                            'step',
                            ['get', 'score_particulier'],
                            '#8B0000',
                            10, '#05852b',
                            18, '#dba239ab',
                            26, '#DF7103',
                            41, '#C74811',
                            56, '#7D0033',
                            76, '#4C0035'
                        ],
                        'fill-opacity': 0.4
                    }
                });
                
                map.addLayer({
                    id: 'kmeans-outline',
                    type: 'line',
                    source: 'kmeans',
                    paint: {
                        'line-color': 'rgba(255, 255, 255, 0.36)',
                        'line-width': 0.5
                    }
                });
                
                map.on('click', 'kmeans-fill', (e) => {
                    if (e.features.length > 0) {
                        const props = e.features[0].properties;
                        console.log('🔍 Props reçues:', props); 
                        displayLocationInfo(props);
                    }
                });
                
                // 👆 Survol
                map.on('mouseenter', 'kmeans-fill', () => {
                    map.getCanvas().style.cursor = 'pointer';
                    map.setPaintProperty('kmeans-fill', 'fill-opacity', 0.7);
                });
                map.on('mouseleave', 'kmeans-fill', () => {
                    map.getCanvas().style.cursor = '';
                    map.setPaintProperty('kmeans-fill', 'fill-opacity', 0.4);
                });
            })
            .catch(err => {
                console.error('❌ Erreur chargement backend:', err);
                alert('❌ Erreur: impossible de charger les données. Vérifiez que l\'API tourne sur http://localhost:8000');
            });
    });

    map.on('error', (e) => {
        console.error('❌ Erreur MapLibre:', e);
    });
}

function displayLocationInfo(props, address = null) {
    const score = props.score_particulier || 50;
    const lettre = getLettre(score);
    const couleur = getCouleur(score);
    const description = getDescriptionClasse(lettre);

    document.getElementById('info-title').textContent = props.cluster_label || 'Zone';
    document.getElementById('info-card-body').innerHTML = `
        ${address ? `<p class="info-address">📍 ${address}</p>` : ''}

        <div class="score-display">
            <div class="score-circle" style="background-color: ${couleur};">
                ${lettre}
            </div>
            <div class="score-text">
                <strong style="color: ${couleur};">${Math.round(score)}/100</strong><br>
                <small>Classe: ${lettre} (${description})</small>
            </div>
        </div>

        <hr class="info-divider">

        <div class="diagnostic-box">
            <strong>📊 Diagnostic:</strong><br>
            ${props.explication_particulier || ''}
        </div>

        ${props.conseils_particulier ? `
        <div class="recommendations-box">
            <strong>💡 Recommandations:</strong><br>
            ${props.conseils_particulier.replace(/\|/g, '<br>• ')}
        </div>
        ` : ''}

        <hr class="info-divider">

        <div class="details-box">
            <strong>📋 Détails de la zone:</strong>
            <div class="detail-grid">
                <div class="detail-item">
                    <span class="detail-icon">🌊</span>
                    <div class="detail-content">
                        <span class="detail-label">Risque inondation</span>
                        <span class="detail-value">${['Aucun','Faible','Modéré','Fort','Très fort'][props.flood_score] || 'N/A'}</span>
                    </div>
                </div>
                <div class="detail-item">
                    <span class="detail-icon">💧</span>
                    <div class="detail-content">
                        <span class="detail-label">Nappe phréatique</span>
                        <span class="detail-value">${['Profonde','Moyenne','Superficielle'][props.nappe] || 'N/A'}</span>
                    </div>
                </div>
                <div class="detail-item">
                    <span class="detail-icon">🧱</span>
                    <div class="detail-content">
                        <span class="detail-label">Risque argile</span>
                        <span class="detail-value">${props.argile}/3</span>
                    </div>
                </div>
                <div class="detail-item">
                    <span class="detail-icon">🌡️</span>
                    <div class="detail-content">
                        <span class="detail-label">Îlot de chaleur</span>
                        <span class="detail-value">${props.icu > 0 ? '+' : ''}${props.icu}°C</span>
                    </div>
                </div>
                <div class="detail-item">
                    <span class="detail-icon">🏭</span>
                    <div class="detail-content">
                        <span class="detail-label">Zone PPRT</span>
                        <span class="detail-value">${props.in_pprt ? 'Oui' : 'Non'}</span>
                    </div>
                </div>
                <div class="detail-item">
                    <span class="detail-icon">🌳</span>
                    <div class="detail-content">
                        <span class="detail-label">Espaces verts</span>
                        <span class="detail-value">${props.green_cover ? 'Oui' : 'Non'}</span>
                    </div>
                </div>
                <div class="detail-item">
                    <span class="detail-icon">🏞️</span>
                    <div class="detail-content">
                        <span class="detail-label">Zone humide</span>
                        <span class="detail-value">${props.zone_humide ? 'Oui' : 'Non'}</span>
                    </div>
                </div>
                <div class="detail-item">
                    <span class="detail-icon">💦</span>
                    <div class="detail-content">
                        <span class="detail-label">Infiltration eau</span>
                        <span class="detail-value">${props.water_infiltration}/10</span>
                    </div>
                </div>
                <div class="detail-item">
                    <span class="detail-icon">🏗️</span>
                    <div class="detail-content">
                        <span class="detail-label">Distance industrie</span>
                        <span class="detail-value">${Math.round(props.dist_industrie)}m</span>
                    </div>
                </div>
                <div class="detail-item">
                    <span class="detail-icon">☣️</span>
                    <div class="detail-content">
                        <span class="detail-label">Sites pollués</span>
                        <span class="detail-value">${Math.round(props.dist_sites_pol)}m</span>
                    </div>
                </div>
            </div>
        </div>
    `;

    openPopup();
}

function openPopup() {
    const infoCard = document.getElementById('info-card');
    infoCard.classList.add('active');
}

function closePopup() {
    const infoCard = document.getElementById('info-card');
    infoCard.classList.remove('active');
}

function togglePopup() {
    const infoCard = document.getElementById('info-card');
    infoCard.classList.toggle('active');
}

function updatePopupContent(data) {
    if (data.title) {
        document.getElementById('info-title').textContent = data.title;
    }
    if (data.body) {
        document.getElementById('info-card-body').innerHTML = data.body;
    }
}

document.addEventListener('DOMContentLoaded', function() {
    initMap();
    
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            closePopup();
        }
    });
});


function handleSearch(event) {
    event.preventDefault();
    const searchTerm = document.getElementById('search-input').value.trim();
    if (!searchTerm) return;

    fetch(`http://localhost:8000/api/address?q=${encodeURIComponent(searchTerm)}`)
        .then(response => {
            if (!response.ok) throw new Error('Adresse introuvable');
            return response.json();
        })
        .then(data => {
            const coords = [data.coordinates.lon, data.coordinates.lat];

            if (window.currentMarker) {
                window.currentMarker.remove();
            }

            window.currentMarker = new maplibregl.Marker({ color: '#564caf' })
                .setLngLat(coords)
                .setPopup(
                    new maplibregl.Popup({ offset: 25 })
                    .setHTML(`
                        <p>lat: ${data.coordinates.lat} | lon: ${data.coordinates.lon}</p>
                    `)
                )
                .addTo(map);

            window.currentMarker.togglePopup();

            map.flyTo({ center: coords, zoom: 16, duration: 1000 });

            displayLocationInfo({
                score_particulier: parseFloat(data.score),
                cluster_label: data.cluster.label,
                explication_particulier: data.explication,
                conseils_particulier: data.recommendations.join(' | '),
                ...data.features
            }, data.address);
        })
        .catch(err => {
            console.error('Erreur recherche adresse:', err);
            alert('Adresse introuvable');
        });
}
