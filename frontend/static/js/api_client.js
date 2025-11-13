/**
 * API Client Module
 * =================
 * Handles all API requests to the backend.
 */

const API_BASE_URL = window.location.origin + '/api';

/**
 * Generic fetch wrapper with error handling
 */
async function apiFetch(endpoint, options = {}) {
    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            ...options,
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            }
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        return data;

    } catch (error) {
        console.error('API request failed:', error);
        throw error;
    }
}

/**
 * Disaster API calls
 */
const DisasterAPI = {
    /**
     * Get all active disaster zones
     */
    async getDisasterZones() {
        return await apiFetch('/disaster/zones');
    },

    /**
     * Check if a location is safe
     */
    async checkLocationSafety(lat, lon) {
        return await apiFetch('/disaster/check-location', {
            method: 'POST',
            body: JSON.stringify({ latitude: lat, longitude: lon })
        });
    },

    /**
     * Get recent disaster updates
     */
    async getUpdates(limit = 10) {
        return await apiFetch(`/disaster/updates?limit=${limit}`);
    },

    /**
     * Get disaster statistics
     */
    async getStatistics() {
        return await apiFetch('/disaster/statistics');
    },

    /**
     * Analyze disaster impact
     */
    async analyzeImpact(disasterZoneId) {
        return await apiFetch('/disaster/impact-analysis', {
            method: 'POST',
            body: JSON.stringify({ disaster_zone_id: disasterZoneId })
        });
    }
};

/**
 * Routes API calls
 */
const RoutesAPI = {
    /**
     * Calculate safe route between two points
     */
    async calculateSafeRoute(startLat, startLon, endLat, endLon) {
        return await apiFetch('/routes/safe-route', {
            method: 'POST',
            body: JSON.stringify({
                start: { lat: startLat, lon: startLon },
                end: { lat: endLat, lon: endLon },
                avoid_disaster_zones: true
            })
        });
    },

    /**
     * Get alternative routes
     */
    async getAlternativeRoutes(startLat, startLon, endLat, endLon, numRoutes = 3) {
        return await apiFetch('/routes/alternative-routes', {
            method: 'POST',
            body: JSON.stringify({
                start: { lat: startLat, lon: startLon },
                end: { lat: endLat, lon: endLon },
                num_routes: numRoutes
            })
        });
    },

    /**
     * Calculate distance between two points
     */
    async calculateDistance(lat1, lon1, lat2, lon2) {
        return await apiFetch('/routes/distance', {
            method: 'POST',
            body: JSON.stringify({
                point1: { lat: lat1, lon: lon1 },
                point2: { lat: lat2, lon: lon2 }
            })
        });
    }
};

/**
 * Shelters API calls
 */
const SheltersAPI = {
    /**
     * Find nearest shelters
     */
    async findNearest(lat, lon, limit = 5) {
        return await apiFetch('/shelters/nearest', {
            method: 'POST',
            body: JSON.stringify({
                latitude: lat,
                longitude: lon,
                limit: limit
            })
        });
    },

    /**
     * Get all shelters as GeoJSON
     */
    async getAll() {
        return await apiFetch('/shelters/all');
    },

    /**
     * Get shelter capacity summary
     */
    async getCapacitySummary() {
        return await apiFetch('/shelters/capacity');
    },

    /**
     * Find nearest hospitals
     */
    async findNearestHospitals(lat, lon, limit = 5) {
        return await apiFetch('/shelters/hospitals/nearest', {
            method: 'POST',
            body: JSON.stringify({
                latitude: lat,
                longitude: lon,
                limit: limit
            })
        });
    },

    /**
     * Get all hospitals as GeoJSON
     */
    async getAllHospitals() {
        return await apiFetch('/shelters/hospitals/all');
    }
};

/**
 * Layers API calls
 */
const LayersAPI = {
    /**
     * Get all available layers metadata
     */
    async getLayersMetadata() {
        return await apiFetch('/layers/');
    },

    /**
     * Get roads layer
     */
    async getRoads(bbox = null) {
        const url = bbox
            ? `/layers/roads?bbox=${bbox.join(',')}`
            : '/layers/roads';
        return await apiFetch(url);
    },

    /**
     * Get admin boundaries
     */
    async getBoundaries(level = null) {
        const url = level
            ? `/layers/boundaries?level=${level}`
            : '/layers/boundaries';
        return await apiFetch(url);
    },

    /**
     * Get cyclone tracks
     */
    async getCycloneTracks(activeOnly = true) {
        return await apiFetch(`/layers/cyclone-tracks?active_only=${activeOnly}`);
    },

    /**
     * Calculate safe zones
     */
    async calculateSafeZones(bufferDistance = 5000) {
        return await apiFetch('/layers/safe-zones', {
            method: 'POST',
            body: JSON.stringify({ buffer_distance_meters: bufferDistance })
        });
    }
};

/**
 * Health check
 */
async function checkAPIHealth() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        const data = await response.json();
        return data.status === 'healthy';
    } catch (error) {
        console.error('API health check failed:', error);
        return false;
    }
}

/**
 * Update connection status indicator
 */
async function updateConnectionStatus() {
    const statusIndicator = document.getElementById('connection-status');
    const isHealthy = await checkAPIHealth();

    if (statusIndicator) {
        statusIndicator.style.color = isHealthy ? '#00ff00' : '#ff0000';
        statusIndicator.title = isHealthy ? 'Connected' : 'Disconnected';
    }
}

// Check API health on page load
document.addEventListener('DOMContentLoaded', () => {
    updateConnectionStatus();
    // Check every 30 seconds
    setInterval(updateConnectionStatus, 30000);
});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { DisasterAPI, RoutesAPI, SheltersAPI, LayersAPI };
}
