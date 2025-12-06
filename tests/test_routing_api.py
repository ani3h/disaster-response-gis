# """
# Routing API Tests
# =================
# Tests for safe route calculation endpoint.
# """

# import pytest
# import requests

# BASE_URL = "http://localhost:5000"


# def test_safe_route_endpoint():
#     """Test /api/routes/safe-route with minimal payload"""
#     # Minimal payload with sample coordinates in Kerala
#     payload = {
#         "origin": [76.2711, 9.9312],      # Kochi coordinates (lon, lat)
#         "destination": [76.9366, 8.5241],  # Thiruvananthapuram coordinates
#         "disaster_type": "flood"
#     }

#     response = requests.post(
#         f"{BASE_URL}/api/routes/safe-route",
#         json=payload
#     )

#     assert response.status_code == 200
#     data = response.json()

#     # Assert route geometry exists
#     assert "route" in data or "geometry" in data or "type" in data

#     # If it's a GeoJSON response
#     if "type" in data:
#         assert data["type"] in ["Feature", "FeatureCollection"]

#     # If route has geometry
#     if "geometry" in data:
#         assert data["geometry"] is not None
def test_route_api_responds(client):
    sample_payload = {
        "start": {"lat": 10.0, "lng": 76.0},
        "end": {"lat": 10.1, "lng": 76.1},
        "avoid": []
    }
    
    res = client.post("/api/routes/calculate", json=sample_payload)
    assert res.status_code == 200
    assert isinstance(res.json, dict)
