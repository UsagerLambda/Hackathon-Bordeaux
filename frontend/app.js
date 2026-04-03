// =====================
// INITIALISATION ET CONFIG
// =====================

let map; // Instance MapLibre
let currentMarker;
let searchResults = [];

/**
 * Calcule un score de résilience (0-100) basé sur les métriques du GeoJSON
 * Plus faible = plus critique, plus élevé = très résilient
 * 
 * Critères :
 * - risque d'inondation (flood_score) : pénalité majeure
 * - nappe phréatique (nappe) : pénalité mineure
 * - espaces verts (green_spaces) : bonus de résilience
 * - distance aux industries (dist_industrie) : bonus si loin
 */
function calculerScore(properties) {
    let score = 50; // Score de base
    
    // Pénalitépour risque d'inondation (0-10)
    if (properties.flood_score !== undefined) {
        score -= properties.flood_score * 8;
    }
    
    // Pénalité légère pour nappe phréatique profonde (1 = profond, 9 = superficiel)
    if (properties.nappe !== undefined) {
        score -= (10 - properties.nappe) * 2;
    }
    
    // Bonus pour espaces verts (résilience écologique)
    if (properties.green_spaces !== undefined) {
        score += properties.green_spaces * 3;
    }
    
    // Bonus si loin des industries polluantes
    if (properties.dist_industrie !== undefined && properties.dist_industrie > 5000) {
        score += 10;
    }
    
    // Bonus si pas de site pollué nearby
    if (properties.dist_sites_pol !== undefined && properties.dist_sites_pol > 8000) {
        score += 5;
    }
    
    // Pénalité pour ICU (ilôt de chaleur urbain) élevé
    if (properties.icu !== undefined && properties.icu > 5) {
        score -= 5;
    }
    
    // Limiter le score entre 0 et 100
    return Math.max(0, Math.min(100, Math.round(score)));
}

// =====================
// UTILISER LES VRAIES DONNEES : scores.geojson
// =====================

/**
 * Retourne la couleur selon le score (7 niveaux)
 * F: 0-9 (critique extrême)
 * E: 10-17 (critique)  
 * D: 18-25 (très fragile)
 * C: 26-40 (fragile)
 * B: 41-55 (moyen)
 * A: 56-75 (résilient)
 * A+: 76-100 (très résilient)
 */
function getCouleur(score) {
    if (score >= 76) return "#4C0035";    // A+ - Vert foncé (très résilient)
    if (score >= 56) return "#7D0033";    // A - Vert clair (résilient)
    if (score >= 41) return "#C74811";    // B - Or/Jaune (moyen)
    if (score >= 26) return "#dba339";    // C - Orange (fragile)
    if (score >= 18) return "#bbf534";    // D - Tomato/Rouge-orange (très fragile)
    if (score >= 10) return "#05852b";    // E - Crimson/Rouge (critique)
    return "#8B0000";                     // F - Rouge très foncé (critique extrême)
}

/** Convertit un score numérique en lettre F-A+ (7 niveaux) */
function getLettre(score) {
    if (score >= 76) return "F";
    if (score >= 56) return "E";
    if (score >= 41) return "D";
    if (score >= 26) return "C";
    if (score >= 18) return "B";
    if (score >= 10) return "A";
    return "F";
}

/** Retourne la description du classement */
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

