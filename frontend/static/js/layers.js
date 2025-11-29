// /**
//  * Map Layers Module
//  * ==================
//  * Handles loading and toggling of map layers.
//  */

// // Layer groups
// const layerGroups = {
//     disasterZones: L.layerGroup(),
//     shelters: L.layerGroup(),
//     hospitals: L.layerGroup(),
//     roads: L.layerGroup(),
//     boundaries: L.layerGroup()
// };

// /**
//  * Load disaster zones layer
//  */
// async function loadDisasterZones() {
//     try {
//         const response = await DisasterAPI.getDisasterZones();

//         if (response.status === 'success') {
//             const geojson = response.data;

//             // Clear existing layer
//             layerGroups.disasterZones.clearLayers();

//             // Add GeoJSON to layer
//             L.geoJSON(geojson, {
//                 style: {
//                     fillColor: '#ff0000',
//                     fillOpacity: 0.3,
//                     color: '#ff0000',
//                     weight: 2
//                 },
//                 onEachFeature: (feature, layer) => {
//                     if (feature.properties) {
//                         const props = feature.properties;
//                         const popupContent = `
//                             <div class="popup-header">⚠️ Disaster Zone</div>
//                             <div class="popup-content">
//                                 <p><strong>Name:</strong> ${props.name || 'Unknown'}</p>
//                                 <p><strong>Severity:</strong> ${props.severity || 'Unknown'}</p>
//                                 <p><strong>Status:</strong> ${props.status || 'Unknown'}</p>
//                                 ${props.affected_population ? `<p><strong>Affected:</strong> ${props.affected_population.toLocaleString()} people</p>` : ''}
//                             </div>
//                         `;
//                         layer.bindPopup(popupContent);
//                     }
//                 }
//             }).addTo(layerGroups.disasterZones);

//             // Add to map if checkbox is checked
//             if (document.getElementById('layer-disaster-zones').checked) {
//                 layerGroups.disasterZones.addTo(map);
//             }

//             console.log('Disaster zones loaded');
//         }
//     } catch (error) {
//         console.error('Error loading disaster zones:', error);
//     }
// }

// /**
//  * Load shelters layer
//  */
// async function loadShelters() {
//     try {
//         const response = await SheltersAPI.getAll();

//         if (response.status === 'success') {
//             const geojson = response.data;

//             // Clear existing layer
//             layerGroups.shelters.clearLayers();

//             // Custom shelter icon
//             const shelterIcon = L.divIcon({
//                 className: 'shelter-marker',
//                 html: '🏠',
//                 iconSize: [25, 25]
//             });

//             // Add GeoJSON to layer
//             L.geoJSON(geojson, {
//                 pointToLayer: (feature, latlng) => {
//                     return L.marker(latlng, { icon: shelterIcon });
//                 },
//                 onEachFeature: (feature, layer) => {
//                     if (feature.properties) {
//                         const props = feature.properties;
//                         const available = props.capacity - props.current_occupancy;
//                         const popupContent = `
//                             <div class="popup-header">🏠 Emergency Shelter</div>
//                             <div class="popup-content">
//                                 <p><strong>Name:</strong> ${props.name}</p>
//                                 <p><strong>Capacity:</strong> ${props.capacity}</p>
//                                 <p><strong>Available:</strong> ${available} spaces</p>
//                                 <p><strong>Facilities:</strong></p>
//                                 <ul style="margin: 5px 0; padding-left: 20px;">
//                                     ${props.has_food ? '<li>Food available</li>' : ''}
//                                     ${props.has_water ? '<li>Water available</li>' : ''}
//                                     ${props.has_medical ? '<li>Medical aid</li>' : ''}
//                                 </ul>
//                             </div>
//                         `;
//                         layer.bindPopup(popupContent);
//                     }
//                 }
//             }).addTo(layerGroups.shelters);

//             // Add to map if checkbox is checked
//             if (document.getElementById('layer-shelters').checked) {
//                 layerGroups.shelters.addTo(map);
//             }

//             console.log('Shelters loaded');
//         }
//     } catch (error) {
//         console.error('Error loading shelters:', error);
//     }
// }

