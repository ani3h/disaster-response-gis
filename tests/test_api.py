"""
API Tests
=========
Tests for API endpoints.
"""

import pytest
from app import create_app


@pytest.fixture
def client():
    """Create test client"""
    app = create_app()
    app.config['TESTING'] = True

    with app.test_client() as client:
        yield client


def test_health_check(client):
    """Test health check endpoint"""
    response = client.get('/api/health')
    assert response.status_code == 200

    data = response.get_json()
    assert data['status'] == 'healthy'
    assert 'service' in data


def test_disaster_zones(client):
    """Test disaster zones endpoint"""
    response = client.get('/api/disaster/zones')
    assert response.status_code == 200

    data = response.get_json()
    assert data['status'] == 'success'
    assert 'data' in data


def test_check_location_safety(client):
    """Test location safety check endpoint"""
    payload = {
        'latitude': 19.0760,
        'longitude': 72.8777
    }

    response = client.post('/api/disaster/check-location', json=payload)
    assert response.status_code == 200

    data = response.get_json()
    assert data['status'] == 'success'


def test_check_location_missing_params(client):
    """Test location safety check with missing parameters"""
    response = client.post('/api/disaster/check-location', json={})
    assert response.status_code == 400


def test_calculate_route(client):
    """Test route calculation endpoint"""
    payload = {
        'start': {'lat': 19.0760, 'lon': 72.8777},
        'end': {'lat': 19.1136, 'lon': 72.8697}
    }

    response = client.post('/api/routes/safe-route', json=payload)
    assert response.status_code == 200

    data = response.get_json()
    assert data['status'] == 'success'


def test_nearest_shelters(client):
    """Test nearest shelters endpoint"""
    payload = {
        'latitude': 19.0760,
        'longitude': 72.8777,
        'limit': 5
    }

    response = client.post('/api/shelters/nearest', json=payload)
    assert response.status_code == 200

    data = response.get_json()
    assert data['status'] == 'success'


# TODO: Add more API tests
# - Test error handling
# - Test authentication (when implemented)
# - Test rate limiting
# - Test data validation
