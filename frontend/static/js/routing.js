/**
 * Routing Module
 * ==============
 * Handles route calculation and visualization.
 */

let routeLayer = null;
let startMarker = null;
let endMarker = null;
let startCoords = null;
let endCoords = null;

/**
 * Initialize routing controls
 */
function initRoutingControls() {
    // Click on map to set start/end points
    map.on('click', (e) => {
        const clickMode = getRouteClickMode();

        if (clickMode === 'start') {
            setRouteStart(e.latlng.lat, e.latlng.lng);
        } else if (clickMode === 'end') {
            setRouteEnd(e.latlng.lat, e.latlng.lng);
        }
    });

    // Calculate route button
    document.getElementById('calculate-route').addEventListener('click', calculateRoute);

    // Clear route button
    document.getElementById('clear-route').addEventListener('click', clearRoute);

    // Allow clicking on map to set route points
    document.getElementById('route-start').addEventListener('focus', () => {
        document.body.setAttribute('data-route-mode', 'start');
        document.getElementById('map').style.cursor = 'crosshair';
    });

    document.getElementById('route-end').addEventListener('focus', () => {
        document.body.setAttribute('data-route-mode', 'end');
        document.getElementById('map').style.cursor = 'crosshair';
    });

    document.getElementById('route-start').addEventListener('blur', () => {
        document.body.removeAttribute('data-route-mode');
        document.getElementById('map').style.cursor = '';
    });

    document.getElementById('route-end').addEventListener('blur', () => {
        document.body.removeAttribute('data-route-mode');
        document.getElementById('map').style.cursor = '';
    });

    console.log('Routing controls initialized');
}

/**
 * Get current route click mode (start or end)
 */
function getRouteClickMode() {
    return document.body.getAttribute('data-route-mode');
}

/**
 * Set route start point
 */
function setRouteStart(lat, lon) {
    startCoords = { lat, lon };

    // Remove existing marker
    if (startMarker) {
        map.removeLayer(startMarker);
    }

    // Add new marker
    startMarker = L.marker([lat, lon], {
        icon: L.divIcon({
            className: 'route-start-marker',
            html: '🔵',
            iconSize: [25, 25]
        })
    }).addTo(map);

    startMarker.bindPopup('<b>Start</b>').openPopup();

    // Update input field with coordinates
    document.getElementById('route-start').value = `${lat.toFixed(5)}, ${lon.toFixed(5)}`;

    console.log('Route start set:', startCoords);
}

/**
 * Set route end point
 */
function setRouteEnd(lat, lon) {
    endCoords = { lat, lon };

    // Remove existing marker
    if (endMarker) {
        map.removeLayer(endMarker);
    }

    // Add new marker
    endMarker = L.marker([lat, lon], {
        icon: L.divIcon({
            className: 'route-end-marker',
            html: '🔴',
            iconSize: [25, 25]
        })
    }).addTo(map);

    endMarker.bindPopup('<b>Destination</b>').openPopup();

    // Update input field with coordinates
    document.getElementById('route-end').value = `${lat.toFixed(5)}, ${lon.toFixed(5)}`;

    console.log('Route end set:', endCoords);
}

/**
 * Parse coordinates from input field
 */
function parseCoordinates(input) {
    // Try to parse "lat, lon" format
    const parts = input.split(',').map(s => s.trim());

    if (parts.length === 2) {
        const lat = parseFloat(parts[0]);
        const lon = parseFloat(parts[1]);

        if (!isNaN(lat) && !isNaN(lon)) {
            return { lat, lon };
        }
    }

    return null;
}

/**
 * Calculate and display safe route
 */