// /**
//  * Load hospitals layer
//  */
// async function loadHospitals() {
//     try {
//         const response = await SheltersAPI.getAllHospitals();

//         if (response.status === 'success') {
//             const geojson = response.data;

//             // Clear existing layer
//             layerGroups.hospitals.clearLayers();

//             // Custom hospital icon
//             const hospitalIcon = L.divIcon({
//                 className: 'hospital-marker',
//                 html: '🏥',
//                 iconSize: [25, 25]
//             });

//             // Add GeoJSON to layer
//             L.geoJSON(geojson, {
//                 pointToLayer: (feature, latlng) => {
//                     return L.marker(latlng, { icon: hospitalIcon });
//                 },
//                 onEachFeature: (feature, layer) => {
//                     if (feature.properties) {
//                         const props = feature.properties;
//                         const popupContent = `
//                             <div class="popup-header">🏥 Hospital</div>
//                             <div class="popup-content">
//                                 <p><strong>Name:</strong> ${props.name}</p>
//                                 <p><strong>Type:</strong> ${props.facility_type || 'General'}</p>
//                                 <p><strong>Capacity:</strong> ${props.capacity} beds</p>
//                                 <p><strong>Emergency Ready:</strong> ${props.emergency_ready ? 'Yes' : 'No'}</p>
//                             </div>
//                         `;
//                         layer.bindPopup(popupContent);
//                     }
//                 }
//             }).addTo(layerGroups.hospitals);

//             // Add to map if checkbox is checked
//             if (document.getElementById('layer-hospitals').checked) {
//                 layerGroups.hospitals.addTo(map);
//             }

//             console.log('Hospitals loaded');
//         }
//     } catch (error) {
//         console.error('Error loading hospitals:', error);
//     }
// }

// /**
//  * Load roads layer
//  */
// async function loadRoads() {
//     try {
//         // Get current map bounds
//         const bounds = map.getBounds();
//         const bbox = [
//             bounds.getWest(),
//             bounds.getSouth(),
//             bounds.getEast(),
//             bounds.getNorth()
//         ];

//         const response = await LayersAPI.getRoads(bbox);

//         if (response.status === 'success') {
//             const geojson = response.data;

//             // Clear existing layer
//             layerGroups.roads.clearLayers();

//             // Add GeoJSON to layer
//             L.geoJSON(geojson, {
//                 style: (feature) => {
//                     const isBlocked = feature.properties?.is_blocked;
//                     return {
//                         color: isBlocked ? '#ff0000' : '#333333',
//                         weight: isBlocked ? 3 : 2,
//                         opacity: 0.7
//                     };
//                 },
//                 onEachFeature: (feature, layer) => {
//                     if (feature.properties) {
//                         const props = feature.properties;
//                         const popupContent = `
//                             <div class="popup-header">🛣️ Road</div>
//                             <div class="popup-content">
//                                 <p><strong>Name:</strong> ${props.name || 'Unnamed'}</p>
//                                 <p><strong>Type:</strong> ${props.road_type || 'Unknown'}</p>
//                                 <p><strong>Condition:</strong> ${props.condition || 'Unknown'}</p>
//                                 <p><strong>Status:</strong> ${props.is_blocked ? '🚫 Blocked' : '✅ Open'}</p>
//                             </div>
//                         `;
//                         layer.bindPopup(popupContent);
//                     }
//                 }
//             }).addTo(layerGroups.roads);

//             // Add to map if checkbox is checked
//             if (document.getElementById('layer-roads').checked) {
//                 layerGroups.roads.addTo(map);
//             }

//             console.log('Roads loaded');
//         }
//     } catch (error) {
//         console.error('Error loading roads:', error);
//     }
// }

// /**
//  * Load administrative boundaries layer
//  */
// async function loadBoundaries() {
//     try {
//         const response = await LayersAPI.getBoundaries();

//         if (response.status === 'success') {
//             const geojson = response.data;

//             // Clear existing layer
//             layerGroups.boundaries.clearLayers();

