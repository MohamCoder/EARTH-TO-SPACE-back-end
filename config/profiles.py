from typing import Any, Dict, List

TARGET_PROFILES: Dict[str, Dict[str, Any]] = {
    "mars_regolith": {
        "name": "Mars — Dry Basaltic Regolith & Rover Mobility",
        "body": "Mars",
        "description": "Hyper-arid, cold basaltic plains and craters (e.g., Jezero/Gale analog).",
        "weights": {
            "aridity_and_soil_moisture": 0.25,
            "elevation_and_slope": 0.20,
            "geology_and_surface_material": 0.25,
            "ice_and_water_indicators": 0.10,
            "temperature": 0.20,
        },
        "targets": {
            "aridity_index": {"value": 0.01, "range": 0.50},
            "soil_moisture": {"value": 0.02, "range": 0.35},
            "elevation_m": {"value": 1500.0, "range": 4500.0},
            "slope_deg": {"value": 4.0, "range": 25.0},
            "sand_fraction_pct": {"value": 75.0, "range": 75.0},
            "freezing_day_ratio": {"value": 0.85, "range": 1.0},
            "snowfall_ratio": {"value": 0.05, "range": 0.60},
            "temp_mean_c": {"value": -20.0, "range": 50.0},
            "diurnal_range_c": {"value": 22.0, "range": 25.0},
        },
        "preferred_lithologies": [
            "basalt", "volcanic", "andesite", "mafic", "sand", "alluvium", "gravel", "evaporite"
        ],
    },
    "mars_polar": {
        "name": "Mars — Polar & Permafrost Ice Operations",
        "body": "Mars",
        "description": "Cold, dry periglacial terrain for subsurface ice drilling and ISRU.",
        "weights": {
            "aridity_and_soil_moisture": 0.15,
            "elevation_and_slope": 0.15,
            "geology_and_surface_material": 0.15,
            "ice_and_water_indicators": 0.35,
            "temperature": 0.20,
        },
        "targets": {
            "aridity_index": {"value": 0.05, "range": 0.60},
            "soil_moisture": {"value": 0.10, "range": 0.40},
            "elevation_m": {"value": 1000.0, "range": 4000.0},
            "slope_deg": {"value": 3.0, "range": 20.0},
            "sand_fraction_pct": {"value": 60.0, "range": 70.0},
            "freezing_day_ratio": {"value": 0.95, "range": 0.95},
            "snowfall_ratio": {"value": 0.70, "range": 0.80},
            "temp_mean_c": {"value": -25.0, "range": 50.0},
            "diurnal_range_c": {"value": 15.0, "range": 25.0},
        },
        "preferred_lithologies": [
            "glacial", "till", "basalt", "volcanic", "sediment", "sand", "gravel"
        ],
    },
    "lunar_basalt": {
        "name": "Moon — Lunar Maria Basaltic Terrain",
        "body": "Moon",
        "description": "Dry, rocky basaltic lava fields and pyroclastic regolith for EVA & mobility.",
        "weights": {
            "aridity_and_soil_moisture": 0.20,
            "elevation_and_slope": 0.25,
            "geology_and_surface_material": 0.30,
            "ice_and_water_indicators": 0.10,
            "temperature": 0.15,
        },
        "targets": {
            "aridity_index": {"value": 0.01, "range": 0.50},
            "soil_moisture": {"value": 0.02, "range": 0.35},
            "elevation_m": {"value": 2000.0, "range": 4500.0},
            "slope_deg": {"value": 6.0, "range": 25.0},
            "sand_fraction_pct": {"value": 80.0, "range": 80.0},
            "freezing_day_ratio": {"value": 0.20, "range": 1.0},
            "snowfall_ratio": {"value": 0.0, "range": 0.50},
            "temp_mean_c": {"value": 10.0, "range": 45.0},
            "diurnal_range_c": {"value": 25.0, "range": 25.0},
        },
        "preferred_lithologies": [
            "basalt", "volcanic", "gabbro", "anorthosite", "tephra", "ash", "lava", "scoria"
        ],
    },
    "lunar_polar": {
        "name": "Moon — South Pole Cryogenic & Crater Rim Analog",
        "body": "Moon",
        "description": "Steep crater-like relief with extreme cold and volatile ice indicators.",
        "weights": {
            "aridity_and_soil_moisture": 0.15,
            "elevation_and_slope": 0.25,
            "geology_and_surface_material": 0.15,
            "ice_and_water_indicators": 0.25,
            "temperature": 0.20,
        },
        "targets": {
            "aridity_index": {"value": 0.05, "range": 0.60},
            "soil_moisture": {"value": 0.08, "range": 0.40},
            "elevation_m": {"value": 2500.0, "range": 4500.0},
            "slope_deg": {"value": 14.0, "range": 25.0},
            "sand_fraction_pct": {"value": 70.0, "range": 75.0},
            "freezing_day_ratio": {"value": 0.95, "range": 0.95},
            "snowfall_ratio": {"value": 0.65, "range": 0.80},
            "temp_mean_c": {"value": -25.0, "range": 50.0},
            "diurnal_range_c": {"value": 18.0, "range": 25.0},
        },
        "preferred_lithologies": [
            "anorthosite", "basalt", "breccia", "volcanic", "glacial", "granite"
        ],
    },
}

CANDIDATE_SITES: List[Dict[str, Any]] = [
    {"id": "atacama", "name": "Atacama Desert", "country": "Chile", "lat": -24.5000, "lon": -69.2500, "recommended_target": "mars_regolith"},
    {"id": "dallol", "name": "Dallol / Danakil Depression", "country": "Ethiopia", "lat": 14.2417, "lon": 40.3000, "recommended_target": "mars_regolith"},
    {"id": "iceland", "name": "Icelandic Volcanic & Glacial Terrain", "country": "Iceland", "lat": 64.9631, "lon": -19.0208, "recommended_target": "mars_polar"},
    {"id": "oman", "name": "Oman Desert Landscapes (Wahiba / Dhofar)", "country": "Oman", "lat": 21.5000, "lon": 57.0000, "recommended_target": "mars_regolith"},
    {"id": "mauna_kea", "name": "Mauna Kea Volcanic Fields", "country": "Hawaii, USA", "lat": 19.8207, "lon": -155.4681, "recommended_target": "lunar_basalt"},
    {"id": "lanzarote", "name": "Lanzarote Volcanic Fields", "country": "Canary Islands, Spain", "lat": 29.0469, "lon": -13.5899, "recommended_target": "lunar_basalt"},
    {"id": "mcmurdo", "name": "McMurdo Dry Valleys", "country": "Antarctica", "lat": -77.4667, "lon": 162.5167, "recommended_target": "mars_polar"},
]
