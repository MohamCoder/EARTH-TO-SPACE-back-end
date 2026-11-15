import asyncio
from typing import Any, Dict

import httpx

from config.profiles import TARGET_PROFILES
from src.data_acquisition.aridity_soil_moisture import get_aridity_and_soil_moisture
from src.data_acquisition.elevation_and_slope import get_elevation_and_slope
from src.data_acquisition.geology_and_surface_material import get_geology_and_surface_material
from src.data_acquisition.ice_water_indicators import get_ice_and_water_indicators
from src.data_acquisition.temperature import get_temperature
from utils.scoring import AnalogAnalysisResponse, build_analog_response


async def evaluate_location(
    lat: float,
    lon: float,
    target_key: str,
    weights: Dict[str, float],
) -> AnalogAnalysisResponse:
    profile = TARGET_PROFILES[target_key]

    async with httpx.AsyncClient() as client:
        aridity_res, terrain_res, geology_res, temp_res = await asyncio.gather(
            get_aridity_and_soil_moisture(client, lat, lon, profile),
            get_elevation_and_slope(client, lat, lon, profile),
            get_geology_and_surface_material(client, lat, lon, profile),
            get_temperature(client, lat, lon, profile),
        )

        elev_m = terrain_res["raw_metrics"].get("elevation_m") if terrain_res["available"] else None
        ice_water_res = await get_ice_and_water_indicators(
            client,
            lat,
            lon,
            profile,
            elevation_m=elev_m,
            has_land_geology=geology_res["available"],
        )

    raw_criteria: Dict[str, Dict[str, Any]] = {
        "aridity_and_soil_moisture": aridity_res,
        "elevation_and_slope": terrain_res,
        "geology_and_surface_material": geology_res,
        "ice_and_water_indicators": ice_water_res,
        "temperature": temp_res,
    }

    return build_analog_response(lat, lon, target_key, profile, weights, raw_criteria)