function initMap() {
    map = new maplibregl.Map({
        container: 'map',
        style: './satellite-style.json',
        center: [-0.5792, 44.8378],
        zoom: 12
    });

    map.on('load', () => {
        console.log('✅ Carte chargée');
        
        // Charger le GeoJSON des carrés avec les VRAIS SCORES
        fetch('./scores.geojson')
            .then(response => {
                if (!response.ok) throw new Error(`Erreur: ${response.status}`);
                return response.json();
            })
            .then(data => {
                console.log(`✅ ${data.features.length} carrés chargés avec scores`);
                
                // Chaque feature a déjà score_particulier et score_elu
                map.addSource('kmeans', {
                    type: 'geojson',
                    data: data
                });

                // Couche de remplissage avec couleurs basées sur score_particulier
                map.addLayer({
                    id: 'kmeans-fill',
                    type: 'fill',
                    source: 'kmeans',
                    paint: {
                        'fill-color': [
                            'step',
                            ['get', 'score_particulier'],    // Utilise le score réel
                            '#8B0000',      // F: 0-9 (rouge très foncé)
                            10, '#05852b',  // E: 10-17 (rouge)
                            18, '#dba339',  // D: 18-25 (rouge-orange)
                            26, '#DF7103',  // C: 26-40 (orange)
                            41, '#C74811',  // B: 41-55 (or)
                            56, '#7D0033',  // A: 56-75 (vert clair)
                            76, '#4C0035'   // A+: 76-100 (vert foncé)
                        ],
                        'fill-opacity': 0.4
                    }
                });

                // Couche de contour (bordure des carrés)
                map.addLayer({
                    id: 'kmeans-outline',
                    type: 'line',
                    source: 'kmeans',
                    paint: {
                        'line-color': 'rgba(255, 255, 255, 0.3)',
                        'line-width': 0.5
                    }
                });
                
                // 🖱️ Interaction : clic sur un carré
                map.on('click', 'kmeans-fill', (e) => {
                    if (e.features.length > 0) {
                        const props = e.features[0].properties;
                        const cellId = props.cell_id;
                        
                        console.log(`🔍 Clic sur cellule : ${cellId}`);
                        
                        // Appel au backend pour avoir les détails dynamiques (sites à proximité, etc.)
                        fetch(`http://localhost:9456/api/cell/${cellId}`)
                            .then(resp => resp.json())
                            .then(data => {
                                displayLocationInfo({
                                    address: data.cluster.label || 'Zone résidentielle',
                                    resilience: Math.round(data.score_num),
                                    risk: data.explication,
                                    recommendations: data.recommendations.join(' | '),
                                    nearby_industrial_sites: data.nearby_industrial_sites,
                                    nearest_refuges: data.nearest_refuges
                                });
                            })
                            .catch(err => {
                                console.error('Erreur API détails cellule:', err);
                                // Fallback sur les données statiques si l'API échoue
                                displayLocationInfo({
                                    address: props.cluster_label || 'Zone résidentielle',
                                    resilience: Math.round(props.score_particulier),
                                    risk: props.explication_particulier,
                                    recommendations: props.conseils_particulier
                                });
                            });
                    }
                });
                
                // 👆 Retour visuel au survol
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
                console.error('❌ Erreur chargement GeoJSON:', err);
                alert('❌ Erreur: impossible de charger la carte. Vérifiez que scores.geojson existe.');
            });

        // Couche des points adresse (points verts)
        map.addSource('addresses', {
            type: 'geojson',
            data: addressesToGeoJSON(mockAddresses)
        });

        map.addLayer({
            id: 'addresses-layer',
            type: 'circle',
            source: 'addresses',
            paint: {
                'circle-radius': 8,
                'circle-color': '#00ff00',
                'circle-opacity': 0.8
            }
        });

        // Clic sur un point adresse
        map.on('click', 'addresses-layer', (e) => {
            if (e.features.length > 0) {
                const feature = e.features[0];
                const address = mockAddresses.find(addr => addr.address === feature.properties.address);
                if (address) {
                    displayLocationInfo(address);
                }
            }
        });

        // Curseur feedback
        map.on('mouseenter', 'addresses-layer', () => {
            map.getCanvas().style.cursor = 'pointer';
        });
        map.on('mouseleave', 'addresses-layer', () => {
            map.getCanvas().style.cursor = '';
        });
    });

    map.on('error', (e) => {
        console.error('❌ Erreur carte MapLibre:', e);
    });
}

// =====================
// CONVERSION GeoJSON
// =====================

/**
 * Convertit un tableau d'adresses en GeoJSON FeatureCollection
 * Utilisé pour afficher les points sur la carte
 */
function addressesToGeoJSON(addresses) {
    return {
        type: 'FeatureCollection',
        features: addresses.map(addr => ({
            type: 'Feature',
            geometry: {
                type: 'Point',
                coordinates: [addr.lng, addr.lat]
            },
            properties: {
                id: addr.id,
                address: addr.address,
                resilience: addr.resilience,
                risk: addr.risk,
                district: addr.district
            }
        }))
    };
}

function handleSearch(event) {
    event.preventDefault();
    
    const searchInput = document.getElementById('search-input');
    const searchTerm = searchInput.value.trim();
    
    if (!searchTerm) {
        alert('Veuillez entrer une adresse');
        return;
    }
    
    searchResults = mockAddresses.filter(addr => 
        addr.address.toLowerCase().includes(searchTerm.toLowerCase()) ||
        addr.district.toLowerCase().includes(searchTerm.toLowerCase())
    );
    
    if (searchResults.length > 0) {
        console.log(`✅ ${searchResults.length} résultat(s) local(aux) trouvé(s)`);
        afficherResultats(searchResults);
    } else {
        console.log('🔍 Recherche avec l\'API BAN...');
        rechercherAvecBAN(searchTerm).then(resultats => {
            if (resultats.length > 0) {
                searchResults = resultats;
                afficherResultats(resultats);
            }
        });
    }
}