async function calculateRoute() {
    try {
        // Get start and end points
        const startInput = document.getElementById('route-start').value;
        const endInput = document.getElementById('route-end').value;

        // Try to use coordinates if already set
        let start = startCoords;
        let end = endCoords;

        // If not set, try to parse from input
        if (!start) {
            start = parseCoordinates(startInput);
            if (!start) {
                alert('Please set a valid start point (click on map or enter coordinates)');
                return;
            }
        }

        if (!end) {
            end = parseCoordinates(endInput);
            if (!end) {
                alert('Please set a valid end point (click on map or enter coordinates)');
                return;
            }
        }

        showLoading(true);

        // Calculate route using API
        const response = await RoutesAPI.calculateSafeRoute(
            start.lat,
            start.lon,
            end.lat,
            end.lon
        );

        if (response.status === 'success') {
            displayRoute(response.data);
        } else {
            alert('Error calculating route. Please try again.');
        }

    } catch (error) {
        console.error('Route calculation error:', error);
        alert('Failed to calculate route. Please check your connection and try again.');
    } finally {
        showLoading(false);
    }
}

/**
 * Display route on map
 */
function displayRoute(routeData) {
    // Clear existing route
    if (routeLayer) {
        map.removeLayer(routeLayer);
    }

    // Create route polyline
    const coordinates = routeData.geometry.coordinates.map(coord => [coord[1], coord[0]]);

    routeLayer = L.polyline(coordinates, {
        color: '#0066ff',
        weight: 5,
        opacity: 0.7
    }).addTo(map);

    // Fit map to route bounds
    map.fitBounds(routeLayer.getBounds(), { padding: [50, 50] });

    // Show route info
    document.getElementById('route-info').style.display = 'block';
    document.getElementById('route-distance').textContent = routeData.total_distance_km;
    document.getElementById('route-safety').textContent = routeData.safety_score || 'N/A';

    // Add popup to route
    const midpoint = Math.floor(coordinates.length / 2);
    L.popup()
        .setLatLng(coordinates[midpoint])
        .setContent(`
            <div class="popup-header">📍 Safe Route</div>
            <div class="popup-content">
                <p><strong>Distance:</strong> ${routeData.total_distance_km} km</p>
                <p><strong>Safety Score:</strong> ${routeData.safety_score || 'N/A'}/100</p>
                ${routeData.estimated_time_minutes ? `<p><strong>Est. Time:</strong> ${routeData.estimated_time_minutes} min</p>` : ''}
            </div>
        `)
        .openOn(map);

    console.log('Route displayed successfully');
}

/**
 * Clear route and markers
 */
function clearRoute() {
    // Remove route layer
    if (routeLayer) {
        map.removeLayer(routeLayer);
        routeLayer = null;
    }

    // Remove markers
    if (startMarker) {
        map.removeLayer(startMarker);
        startMarker = null;
    }

    if (endMarker) {
        map.removeLayer(endMarker);
        endMarker = null;
    }

    // Clear coordinates
    startCoords = null;
    endCoords = null;

    // Clear input fields
    document.getElementById('route-start').value = '';
    document.getElementById('route-end').value = '';

    // Hide route info
    document.getElementById('route-info').style.display = 'none';

    console.log('Route cleared');
}

/**
 * Find nearest shelter from current location
 */
async function findNearestShelter(lat, lon) {
    try {
        showLoading(true);

        const response = await SheltersAPI.findNearest(lat, lon, 1);

        if (response.status === 'success' && response.data.length > 0) {
            const nearestShelter = response.data[0];
            const shelterCoords = nearestShelter.geometry.coordinates;

            // Set route to nearest shelter
            setRouteStart(lat, lon);
            setRouteEnd(shelterCoords[1], shelterCoords[0]);

            // Calculate route
            await calculateRoute();

            alert(`Nearest shelter: ${nearestShelter.name}\nDistance: ${nearestShelter.distance_km} km`);
        } else {
            alert('No shelters found nearby.');
        }

    } catch (error) {
        console.error('Error finding nearest shelter:', error);
        alert('Failed to find nearest shelter.');
    } finally {
        showLoading(false);
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        initRoutingControls,
        calculateRoute,
        clearRoute,
        findNearestShelter
    };
}
