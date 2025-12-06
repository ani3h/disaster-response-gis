# """
# API Endpoint Tests
# ==================
# Simple tests for all main API endpoints.
# Tests verify each endpoint returns 200 and valid JSON.
# """

# import pytest
# import requests

# # Base URL for the API
# BASE_URL = "http://localhost:5000"


# def test_health_endpoint():
#     """Test /api/health endpoint"""
#     response = requests.get(f"{BASE_URL}/api/health")
#     assert response.status_code == 200
#     data = response.json()
#     assert data["status"] == "healthy"
#     assert "service" in data


# def test_layers_boundaries():
#     """Test /api/layers/boundaries endpoint"""
#     response = requests.get(f"{BASE_URL}/api/layers/boundaries")
#     assert response.status_code == 200
#     data = response.json()
#     assert data["type"] == "FeatureCollection"
#     assert "features" in data


# def test_layers_buildings():
#     """Test /api/layers/buildings endpoint"""
#     response = requests.get(f"{BASE_URL}/api/layers/buildings")
#     assert response.status_code == 200
#     data = response.json()
#     assert data["type"] == "FeatureCollection"
#     assert "features" in data


# def test_layers_hospitals():
#     """Test /api/layers/hospitals endpoint"""
#     response = requests.get(f"{BASE_URL}/api/layers/hospitals")
#     assert response.status_code == 200
#     data = response.json()
#     assert data["type"] == "FeatureCollection"
#     assert "features" in data


# def test_layers_shelters():
#     """Test /api/layers/shelters endpoint"""
#     response = requests.get(f"{BASE_URL}/api/layers/shelters")
#     assert response.status_code == 200
#     data = response.json()
#     assert data["type"] == "FeatureCollection"
#     assert "features" in data


# def test_disaster_live_flood():
#     """Test /api/disaster/live/flood endpoint"""
#     response = requests.get(f"{BASE_URL}/api/disaster/live/flood")
#     assert response.status_code == 200
#     data = response.json()
#     assert data["type"] == "FeatureCollection"
#     assert "features" in data


# def test_disaster_live_cyclone():
#     """Test /api/disaster/live/cyclone endpoint"""
#     response = requests.get(f"{BASE_URL}/api/disaster/live/cyclone")
#     assert response.status_code == 200
#     data = response.json()
#     assert data["type"] == "FeatureCollection"
#     assert "features" in data


# def test_disaster_live_landslide():
#     """Test /api/disaster/live/landslide endpoint"""
#     response = requests.get(f"{BASE_URL}/api/disaster/live/landslide")
#     assert response.status_code == 200
#     data = response.json()
#     assert data["type"] == "FeatureCollection"
#     assert "features" in data


# def test_disaster_landslides_with_fallback():
#     """Test /api/disaster/landslides endpoint with fallback logic"""
#     response = requests.get(f"{BASE_URL}/api/disaster/landslides")
#     assert response.status_code == 200
#     data = response.json()
#     # Should return either live data or fallback historical data
#     assert data["type"] == "FeatureCollection"
#     assert "features" in data
#     # Check if metadata indicates data source
#     if "metadata" in data:
#         assert "source" in data["metadata"]
import json

def test_disaster_statistics(client):
    response = client.get("/api/disaster/statistics")
    assert response.status_code == 200
    assert isinstance(response.json, dict)

def test_disaster_updates(client):
    response = client.get("/api/disaster/updates")
    assert response.status_code == 200
    assert isinstance(response.json, dict)

def test_landslides_endpoint(client):
    response = client.get("/api/disaster/landslides")
    assert response.status_code == 200

def test_live_flood(client):
    response = client.get("/api/disaster/live/flood")
    assert response.status_code == 200

def test_live_cyclone(client):
    response = client.get("/api/disaster/live/cyclone")
    assert response.status_code == 200

def test_live_landslide(client):
    response = client.get("/api/disaster/live/landslide")
    assert response.status_code == 200
