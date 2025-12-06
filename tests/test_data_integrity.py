# """
# Data Integrity Tests
# ====================
# Verifies that required data files and directories exist.
# """

# import os
# import pytest

# # Base data directory
# DATA_DIR = "data/processed"


# def test_processed_directory_exists():
#     """Verify processed data directory exists"""
#     assert os.path.exists(DATA_DIR), f"Directory {DATA_DIR} does not exist"
#     assert os.path.isdir(DATA_DIR), f"{DATA_DIR} is not a directory"


# def test_kerala_base_layers_exist():
#     """Verify all required Kerala base layer files exist"""
#     required_files = [
#         "kerala_boundary.geojson",
#         "kerala_buildings.geojson",
#         "kerala_district.geojson",
#         "kerala_hospitals.geojson",
#         "kerala_roads.geojson",
#         "kerala_shelters.geojson",
#         "kerala_state.geojson",
#         "kerala_taluk.geojson",
#         "kerala_village.geojson"
#     ]

#     for filename in required_files:
#         filepath = os.path.join(DATA_DIR, filename)
#         assert os.path.exists(filepath), f"Required file {filename} not found"
#         assert os.path.isfile(filepath), f"{filename} is not a file"
#         # Verify file is not empty
#         assert os.path.getsize(filepath) > 0, f"{filename} is empty"


# def test_landslides_directory_exists():
#     """Verify Landslides directory exists and contains district files"""
#     landslides_dir = os.path.join(DATA_DIR, "Landslides")
#     assert os.path.exists(landslides_dir), "Landslides directory does not exist"
#     assert os.path.isdir(landslides_dir), "Landslides path is not a directory"

#     # Check that it contains some files
#     files = os.listdir(landslides_dir)
#     assert len(files) > 0, "Landslides directory is empty"


# def test_live_disasters_directory_exists():
#     """Verify live_disasters directory exists"""
#     live_disasters_dir = os.path.join(DATA_DIR, "live_disasters")
#     assert os.path.exists(live_disasters_dir), "live_disasters directory does not exist"
#     assert os.path.isdir(live_disasters_dir), "live_disasters path is not a directory"


# def test_optional_layers_if_exist():
#     """Check optional layers if they exist"""
#     optional_files = [
#         "kerala_coastline.geojson",
#         "kerala_rivers.geojson",
#         "kerala_water.geojson",
#         "kerala_emergency.geojson"
#     ]

#     for filename in optional_files:
#         filepath = os.path.join(DATA_DIR, filename)
#         if os.path.exists(filepath):
#             # If file exists, verify it's not empty
#             assert os.path.getsize(filepath) > 0, f"Optional file {filename} exists but is empty"
def test_layers_boundary(client):
    res = client.get("/api/layers/boundaries")
    assert res.status_code == 200

def test_layers_buildings(client):
    res = client.get("/api/layers/buildings")
    assert res.status_code == 200

def test_layers_coastline(client):
    res = client.get("/api/layers/coastline")
    assert res.status_code == 200

def test_layers_hospitals(client):
    res = client.get("/api/shelters/hospitals/all")
    assert res.status_code == 200

def test_layers_shelters(client):
    res = client.get("/api/shelters/all")
    assert res.status_code == 200