//             // Add GeoJSON to layer
//             L.geoJSON(geojson, {
//                 style: {
//                     fillColor: '#cccccc',
//                     fillOpacity: 0.1,
//                     color: '#666666',
//                     weight: 1
//                 },
//                 onEachFeature: (feature, layer) => {
//                     if (feature.properties) {
//                         const props = feature.properties;
//                         const popupContent = `
//                             <div class="popup-header">📍 ${props.name}</div>
//                             <div class="popup-content">
//                                 <p><strong>Type:</strong> ${props.admin_type || 'Unknown'}</p>
//                                 ${props.population ? `<p><strong>Population:</strong> ${props.population.toLocaleString()}</p>` : ''}
//                                 ${props.area_sqkm ? `<p><strong>Area:</strong> ${props.area_sqkm.toFixed(2)} km²</p>` : ''}
//                             </div>
//                         `;
//                         layer.bindPopup(popupContent);
//                     }
//                 }
//             }).addTo(layerGroups.boundaries);

//             // Add to map if checkbox is checked
//             if (document.getElementById('layer-boundaries').checked) {
//                 layerGroups.boundaries.addTo(map);
//             }

//             console.log('Boundaries loaded');
//         }
//     } catch (error) {
//         console.error('Error loading boundaries:', error);
//     }
// }

// /**
//  * Initialize layer control checkboxes
//  */
// function initLayerControls() {
//     // Disaster zones toggle
//     document.getElementById('layer-disaster-zones').addEventListener('change', (e) => {
//         if (e.target.checked) {
//             layerGroups.disasterZones.addTo(map);
//         } else {
//             map.removeLayer(layerGroups.disasterZones);
//         }
//     });

//     // Shelters toggle
//     document.getElementById('layer-shelters').addEventListener('change', (e) => {
//         if (e.target.checked) {
//             layerGroups.shelters.addTo(map);
//         } else {
//             map.removeLayer(layerGroups.shelters);
//         }
//     });

//     // Hospitals toggle
//     document.getElementById('layer-hospitals').addEventListener('change', (e) => {
//         if (e.target.checked) {
//             layerGroups.hospitals.addTo(map);
//         } else {
//             map.removeLayer(layerGroups.hospitals);
//         }
//     });

//     // Roads toggle
//     document.getElementById('layer-roads').addEventListener('change', async (e) => {
//         if (e.target.checked) {
//             await loadRoads();
//         } else {
//             map.removeLayer(layerGroups.roads);
//         }
//     });

//     // Boundaries toggle
//     document.getElementById('layer-boundaries').addEventListener('change', async (e) => {
//         if (e.target.checked) {
//             await loadBoundaries();
//         } else {
//             map.removeLayer(layerGroups.boundaries);
//         }
//     });

//     console.log('Layer controls initialized');
// }

// // Export for use in other modules
// if (typeof module !== 'undefined' && module.exports) {
//     module.exports = {
//         loadDisasterZones,
//         loadShelters,
//         loadHospitals,
//         loadRoads,
//         loadBoundaries,
//         initLayerControls
//     };
// }
/***********************************************
 * FIXED LAYERS.JS (FINAL)
 ***********************************************/

let LAYERS = {
    hospitals: null,
    shelters: null,
    roads: null,
    boundaries: null,

    cycloneLines: null,
    cyclonePoints: null,

    landslides: []
};

/* ------------------------------
   Utility: Validate GeoJSON 
--------------------------------*/
function isValidGeoJSON(obj) {
    return obj &&
        (obj.type === "FeatureCollection" ||
         obj.type === "Feature" ||
         obj.type === "GeometryCollection");
}

/* ------------------------------
    Load Hospitals
--------------------------------*/
async function loadHospitals() {
    const response = await API.getHospitals();
    const data = response?.data;

    if (!isValidGeoJSON(data)) return console.error("Invalid Hospital GeoJSON");

    LAYERS.hospitals = L.geoJSON(data, {
        pointToLayer: (f, ll) => L.circleMarker(ll, { radius: 4, color: "green" })
    });

    if (document.getElementById("layer-hospitals").checked)
        LAYERS.hospitals.addTo(map);
}

