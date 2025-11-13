"""
Application Configuration
=========================
Centralized configuration for the Disaster Response GIS system.
Loads settings from environment variables with sensible defaults.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# =============================================================================
# Flask Configuration
# =============================================================================
DEBUG = os.getenv('DEBUG', 'True') == 'True'
HOST = os.getenv('HOST', '0.0.0.0')
PORT = int(os.getenv('PORT', 5000))
SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

# =============================================================================
# Database Configuration (PostgreSQL + PostGIS)
# =============================================================================
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'disaster_gis_db')
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'password')

# SQLAlchemy Database URI
DATABASE_URI = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Connection pool settings
SQLALCHEMY_POOL_SIZE = int(os.getenv('SQLALCHEMY_POOL_SIZE', 10))
SQLALCHEMY_MAX_OVERFLOW = int(os.getenv('SQLALCHEMY_MAX_OVERFLOW', 20))

# =============================================================================
# GIS Configuration
# =============================================================================
# Default SRID for all spatial data (WGS 84)
DEFAULT_SRID = 4326

# Map default center (latitude, longitude)
MAP_CENTER_LAT = float(os.getenv('MAP_CENTER_LAT', 20.5937))  # India center
MAP_CENTER_LON = float(os.getenv('MAP_CENTER_LON', 78.9629))
MAP_DEFAULT_ZOOM = int(os.getenv('MAP_DEFAULT_ZOOM', 5))

# Buffer distances (in meters)
DISASTER_BUFFER_DISTANCE = int(os.getenv('DISASTER_BUFFER_DISTANCE', 5000))  # 5km
SAFE_ZONE_BUFFER = int(os.getenv('SAFE_ZONE_BUFFER', 10000))  # 10km

# =============================================================================
# API Configuration
# =============================================================================
# External API keys (if needed for real-time data)
WEATHER_API_KEY = os.getenv('WEATHER_API_KEY', '')
EARTHQUAKE_API_KEY = os.getenv('EARTHQUAKE_API_KEY', '')
TRAFFIC_API_KEY = os.getenv('TRAFFIC_API_KEY', '')

# API rate limiting
API_RATE_LIMIT = os.getenv('API_RATE_LIMIT', '100 per hour')

# =============================================================================
# Cache Configuration
# =============================================================================
CACHE_TYPE = os.getenv('CACHE_TYPE', 'simple')  # simple, redis, memcached
CACHE_DEFAULT_TIMEOUT = int(os.getenv('CACHE_DEFAULT_TIMEOUT', 300))  # 5 minutes

# Redis configuration (if using Redis cache)
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_DB = int(os.getenv('REDIS_DB', 0))

# =============================================================================
# Real-time Update Configuration
# =============================================================================
# Refresh intervals (in seconds)
DISASTER_UPDATE_INTERVAL = int(os.getenv('DISASTER_UPDATE_INTERVAL', 60))  # 1 minute
TRAFFIC_UPDATE_INTERVAL = int(os.getenv('TRAFFIC_UPDATE_INTERVAL', 300))  # 5 minutes
WEATHER_UPDATE_INTERVAL = int(os.getenv('WEATHER_UPDATE_INTERVAL', 600))  # 10 minutes

# =============================================================================
# Routing Configuration
# =============================================================================
# Maximum route distance (in meters)
MAX_ROUTE_DISTANCE = int(os.getenv('MAX_ROUTE_DISTANCE', 100000))  # 100km

# Routing algorithm preference
ROUTING_ALGORITHM = os.getenv('ROUTING_ALGORITHM', 'dijkstra')  # dijkstra, astar

# =============================================================================
# File Upload Configuration
# =============================================================================
UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'data/uploads')
ALLOWED_EXTENSIONS = {'geojson', 'shp', 'kml', 'gpx', 'json'}
MAX_UPLOAD_SIZE = int(os.getenv('MAX_UPLOAD_SIZE', 16 * 1024 * 1024))  # 16MB

# =============================================================================
# Logging Configuration
# =============================================================================
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = os.getenv('LOG_FILE', 'logs/app.log')

# =============================================================================
# Data Directories
# =============================================================================
RAW_DATA_DIR = 'data/raw'
PROCESSED_DATA_DIR = 'data/processed'
STATIC_DATA_DIR = 'frontend/static/data'
