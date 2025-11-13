/**
 * Map Initialization Module
 * ==========================
 * Initializes the Leaflet map and handles main map interactions.
 */

// Global map variable
let map;
let userMarker = null;
let currentRoute = null;

/**
 * Initialize the Leaflet map
 */
function initMap() {
    // Create map centered on India (can be changed via config)
    map = L.map('map').setView([20.5937, 78.9629], 5);

    // Add base tile layer (OpenStreetMap)
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        maxZoom: 19
    }).addTo(map);

    // Add scale control
    L.control.scale({ position: 'bottomleft' }).addTo(map);

    console.log('Map initialized successfully');
}

/**
 * Add user location marker
 */
function addUserLocation(lat, lon) {
    if (userMarker) {
        map.removeLayer(userMarker);
    }

    userMarker = L.marker([lat, lon], {
        icon: L.divIcon({
            className: 'user-location-marker',
            html: '📍',
            iconSize: [30, 30]
        })
    }).addTo(map);

    userMarker.bindPopup('<b>Your Location</b>').openPopup();
    map.setView([lat, lon], 13);
}

/**
 * Get user's current location
 */
function locateUser() {
    if ('geolocation' in navigator) {
        showLoading(true);

        navigator.geolocation.getCurrentPosition(
            (position) => {
                const lat = position.coords.latitude;
                const lon = position.coords.longitude;

                addUserLocation(lat, lon);
                showLoading(false);

                // Check if location is safe
                checkLocationSafety(lat, lon);
            },
            (error) => {
                console.error('Geolocation error:', error);
                alert('Unable to get your location. Please check location permissions.');
                showLoading(false);
            }
        );
    } else {
        alert('Geolocation is not supported by your browser.');
    }
}

/**
 * Check if current location is in disaster zone
 */
async function checkLocationSafety(lat, lon) {
    try {
        const response = await DisasterAPI.checkLocationSafety(lat, lon);

        if (response.status === 'success') {
            const data = response.data;

            if (data.in_danger) {
                alert(`⚠️ WARNING: You are in a disaster zone!\n\nZone: ${data.name}\nSeverity: ${data.severity}\n\nPlease evacuate to safety immediately!`);
            } else {
                console.log('Location is safe');
            }
        }
    } catch (error) {
        console.error('Error checking location safety:', error);
    }
}

/**
 * Search for a location
 */
async function searchLocation(query) {
    if (!query.trim()) return;

    showLoading(true);

    try {
        // Using Nominatim geocoding API (free, but rate-limited)
        const response = await fetch(
            `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(query)}`
        );

        const results = await response.json();

        if (results.length > 0) {
            const result = results[0];
            const lat = parseFloat(result.lat);
            const lon = parseFloat(result.lon);

            map.setView([lat, lon], 13);

            // Add temporary marker
            L.marker([lat, lon])
                .addTo(map)
                .bindPopup(`<b>${result.display_name}</b>`)
                .openPopup();
        } else {
            alert('Location not found. Please try a different search term.');
        }
    } catch (error) {
        console.error('Search error:', error);
        alert('Error searching for location.');
    } finally {
        showLoading(false);
    }
}

/**
 * Refresh all map data
 */
async function refreshMapData() {
    showLoading(true);

    try {
        // Reload all layers
        await loadDisasterZones();
        await loadShelters();
        await loadHospitals();

        // Update statistics
        await updateStatistics();

        // Update last update time
        updateLastUpdateTime();

        console.log('Map data refreshed');
    } catch (error) {
        console.error('Error refreshing data:', error);
    } finally {
        showLoading(false);
    }
}

/**
 * Update statistics panel
 */
async function updateStatistics() {
    try {
        const response = await DisasterAPI.getStatistics();

        if (response.status === 'success') {
            const stats = response.data;

            document.getElementById('stat-disasters').textContent = stats.active_disasters || 0;
            document.getElementById('stat-population').textContent =
                (stats.estimated_affected_population || 0).toLocaleString();
            document.getElementById('stat-shelters').textContent = stats.active_alerts || 0;
            document.getElementById('stat-alerts').textContent = stats.active_alerts || 0;
        }
    } catch (error) {
        console.error('Error updating statistics:', error);
    }
}

/**
 * Load recent disaster updates
 */
async function loadDisasterUpdates() {
    try {
        const response = await DisasterAPI.getUpdates(5);

        if (response.status === 'success') {
            const updates = response.data;
            const updatesList = document.getElementById('updates-list');

            if (updates.length === 0) {
                updatesList.innerHTML = '<p class="loading">No recent updates</p>';
                return;
            }

            updatesList.innerHTML = updates.map(update => `
                <div class="update-item severity-${update.severity}">
                    <strong>${update.title}</strong>
                    <p style="font-size: 12px; margin-top: 5px;">${update.description}</p>
                    <p style="font-size: 11px; color: #666; margin-top: 5px;">
                        ${new Date(update.timestamp).toLocaleString()}
                    </p>
                </div>
            `).join('');
        }
    } catch (error) {
        console.error('Error loading updates:', error);
        document.getElementById('updates-list').innerHTML =
            '<p class="loading">Error loading updates</p>';
    }
}

/**
 * Update last update timestamp
 */
function updateLastUpdateTime() {
    const now = new Date();
    const timeStr = now.toLocaleTimeString();
    document.getElementById('last-update').textContent = `Last updated: ${timeStr}`;
}

/**
 * Show/hide loading overlay
 */
function showLoading(show) {
    const overlay = document.getElementById('loading-overlay');
    overlay.style.display = show ? 'flex' : 'none';
}

/**
 * Toggle fullscreen mode
 */
function toggleFullscreen() {
    if (!document.fullscreenElement) {
        document.documentElement.requestFullscreen();
    } else {
        if (document.exitFullscreen) {
            document.exitFullscreen();
        }
    }
}

/**
 * Initialize event listeners
 */
function initEventListeners() {
    // Locate me button
    document.getElementById('locate-me').addEventListener('click', locateUser);

    // Refresh data button
    document.getElementById('refresh-data').addEventListener('click', refreshMapData);

    // Fullscreen toggle
    document.getElementById('toggle-fullscreen').addEventListener('click', toggleFullscreen);

    // Search location
    document.getElementById('search-btn').addEventListener('click', () => {
        const query = document.getElementById('location-search').value;
        searchLocation(query);
    });

    document.getElementById('location-search').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            const query = e.target.value;
            searchLocation(query);
        }
    });

    console.log('Event listeners initialized');
}

/**
 * Initialize the application
 */
async function initApp() {
    console.log('Initializing Disaster Response GIS Dashboard...');

    // Initialize map
    initMap();

    // Initialize event listeners
    initEventListeners();

    // Initialize layer controls
    initLayerControls();

    // Initialize routing controls
    initRoutingControls();

    // Load initial data
    showLoading(true);

    try {
        await Promise.all([
            loadDisasterZones(),
            loadShelters(),
            loadHospitals(),
            updateStatistics(),
            loadDisasterUpdates()
        ]);

        updateLastUpdateTime();

        console.log('Application initialized successfully');
    } catch (error) {
        console.error('Error during initialization:', error);
    } finally {
        showLoading(false);
    }

    // Set up auto-refresh (every 5 minutes)
    setInterval(() => {
        refreshMapData();
        loadDisasterUpdates();
    }, 5 * 60 * 1000);
}

// Start the application when DOM is ready
document.addEventListener('DOMContentLoaded', initApp);
