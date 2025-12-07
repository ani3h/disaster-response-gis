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

![disaster-response-dashboard](https://github.com/ani3h/disaster-response-gis/blob/f0d2d422a5516097f8ddc89bc7a79a633151f374/Archive/demo.gif)

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
│   ├── services/
│   │   ├── real_time_fetcher.py # Live data fetch
│   │   └── cache_manager.py    # API caching
│   │
│   └── init__.py
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
├── tests/                # Testing Files
│   ├── conftest.py
│   ├── test_api_endpoints.py
│   ├── test_data_intergration.py
│   └── test_routing_api.py
│
└── data/                    # GIS datasets
    ├── raw/                 # Raw data
    └── processed/           # Clean GeoJSON layers


```

---

## Setup Instructions

### A. Environment Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/disaster-response-gis.git
   cd disaster-response-gis
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv gis
   source gis/bin/activate  # On Windows: gis\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

### B. Downloading the /data dir

Download the 'data' dir from the following link:
```bash
https://iiitbac-my.sharepoint.com/:u:/g/personal/kantheti_anish_iiitb_ac_in/EUW-F_s1p0xJspEelGc9k90BDU-qqSuAcgYMn_klQdLLpQ?e=2c9oHJ
```

After dowloading put in the root dir according to the Directory Map

### C. Environment Variables

Create a `.env` file in the project root with the following variables:

```bash
# API Keys
AMBEE_API_KEY=your_key_here

# Flask Configuration
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
```

You can copy from the example file:
```bash
cp .env.example .env
```

### D. Run the Application

Start the Flask development server:
```bash
python app.py
```

Open your browser and navigate to:
```
http://localhost:5000
```

---

## Testing

### 1. Requirements

Before testing, install dependencies:
```bash
python -m venv venv
source venv/bin/activate      # macOS / Linux
venv\Scripts\activate         # Windows
```

```bash
pip install -r requirements.txt
```

This project uses:
- pytest
- pytest-flask


### 2. Verify installation: 
```bash
pip install pytest pytest-flask
```

### 3. Test Structure

All test scripts are inside:

tests/
│ test_api_endpoints.py
│ test_data_integrity.py
│ test_routing_api.py
│ conftest.py

NOTE: Tests do NOT require real API keys and do not depend on live data.

### 4. Configuration

Make sure .env exists : 
```bash
copy .env.example .env
Add: AMBEE_API_KEY=dummy_value
```

5. Run All Tests

From the project root:
```bash
pytest -v
```
