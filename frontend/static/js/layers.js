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
    boundaries: L.layerGroup(),
    buildings: L.layerGroup(),
    coastline: L.layerGroup(),
    landslides: L.layerGroup(),
    cyclone: L.layerGroup(),
    affectedZones: L.layerGroup()
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
            if (document.getElementById('layer-disaster-zones')?.checked) {
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
                        const available = (props.capacity || 0) - (props.current_occupancy || 0);
                        const popupContent = `
                            <div class="popup-header">🏠 Emergency Shelter</div>
                            <div class="popup-content">
                                <p><strong>Name:</strong> ${props.name || 'Unknown'}</p>
                                <p><strong>Capacity:</strong> ${props.capacity || 'N/A'}</p>
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
                                <p><strong>Name:</strong> ${props.name || 'Unknown'}</p>
                                <p><strong>Type:</strong> ${props.facility_type || 'General'}</p>
                                <p><strong>Capacity:</strong> ${props.capacity || 'N/A'} beds</p>
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
                            <div class="popup-header">📍 ${props.name || 'Boundary'}</div>
                            <div class="popup-content">
                                <p><strong>Type:</strong> ${props.admin_type || 'Administrative'}</p>
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
 * Load buildings layer
 */
async function loadBuildings() {
    try {
        const response = await LayersAPI.getBuildings();

        if (response.status === 'success') {
            const geojson = response.data;

            layerGroups.buildings.clearLayers();

            L.geoJSON(geojson, {
                style: {
                    fillColor: '#8B4513',
                    fillOpacity: 0.5,
                    color: '#654321',
                    weight: 1
                },
                onEachFeature: (feature, layer) => {
                    if (feature.properties) {
                        const props = feature.properties;
                        const popupContent = `
                            <div class="popup-header">🏢 Building</div>
                            <div class="popup-content">
                                <p><strong>Type:</strong> ${props.building || 'Unknown'}</p>
                            </div>
                        `;
                        layer.bindPopup(popupContent);
                    }
                }
            }).addTo(layerGroups.buildings);

            if (document.getElementById('layer-buildings').checked) {
                layerGroups.buildings.addTo(map);
            }

            console.log('Buildings loaded');
        }
    } catch (error) {
        console.error('Error loading buildings:', error);
    }
}

/**
 * Load coastline layer
 */
async function loadCoastline() {
    try {
        const response = await LayersAPI.getCoastline();

        if (response.status === 'success') {
            const geojson = response.data;

            layerGroups.coastline.clearLayers();

            L.geoJSON(geojson, {
                style: {
                    color: '#1E90FF',
                    weight: 3,
                    opacity: 0.8
                },
                onEachFeature: (feature, layer) => {
                    layer.bindPopup('<div class="popup-header">🌊 Coastline</div>');
                }
            }).addTo(layerGroups.coastline);

            if (document.getElementById('layer-coastline').checked) {
                layerGroups.coastline.addTo(map);
            }

            console.log('Coastline loaded');
        }
    } catch (error) {
        console.error('Error loading coastline:', error);
    }
}

/**
 * Load landslides layer
 */
async function loadLandslides() {
    try {
        const response = await LayersAPI.getLandslides();

        if (response.status === 'success') {
            const geojson = response.data;

            layerGroups.landslides.clearLayers();

            L.geoJSON(geojson, {
                style: {
                    fillColor: '#D2691E',
                    fillOpacity: 0.4,
                    color: '#8B4513',
                    weight: 2
                },
                onEachFeature: (feature, layer) => {
                    if (feature.properties) {
                        const props = feature.properties;
                        const popupContent = `
                            <div class="popup-header">⚠️ Landslide Zone</div>
                            <div class="popup-content">
                                <p><strong>District:</strong> ${props.district || 'Unknown'}</p>
                                <p><strong>Severity:</strong> ${props.severity || 'High'}</p>
                                <p><strong>Type:</strong> Landslide Hazard</p>
                            </div>
                        `;
                        layer.bindPopup(popupContent);
                    }
                }
            }).addTo(layerGroups.landslides);

            if (document.getElementById('layer-landslides').checked) {
                layerGroups.landslides.addTo(map);
            }

            console.log('Landslides loaded');
        }
    } catch (error) {
        console.error('Error loading landslides:', error);
    }
}

/**
 * Load cyclone layer
 */
async function loadCyclone() {
    try {
        const response = await LayersAPI.getCyclone();

        if (response.status === 'success') {
            const geojson = response.data;

            layerGroups.cyclone.clearLayers();

            L.geoJSON(geojson, {
                style: {
                    fillColor: '#4169E1',
                    fillOpacity: 0.3,
                    color: '#0000CD',
                    weight: 2
                },
                onEachFeature: (feature, layer) => {
                    if (feature.properties) {
                        const props = feature.properties;
                        const popupContent = `
                            <div class="popup-header">🌀 Cyclone Zone</div>
                            <div class="popup-content">
                                <p><strong>Severity:</strong> ${props.severity || 'High'}</p>
                                <p><strong>Type:</strong> Cyclone Impact Zone</p>
                            </div>
                        `;
                        layer.bindPopup(popupContent);
                    }
                }
            }).addTo(layerGroups.cyclone);

            if (document.getElementById('layer-cyclone').checked) {
                layerGroups.cyclone.addTo(map);
            }

            console.log('Cyclone zones loaded');
        }
    } catch (error) {
        console.error('Error loading cyclone:', error);
    }
}

/**
 * Load affected zones layer
 */
async function loadAffectedZones() {
    try {
        const response = await LayersAPI.getAffectedZones();

        if (response.status === 'success') {
            const geojson = response.data;

            layerGroups.affectedZones.clearLayers();

            L.geoJSON(geojson, {
                style: (feature) => {
                    const disasterType = feature.properties?.disaster_type;
                    let color = '#ff0000';

                    if (disasterType === 'landslide') color = '#D2691E';
                    else if (disasterType === 'cyclone') color = '#4169E1';
                    else if (disasterType === 'flood') color = '#0066ff';

                    return {
                        fillColor: color,
                        fillOpacity: 0.35,
                        color: color,
                        weight: 2
                    };
                },
                onEachFeature: (feature, layer) => {
                    if (feature.properties) {
                        const props = feature.properties;
                        const popupContent = `
                            <div class="popup-header">⚠️ Affected Zone</div>
                            <div class="popup-content">
                                <p><strong>Type:</strong> ${props.disaster_type || 'Unknown'}</p>
                                <p><strong>Severity:</strong> ${props.severity || 'Unknown'}</p>
                            </div>
                        `;
                        layer.bindPopup(popupContent);
                    }
                }
            }).addTo(layerGroups.affectedZones);

            if (document.getElementById('layer-affected-zones').checked) {
                layerGroups.affectedZones.addTo(map);
            }

            console.log('Affected zones loaded');
        }
    } catch (error) {
        console.error('Error loading affected zones:', error);
    }
}

/**
 * Initialize layer control checkboxes
 */
function initLayerControls() {
    // Boundaries toggle
    document.getElementById('layer-boundaries').addEventListener('change', async (e) => {
        if (e.target.checked) {
            await loadBoundaries();
        } else {
            map.removeLayer(layerGroups.boundaries);
        }
    });

    // Buildings toggle
    document.getElementById('layer-buildings').addEventListener('change', async (e) => {
        if (e.target.checked) {
            await loadBuildings();
        } else {
            map.removeLayer(layerGroups.buildings);
        }
    });

    // Coastline toggle
    document.getElementById('layer-coastline').addEventListener('change', async (e) => {
        if (e.target.checked) {
            await loadCoastline();
        } else {
            map.removeLayer(layerGroups.coastline);
        }
    });

    // Landslides toggle
    document.getElementById('layer-landslides').addEventListener('change', async (e) => {
        if (e.target.checked) {
            await loadLandslides();
        } else {
            map.removeLayer(layerGroups.landslides);
        }
    });

    // Cyclone toggle
    document.getElementById('layer-cyclone').addEventListener('change', async (e) => {
        if (e.target.checked) {
            await loadCyclone();
        } else {
            map.removeLayer(layerGroups.cyclone);
        }
    });

    // Affected zones toggle
    document.getElementById('layer-affected-zones').addEventListener('change', async (e) => {
        if (e.target.checked) {
            await loadAffectedZones();
        } else {
            map.removeLayer(layerGroups.affectedZones);
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
        loadBuildings,
        loadCoastline,
        loadLandslides,
        loadCyclone,
        loadAffectedZones,
        initLayerControls
    };
}
