# 🌍 Disaster Response GIS

### Real-Time Impact Mapping and Safe Route Visualization for Emergency Management

This project aims to create an **interactive GIS-based disaster response dashboard** that visualizes real-time disaster impact zones, identifies safe evacuation routes, and maps nearby shelters and hospitals. By integrating spatial data, open-source mapping tools, and real-time datasets, the system enhances **situational awareness** and **disaster response coordination**.

---

## Features
- Real-time visualization of disaster impact zones (floods, cyclones, earthquakes)
- Safe route and evacuation path optimization using network analysis
- Mapping of hospitals, shelters, and safe zones
- Integration of open-source datasets (OSM, NDMA, Bhuvan, IMD)
- Interactive web dashboard using **Leaflet/Folium** and **Flask/Django**

---

## Project Objectives
- Develop a real-time GIS dashboard for visualizing disaster impacts  
- Identify optimal evacuation routes using spatial and network analysis  
- Demonstrate the potential of open GIS data for emergency planning

---

## Directory Map

```
disaster-response-gis/
│
│ app.py                     # Main Flask app entry point
│ config.py                  # App + DB configuration
│ requirements.txt           # Python dependencies
│ .env.example               # Sample environment variables
│
├── backend/                 # Backend logic (APIs, GIS, DB)
│   ├── api/                 
│   │   ├── disaster_api.py  # Disaster zones API
│   │   ├── routes_api.py    # Safe route API
│   │   ├── shelters_api.py  # Shelter/hospital API
│   │   └── layers_api.py    # Map layers API
│   │
│   ├── core/                
│   │   ├── data_loader.py      # Load GIS data
│   │   ├── spatial_analysis.py # Buffers, overlays, risk zones
│   │   ├── route_optimizer.py  # Route calculation (NetworkX)
│   │   └── impact_analysis.py  # Severity + exposure analysis
│   │
│   ├── db/
│   │   ├── db_connection.py   # PostGIS connection
│   │   ├── models.py          # DB models
│   │   └── postgis_queries.py # Spatial SQL calls
│   │
│   ├── services/
│   │   ├── real_time_fetcher.py # Live data fetch
│   │   └── cache_manager.py    # API caching
│   │
│   └── __init__.py
│
├── frontend/                # Web dashboard (Leaflet)
│   ├── templates/index.html # Main UI
│   └── static/
│       ├── css/styles.css   # Dashboard styles
│       └── js/
│           ├── map.js        # Leaflet map init
│           ├── layers.js     # Layer toggles
│           ├── routing.js    # Route drawing
│           └── api_client.js # API calls
│
├── data/                    # GIS datasets
│   ├── raw/                 # Raw data
│   └── processed/           # Clean GeoJSON layers
│
├── docs/                    # SRS + diagrams
└── tests/                   # Backend tests

```

---
