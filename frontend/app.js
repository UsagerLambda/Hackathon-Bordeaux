let map;
let selectedFeatureId = null;
let refugeMarkers = [];
let industrieMarkers = [];
let zonePollueeMarkers = [];
let activePopups = [];


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
// REFUGES
// =====================

function nettoyerMarkers() {
    refugeMarkers.forEach(m => m.remove());
    industrieMarkers.forEach(m => m.remove());
    zonePollueeMarkers.forEach(m => m.remove());
    activePopups.forEach(p => p.remove());
    refugeMarkers = [];
    industrieMarkers = [];
    zonePollueeMarkers = [];
    activePopups = [];
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

        // Affiche l'overlay de chargement si besoin
        fetch('http://127.0.0.1:8000/api/map')
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
                            'case',
                            ['boolean', ['feature-state', 'selected'], false],
                            '#3b82f6',
                            [
                                'step',
                                ['get', 'score_particulier'],
                                '#8B0000',
                                10, '#05852b',
                                18, '#dba239ab',
                                26, '#DF7103',
                                41, '#C74811',
                                56, '#7D0033',
                                76, '#4C0035'
                            ]
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
                            const featureId = e.features[0].id;

                            if (selectedFeatureId !== null) {
                                map.setFeatureState(
                                    { source: 'kmeans', id: selectedFeatureId },
                                    { selected: false }
                                );
                            }

                            selectedFeatureId = featureId;
                            map.setFeatureState(
                                { source: 'kmeans', id: featureId },
                                { selected: true }
                            );

                            displayLocationInfo(props);

                            fetch(`http://localhost:8000/api/cell/${props.cell_id}`)
                                .then(r => r.json())
                                .then(data => afficherPOI(data))
                                .catch(err => console.error('Erreur POI:', err));
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
            <strong><i class="fas fa-circle-question"></i> Diagnostic:</strong><br>
            ${props.explication_particulier || ''}
        </div>

        ${props.conseils_particulier ? `
        <div class="recommendations-box">
            <strong><i class="fas fa-wand-magic-sparkles"></i> Recommandations:</strong><br>
            ${props.conseils_particulier.replace(/\|/g, '<br>• ')}
        </div>
        ` : ''}

        <hr class="info-divider">

        <div class="details-box">
            <strong><i class="fas fa-circle-plus"></i> Détails de la zone:</strong>
            <div class="detail-grid">
                <div class="detail-item">
                    <span class="detail-icon"><i class="fas fa-water"></i></span>
                    <div class="detail-content">
                        <span class="detail-label">Risque inondation</span>
                        <span class="detail-value">${['Aucun', 'Faible', 'Modéré', 'Fort', 'Très fort'][props.flood_score] || 'N/A'}</span>
                    </div>
                </div>
                <div class="detail-item">
                    <span class="detail-icon"><i class="fas fa-droplet"></i></span>
                    <div class="detail-content">
                        <span class="detail-label">Nappe phréatique</span>
                        <span class="detail-value">${['Profonde', 'Moyenne', 'Superficielle'][props.nappe] || 'N/A'}</span>
                    </div>
                </div>
                <div class="detail-item">
                    <span class="detail-icon"><i class="fas fa-cubes"></i></span>
                    <div class="detail-content">
                        <span class="detail-label">Risque argile</span>
                        <span class="detail-value">${props.argile}/3</span>
                    </div>
                </div>
                <div class="detail-item">
                    <span class="detail-icon"><i class="fas fa-temperature-high"></i></span>
                    <div class="detail-content">
                        <span class="detail-label">Îlot de chaleur</span>
                        <span class="detail-value">${props.icu > 0 ? '+' : ''}${props.icu}°C</span>
                    </div>
                </div>
                <div class="detail-item">
                    <span class="detail-icon"><i class="fas fa-industry"></i></span>
                    <div class="detail-content">
                        <span class="detail-label">Zone PPRT</span>
                        <span class="detail-value">${props.in_pprt ? 'Oui' : 'Non'}</span>
                    </div>
                </div>
                <div class="detail-item">
                    <span class="detail-icon"><i class="fas fa-tree"></i></span>
                    <div class="detail-content">
                        <span class="detail-label">Espaces verts</span>
                        <span class="detail-value">${props.green_cover ? 'Oui' : 'Non'}</span>
                    </div>
                </div>
                <div class="detail-item">
                    <span class="detail-icon"><i class="fas fa-frog"></i></span>
                    <div class="detail-content">
                        <span class="detail-label">Zone humide</span>
                        <span class="detail-value">${props.zone_humide ? 'Oui' : 'Non'}</span>
                    </div>
                </div>
                <div class="detail-item">
                    <span class="detail-icon"><i class="fas fa-cloud-rain"></i></span>
                    <div class="detail-content">
                        <span class="detail-label">Infiltration eau</span>
                        <span class="detail-value">${props.water_infiltration}/10</span>
                    </div>
                </div>
                <div class="detail-item">
                    <span class="detail-icon"><i class="fas fa-building"></i></span>
                    <div class="detail-content">
                        <span class="detail-label">Distance industrie</span>
                        <span class="detail-value">${Math.round(props.dist_industrie)}m</span>
                    </div>
                </div>
                <div class="detail-item">
                    <span class="detail-icon"><i class="fas fa-biohazard"></i></span>
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

document.addEventListener('DOMContentLoaded', function () {
            initMap();

            document.addEventListener('keydown', function (e) {
                if (e.key === 'Escape') {
                    closePopup();
                }
            });
        });


    function handleSearch(event) {
        event.preventDefault();
        const searchTerm = document.getElementById('search-input').value.trim();
        if (!searchTerm) return;

        fetch(`http://127.0.0.1:8000/api/address?q=${encodeURIComponent(searchTerm)}`)
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
                    .addTo(map);

                map.flyTo({ center: coords, zoom: 16, duration: 1000 });

                displayLocationInfo({
                    score_particulier: parseFloat(data.score),
                    cluster_label: data.cluster.label,
                    explication_particulier: data.explication,
                    conseils_particulier: data.recommendations.join(' | '),
                    ...data.features
                }, data.address);
                
                afficherPOI(data);
            })
            .catch(err => {
                console.error('Erreur recherche adresse:', err);
                alert('Adresse introuvable');
            });
    }

    function afficherPOI(data) {
        nettoyerMarkers();
        if (data.nearest_refuges) {
            data.nearest_refuges.forEach(refuge => {
                const popup = new maplibregl.Popup({ offset: 25, closeButton: false, closeOnClick: false, className: 'hover-popup' })
                    .setHTML(`
                        <p><strong><i class="fas fa-person-shelter"></i> Point de refuge</strong></p>
                        <p>${refuge.name}</p>
                        <p>${refuge.address}</p>
                        <p>${Math.round(refuge.distance_m)}m</p>
                    `);

                const marker = new maplibregl.Marker({ color: '#1a9641' })
                    .setLngLat([refuge.lon, refuge.lat])
                    .addTo(map);

                const el = marker.getElement();
                el.addEventListener('mouseenter', () => popup.addTo(map).setLngLat([refuge.lon, refuge.lat]));
                el.addEventListener('mouseleave', () => popup.remove());

                activePopups.push(popup);
                refugeMarkers.push(marker);
            });
        }

        if (data.nearby_industrial_sites) {
            data.nearby_industrial_sites.forEach(site => {
                if (!site.lat || !site.lon) return;

                const estPollue = site.type_risque.includes('Pollué') || site.type_risque.includes('BASOL');
                const couleur = estPollue ? '#dba339' : '#C74811';
                const icone = estPollue ? '<i class="fas fa-biohazard"></i> Zone polluée' : '<i class="fas fa-industry"></i> Site industriel';
                const markersArray = estPollue ? zonePollueeMarkers : industrieMarkers;

                const popup = new maplibregl.Popup({ offset: 25, closeButton: false, closeOnClick: false, className: 'hover-popup' })
                    .setHTML(`
                        <p><strong>${icone}</strong></p>
                        <p>${site.nom}</p>
                        <p>Type : ${site.type_risque}</p>
                        <p>${Math.round(site.distance_m)}m</p>
                    `);

                const marker = new maplibregl.Marker({ color: couleur })
                    .setLngLat([site.lon, site.lat])
                    .addTo(map);
                
                const el = marker.getElement();
                el.addEventListener('mouseenter', () => popup.addTo(map).setLngLat([site.lon, site.lat]));
                el.addEventListener('mouseleave', () => popup.remove());

                activePopups.push(popup);
                markersArray.push(marker);
            });
        }
    }