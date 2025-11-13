/**
 * Map Layers Module
 * ==================
 * Handles loading and toggling of map layers.
 */

// Layer groups
const layerGroups = {
    disasterZones: L.layerGroup(),
    shelters: L.layerGroup(),
    hospitals: L.layerGroup(),
    roads: L.layerGroup(),
    boundaries: L.layerGroup()
};

/**
 * Load disaster zones layer
 */
async function loadDisasterZones() {
    try {
        const response = await DisasterAPI.getDisasterZones();

        if (response.status === 'success') {
            const geojson = response.data;

            // Clear existing layer
            layerGroups.disasterZones.clearLayers();

            // Add GeoJSON to layer
            L.geoJSON(geojson, {
                style: {
                    fillColor: '#ff0000',
                    fillOpacity: 0.3,
                    color: '#ff0000',
                    weight: 2
                },
                onEachFeature: (feature, layer) => {
                    if (feature.properties) {
                        const props = feature.properties;
                        const popupContent = `
                            <div class="popup-header">⚠️ Disaster Zone</div>
                            <div class="popup-content">
                                <p><strong>Name:</strong> ${props.name || 'Unknown'}</p>
                                <p><strong>Severity:</strong> ${props.severity || 'Unknown'}</p>
                                <p><strong>Status:</strong> ${props.status || 'Unknown'}</p>
                                ${props.affected_population ? `<p><strong>Affected:</strong> ${props.affected_population.toLocaleString()} people</p>` : ''}
                            </div>
                        `;
                        layer.bindPopup(popupContent);
                    }
                }
            }).addTo(layerGroups.disasterZones);

            // Add to map if checkbox is checked
            if (document.getElementById('layer-disaster-zones').checked) {
                layerGroups.disasterZones.addTo(map);
            }

            console.log('Disaster zones loaded');
        }
    } catch (error) {
        console.error('Error loading disaster zones:', error);
    }
}

/**
 * Load shelters layer
 */
async function loadShelters() {
    try {
        const response = await SheltersAPI.getAll();

        if (response.status === 'success') {
            const geojson = response.data;

            // Clear existing layer
            layerGroups.shelters.clearLayers();

            // Custom shelter icon
            const shelterIcon = L.divIcon({
                className: 'shelter-marker',
                html: '🏠',
                iconSize: [25, 25]
            });

            // Add GeoJSON to layer
            L.geoJSON(geojson, {
                pointToLayer: (feature, latlng) => {
                    return L.marker(latlng, { icon: shelterIcon });
                },
                onEachFeature: (feature, layer) => {
                    if (feature.properties) {
                        const props = feature.properties;
                        const available = props.capacity - props.current_occupancy;
                        const popupContent = `
                            <div class="popup-header">🏠 Emergency Shelter</div>
                            <div class="popup-content">
                                <p><strong>Name:</strong> ${props.name}</p>
                                <p><strong>Capacity:</strong> ${props.capacity}</p>
                                <p><strong>Available:</strong> ${available} spaces</p>
                                <p><strong>Facilities:</strong></p>
                                <ul style="margin: 5px 0; padding-left: 20px;">
                                    ${props.has_food ? '<li>Food available</li>' : ''}
                                    ${props.has_water ? '<li>Water available</li>' : ''}
                                    ${props.has_medical ? '<li>Medical aid</li>' : ''}
                                </ul>
                            </div>
                        `;
                        layer.bindPopup(popupContent);
                    }
                }
            }).addTo(layerGroups.shelters);

            // Add to map if checkbox is checked
            if (document.getElementById('layer-shelters').checked) {
                layerGroups.shelters.addTo(map);
            }

            console.log('Shelters loaded');
        }
    } catch (error) {
        console.error('Error loading shelters:', error);
    }
}

/**
 * Load hospitals layer
 */
async function loadHospitals() {
    try {
        const response = await SheltersAPI.getAllHospitals();

        if (response.status === 'success') {
            const geojson = response.data;

            // Clear existing layer
            layerGroups.hospitals.clearLayers();

            // Custom hospital icon
            const hospitalIcon = L.divIcon({
                className: 'hospital-marker',
                html: '🏥',
                iconSize: [25, 25]
            });

            // Add GeoJSON to layer
            L.geoJSON(geojson, {
                pointToLayer: (feature, latlng) => {
                    return L.marker(latlng, { icon: hospitalIcon });
                },
                onEachFeature: (feature, layer) => {
                    if (feature.properties) {
                        const props = feature.properties;
                        const popupContent = `
                            <div class="popup-header">🏥 Hospital</div>
                            <div class="popup-content">
                                <p><strong>Name:</strong> ${props.name}</p>
                                <p><strong>Type:</strong> ${props.facility_type || 'General'}</p>
                                <p><strong>Capacity:</strong> ${props.capacity} beds</p>
                                <p><strong>Emergency Ready:</strong> ${props.emergency_ready ? 'Yes' : 'No'}</p>
                            </div>
                        `;
                        layer.bindPopup(popupContent);
                    }
                }
            }).addTo(layerGroups.hospitals);

            // Add to map if checkbox is checked
            if (document.getElementById('layer-hospitals').checked) {
                layerGroups.hospitals.addTo(map);
            }

            console.log('Hospitals loaded');
        }
    } catch (error) {
        console.error('Error loading hospitals:', error);
    }
}

