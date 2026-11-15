from typing import Dict, Optional
from fastapi import APIRouter, HTTPException, Query

from config.profiles import TARGET_PROFILES
from utils.pipeline import evaluate_location
from utils.scoring import AnalogAnalysisResponse

router = APIRouter(tags=["Analysis"])


def _parse_weights(
    target: str,
    w_aridity: Optional[float],
    w_terrain: Optional[float],
    w_geology: Optional[float],
    w_ice_water: Optional[float],
    w_temp: Optional[float],
) -> Dict[str, float]:
    defaults = TARGET_PROFILES[target]["weights"]
    overrides = {
        "aridity_and_soil_moisture": w_aridity,
        "elevation_and_slope": w_terrain,
        "geology_and_surface_material": w_geology,
        "ice_and_water_indicators": w_ice_water,
        "temperature": w_temp,
    }

    if all(v is None for v in overrides.values()):
        return dict(defaults)

    merged = {
        k: (overrides[k] if overrides[k] is not None else default_w)
        for k, default_w in defaults.items()
    }
    total = sum(merged.values())
    if total <= 0:
        raise HTTPException(status_code=400, detail="Custom weights must sum to > 0.")

    return {k: v / total for k, v in merged.items()}


@router.get("/analyze", response_model=AnalogAnalysisResponse)
async def analyze_point(
    lat: float = Query(..., ge=-90.0, le=90.0, description="Latitude in decimal degrees (-90 to 90)"),
    lon: float = Query(..., ge=-180.0, le=180.0, description="Longitude in decimal degrees (-180 to 180)"),
    target: str = Query("mars_regolith", description="Target profile: mars_regolith, mars_polar, lunar_basalt, lunar_polar"),
    w_aridity: Optional[float] = Query(None, ge=0.0, le=1.0, description="Optional custom weight for aridity & soil moisture"),
    w_terrain: Optional[float] = Query(None, ge=0.0, le=1.0, description="Optional custom weight for elevation & slope"),
    w_geology: Optional[float] = Query(None, ge=0.0, le=1.0, description="Optional custom weight for geology & surface material"),
    w_ice_water: Optional[float] = Query(None, ge=0.0, le=1.0, description="Optional custom weight for ice & water indicators"),
    w_temp: Optional[float] = Query(None, ge=0.0, le=1.0, description="Optional custom weight for temperature"),
):
    if target not in TARGET_PROFILES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid target '{target}'. Choose from: {list(TARGET_PROFILES.keys())}",
        )

    weights = _parse_weights(target, w_aridity, w_terrain, w_geology, w_ice_water, w_temp)
    return await evaluate_location(lat, lon, target, weights)