/**
 * Recherche une adresse via l'API locale (qui interroge la BAN)
 * Retourne les données de résilience associées.
 */
async function rechercherAvecBAN(q) {
    try {
        console.log(`🌐 Recherche de l'adresse : ${q}`);
        const response = await fetch(`http://localhost:9456/api/address?q=${encodeURIComponent(q)}`);
        if (!response.ok) throw new Error("Adresse introuvable ou erreur API");
        
        const data = await response.json();
        
        // On formate l'objet pour qu'il soit compatible avec displayLocationInfo
        return [{
            address: data.address,
            resilience: Math.round(data.score_num),
            risk: data.explication,
            recommendations: data.recommendations.join(' | '),
            nearby_industrial_sites: data.nearby_industrial_sites,
            nearest_refuges: data.nearest_refuges,
            lat: data.coordinates.lat,
            lng: data.coordinates.lon
        }];
    } catch (error) {
        console.error("❌ Erreur de recherche :", error);
        alert("Impossible de trouver cette adresse ou le serveur est hors ligne.");
        return [];
    }
}


function afficherResultats(resultats) {
    if (resultats.length === 0) return;
    
    displayLocationInfo(resultats[0]);
    
    if (map) {
        map.flyTo({
            center: [resultats[0].lng, resultats[0].lat],
            zoom: 15,
            duration: 1000
        });
    }
}

// =====================
// AFFICHAGE DES INFOS - Popup améliorée
// =====================

function displayLocationInfo(location) {
    let title = location.address || 'Informations';
    let score = location.resilience || 50;
    let lettre = getLettre(score);
    let couleur = getCouleur(score);
    let description = getDescriptionClasse(lettre);
    
    let bodyHTML = `
        <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem;">
            <div style="
                width: 60px;
                height: 60px;
                border-radius: 50%;
                background-color: ${couleur};
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 2rem;
                font-weight: bold;
                color: white;
                text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
            ">
                ${lettre}
            </div>
            <div>
                <strong style="color: ${couleur}; font-size: 1.2rem;">${score}/100</strong><br>
                <small style="color: #aaa;">Classe: ${lettre} (${description})</small>
            </div>
        </div>
        
        <hr style="border: none; border-top: 1px solid #444; margin: 1rem 0;">
        
        <div style="background: rgba(255,255,255,0.05); padding: 0.75rem; border-radius: 4px; margin-bottom: 1rem;">
            <strong>📊 Diagnostic:</strong><br>
            <small style="color: #ddd; line-height: 1.6;">${location.risk || 'Non spécifié'}</small>
        </div>
    `;
    
    // Ajout des sites industriels proches
    if (location.nearby_industrial_sites && location.nearby_industrial_sites.length > 0) {
        bodyHTML += `
        <div style="background: rgba(199, 72, 17, 0.1); padding: 0.75rem; border-radius: 4px; border-left: 3px solid #C74811; margin-bottom: 1rem;">
            <strong style="color: #C74811;">🏭 Sites industriels / pollués:</strong><br>
            <small style="color: #ddd; line-height: 1.6;">
                ${location.nearby_industrial_sites.map(s => `• ${s.nom} (${s.distance_m}m)`).join('<br>')}
            </small>
        </div>
        `;
    }

    // Ajout des points de refuge proches
    if (location.nearest_refuges && location.nearest_refuges.length > 0) {
        bodyHTML += `
        <div style="background: rgba(5, 133, 43, 0.1); padding: 0.75rem; border-radius: 4px; border-left: 3px solid #05852b; margin-bottom: 1rem;">
            <strong style="color: #05852b;">🚒 Points de refuge (gymnases):</strong><br>
            <small style="color: #ddd; line-height: 1.6;">
                ${location.nearest_refuges.map(r => `• ${r.name} (${r.distance_m}m)`).join('<br>')}
            </small>
        </div>
        `;
    }
    
    if (location.recommendations) {
        bodyHTML += `
        <div style="background: rgba(76, 86, 175, 0.1); padding: 0.75rem; border-radius: 4px; border-left: 3px solid #4c74af;">
            <strong style="color: #4c5baf;">💡 Recommandations:</strong><br>
            <small style="color: #ddd; line-height: 1.6;">${location.recommendations.replace(/\|/g, '<br>• ')}</small>
        </div>
        `;
    }

    
    updatePopupContent({
        title: title,
        body: bodyHTML
    });
    openPopup();
}

// =====================
// POPUP - Fonctions
// =====================

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

// =====================
// INITIALISATION
// =====================

document.addEventListener('DOMContentLoaded', function() {
    initMap();
    
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            closePopup();
        }
    });
});