/**
 * Load roads layer
 */
async function loadRoads() {
    try {
        // Get current map bounds
        const bounds = map.getBounds();
        const bbox = [
            bounds.getWest(),
            bounds.getSouth(),
            bounds.getEast(),
            bounds.getNorth()
        ];

        const response = await LayersAPI.getRoads(bbox);

        if (response.status === 'success') {
            const geojson = response.data;

            // Clear existing layer
            layerGroups.roads.clearLayers();

            // Add GeoJSON to layer
            L.geoJSON(geojson, {
                style: (feature) => {
                    const isBlocked = feature.properties?.is_blocked;
                    return {
                        color: isBlocked ? '#ff0000' : '#333333',
                        weight: isBlocked ? 3 : 2,
                        opacity: 0.7
                    };
                },
                onEachFeature: (feature, layer) => {
                    if (feature.properties) {
                        const props = feature.properties;
                        const popupContent = `
                            <div class="popup-header">🛣️ Road</div>
                            <div class="popup-content">
                                <p><strong>Name:</strong> ${props.name || 'Unnamed'}</p>
                                <p><strong>Type:</strong> ${props.road_type || 'Unknown'}</p>
                                <p><strong>Condition:</strong> ${props.condition || 'Unknown'}</p>
                                <p><strong>Status:</strong> ${props.is_blocked ? '🚫 Blocked' : '✅ Open'}</p>
                            </div>
                        `;
                        layer.bindPopup(popupContent);
                    }
                }
            }).addTo(layerGroups.roads);

            // Add to map if checkbox is checked
            if (document.getElementById('layer-roads').checked) {
                layerGroups.roads.addTo(map);
            }

            console.log('Roads loaded');
        }
    } catch (error) {
        console.error('Error loading roads:', error);
    }
}

/**
 * Load administrative boundaries layer
 */
async function loadBoundaries() {
    try {
        const response = await LayersAPI.getBoundaries();

        if (response.status === 'success') {
            const geojson = response.data;

            // Clear existing layer
            layerGroups.boundaries.clearLayers();

            // Add GeoJSON to layer
            L.geoJSON(geojson, {
                style: {
                    fillColor: '#cccccc',
                    fillOpacity: 0.1,
                    color: '#666666',
                    weight: 1
                },
                onEachFeature: (feature, layer) => {
                    if (feature.properties) {
                        const props = feature.properties;
                        const popupContent = `
                            <div class="popup-header">📍 ${props.name}</div>
                            <div class="popup-content">
                                <p><strong>Type:</strong> ${props.admin_type || 'Unknown'}</p>
                                ${props.population ? `<p><strong>Population:</strong> ${props.population.toLocaleString()}</p>` : ''}
                                ${props.area_sqkm ? `<p><strong>Area:</strong> ${props.area_sqkm.toFixed(2)} km²</p>` : ''}
                            </div>
                        `;
                        layer.bindPopup(popupContent);
                    }
                }
            }).addTo(layerGroups.boundaries);

            // Add to map if checkbox is checked
            if (document.getElementById('layer-boundaries').checked) {
                layerGroups.boundaries.addTo(map);
            }

            console.log('Boundaries loaded');
        }
    } catch (error) {
        console.error('Error loading boundaries:', error);
    }
}

/**
 * Initialize layer control checkboxes
 */
function initLayerControls() {
    // Disaster zones toggle
    document.getElementById('layer-disaster-zones').addEventListener('change', (e) => {
        if (e.target.checked) {
            layerGroups.disasterZones.addTo(map);
        } else {
            map.removeLayer(layerGroups.disasterZones);
        }
    });

    // Shelters toggle
    document.getElementById('layer-shelters').addEventListener('change', (e) => {
        if (e.target.checked) {
            layerGroups.shelters.addTo(map);
        } else {
            map.removeLayer(layerGroups.shelters);
        }
    });

    // Hospitals toggle
    document.getElementById('layer-hospitals').addEventListener('change', (e) => {
        if (e.target.checked) {
            layerGroups.hospitals.addTo(map);
        } else {
            map.removeLayer(layerGroups.hospitals);
        }
    });

    // Roads toggle
    document.getElementById('layer-roads').addEventListener('change', async (e) => {
        if (e.target.checked) {
            await loadRoads();
        } else {
            map.removeLayer(layerGroups.roads);
        }
    });

    // Boundaries toggle
    document.getElementById('layer-boundaries').addEventListener('change', async (e) => {
        if (e.target.checked) {
            await loadBoundaries();
        } else {
            map.removeLayer(layerGroups.boundaries);
        }
    });

    console.log('Layer controls initialized');
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        loadDisasterZones,
        loadShelters,
        loadHospitals,
        loadRoads,
        loadBoundaries,
        initLayerControls
    };
}