/* ------------------------------
    Load Shelters
--------------------------------*/
async function loadShelters() {
    const response = await API.getShelters();
    const data = response?.data;

    if (!isValidGeoJSON(data)) return console.error("Invalid Shelter GeoJSON");

    LAYERS.shelters = L.geoJSON(data, {
        pointToLayer: (f, ll) => L.circleMarker(ll, { radius: 4, color: "blue" })
    });

    if (document.getElementById("layer-shelters").checked)
        LAYERS.shelters.addTo(map);
}

/* ------------------------------
    Load Roads (optional)
--------------------------------*/
async function loadRoads() {
    const response = await API.getRoads();
    const data = response?.data;

    if (!isValidGeoJSON(data)) return console.error("Invalid Roads GeoJSON");

    LAYERS.roads = L.geoJSON(data, {
        style: { color: "gray", weight: 1 }
    });

    if (document.getElementById("layer-roads").checked)
        LAYERS.roads.addTo(map);
}

/* ------------------------------
    Load Boundaries
--------------------------------*/
async function loadBoundaries() {
    const response = await API.getBoundaries();
    const data = response?.data;

    if (!isValidGeoJSON(data)) return console.error("Invalid Boundaries GeoJSON");

    LAYERS.boundaries = L.geoJSON(data, {
        style: { color: "#444", weight: 1, fillOpacity: 0.1 }
    });

    if (document.getElementById("layer-boundaries").checked)
        LAYERS.boundaries.addTo(map);
}

/* ------------------------------
    Load Cyclones (lines + points)
--------------------------------*/
async function loadCyclones() {
    const data = await API.getCyclones();

    if (data.lines && isValidGeoJSON(data.lines)) {
        LAYERS.cycloneLines = L.geoJSON(data.lines, {
            style: { color: "red", weight: 2 }
        });

        if (document.getElementById("layer-disaster-zones").checked)
            LAYERS.cycloneLines.addTo(map);
    }

    if (data.points && isValidGeoJSON(data.points)) {
        LAYERS.cyclonePoints = L.geoJSON(data.points, {
            pointToLayer: (f, ll) => L.circleMarker(ll, { radius: 3, color: "orange" })
        });

        if (document.getElementById("layer-disaster-zones").checked)
            LAYERS.cyclonePoints.addTo(map);
    }
}

/* ------------------------------
    Load Landslides (multiple files)
--------------------------------*/
async function loadLandslides() {
    const list = await API.getLandslides();   // array of FeatureCollection objects

    if (!Array.isArray(list)) return console.error("Invalid Landslide Array");

    for (const ls of list) {
        if (!isValidGeoJSON(ls)) continue;

        const layer = L.geoJSON(ls, {
            style: { color: "#660000", weight: 2 }
        });

        LAYERS.landslides.push(layer);

        if (document.getElementById("layer-disaster-zones").checked)
            layer.addTo(map);
    }
}

/* ------------------------------
    Checkbox Controls
--------------------------------*/
function initLayerControls() {
    const pairs = {
        "layer-hospitals": "hospitals",
        "layer-shelters": "shelters",
        "layer-roads": "roads",
        "layer-boundaries": "boundaries"
    };

    for (let id in pairs) {
        document.getElementById(id).addEventListener("change", e => {
            const layer = LAYERS[pairs[id]];
            if (!layer) return;

            e.target.checked ? layer.addTo(map) : map.removeLayer(layer);
        });
    }

    // Disaster zones combine all hazards
    document.getElementById("layer-disaster-zones").addEventListener("change", e => {
        if (e.target.checked) {
            if (LAYERS.cycloneLines) LAYERS.cycloneLines.addTo(map);
            if (LAYERS.cyclonePoints) LAYERS.cyclonePoints.addTo(map);
            for (const ls of LAYERS.landslides) ls.addTo(map);
        } else {
            if (LAYERS.cycloneLines) map.removeLayer(LAYERS.cycloneLines);
            if (LAYERS.cyclonePoints) map.removeLayer(LAYERS.cyclonePoints);
            for (const ls of LAYERS.landslides) map.removeLayer(ls);
        }
    });
}

/* ------------------------------
    Load everything at startup
--------------------------------*/
async function loadAllLayers() {
    await loadHospitals();
    await loadShelters();
    await loadBoundaries();
    await loadCyclones();
    await loadLandslides();

    document.getElementById("loading-overlay").style.display = "none";
}

