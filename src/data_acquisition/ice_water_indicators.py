from typing import Any, Dict
import httpx
from src.data_acquisition.utils import fetch_era5_daily, normalize_similarity


async def get_ice_and_water_indicators(
    client: httpx.AsyncClient,
    lat: float,
    lon: float,
    profile: Dict[str, Any],
    elevation_m: float | None = None,
    has_land_geology: bool = True,
) -> Dict[str, Any]:
    targets = profile["targets"]
    try:
        daily = await fetch_era5_daily(client, lat, lon)
        t_mean_list = daily.get("temperature_2m_mean", [])
        precip_list = daily.get("precipitation_sum", [])
        snow_list = daily.get("snowfall_sum", [])

        valid_days = [t for t in t_mean_list if t is not None]
        if not valid_days:
            raise ValueError("Temperature series unavailable for freeze-day calculation")

        freezing_days = sum(1 for t in valid_days if t < 0.0)
        freezing_day_ratio = freezing_days / len(valid_days)

        total_precip_mm = sum(p for p in precip_list if p is not None)
        total_snow_we_mm = sum(s for s in snow_list if s is not None)
        snowfall_ratio = (
            min(1.0, total_snow_we_mm / max(total_precip_mm, 1.0))
            if total_precip_mm > 1.0
            else (1.0 if total_snow_we_mm > 0 else 0.0)
        )

        likely_water = (elevation_m is not None and elevation_m <= 0.0 and not has_land_geology)

        if likely_water:
            combined_score = 0.0
        else:
            freeze_score = normalize_similarity(
                freezing_day_ratio, targets["freezing_day_ratio"]["value"], targets["freezing_day_ratio"]["range"]
            )
            snow_score = normalize_similarity(
                snowfall_ratio, targets["snowfall_ratio"]["value"], targets["snowfall_ratio"]["range"]
            )
            combined_score = round(0.55 * freeze_score + 0.45 * snow_score, 4)

        return {
            "available": True,
            "normalized_score": combined_score,
            "raw_metrics": {
                "freezing_day_ratio": round(freezing_day_ratio, 3),
                "snowfall_water_equiv_ratio": round(snowfall_ratio, 3),
                "likely_open_water_body": likely_water,
            },
            "target_reference": {
                "target_freezing_day_ratio": targets["freezing_day_ratio"]["value"],
                "target_snowfall_ratio": targets["snowfall_ratio"]["value"],
            },
            "evidence": {
                "source": "Open-Meteo ERA5-Land Cryosphere Proxy & Land/Elevation Mask",
                "spatial_resolution": "~9 km",
                "limitations": "Surface freeze/snow metrics are proxy indicators, not confirmed subsurface ground-ice cores.",
            },
        }
    except Exception as exc:
        return {
            "available": False,
            "normalized_score": None,
            "raw_metrics": {"error": str(exc)},
            "target_reference": {},
            "evidence": {
                "source": "ERA5-Land",
                "spatial_resolution": "~9 km",
                "limitations": "Data unavailable",
            },
        }
