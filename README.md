# EARTH-TO-SPACE — Terrestrial Analog Identification API

A lightweight **FastAPI** backend built for the **NASA Space Apps Challenge (Challenge 10: Identify Earth Locations that Analog the Permanent Moon Base Locations and Mars)**.

Instead of downloading multi-gigabyte satellite raster scenes per request, this API queries point-based geospatial REST endpoints on the fly (**< 25 KB total bandwidth per query**) to evaluate any Earth `(lat, lon)` coordinate against Moon and Mars mission profiles across five environmental criteria.

---

## Project Structure

```text
nasa_hackathon/
├── config/
│   ├── __init__.py
│   └── profiles.py                       # Moon/Mars target profiles, weights & candidate sites
├── src/
│   ├── __init__.py
│   ├── api/
│   │   ├── __init__.py                   # Exports api_router
│   │   ├── router.py                     # Combines route modules
│   │   ├── analyze.py                    # GET /analyze (validation & custom weight parsing)
│   │   └── catalog.py                    # GET /targets & GET /candidates
│   └── data_acquisition/
│       ├── __init__.py
│       ├── utils.py                      # Shared ERA5-Land request deduplicator & math helpers
│       ├── aridity_soil_moisture.py      # Criterion 1: UNEP Aridity Index & soil moisture
│       ├── elevation_and_slope.py        # Criterion 2: Copernicus 90m DEM & finite-difference slope
│       ├── geology_and_surface_material.py # Criterion 3: Macrostrat lithology & SoilGrids texture
│       ├── ice_water_indicators.py       # Criterion 4: Freezing-day fraction, snow ratio & water mask
│       └── temperature.py                # Criterion 5: Mean annual temperature & diurnal range
├── utils/
│   ├── __init__.py
│   ├── pipeline.py                       # Async orchestration across all 5 acquisition modules
│   └── scoring.py                        # Pydantic response schemas & weight re-normalization
├── main.py                               # FastAPI application entrypoint & CORS configuration
├── pyproject.toml
└── uv.lock EARTH-TO-SPACE-back-end
