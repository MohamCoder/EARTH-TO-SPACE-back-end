from typing import Any, Dict
import httpx
from src.data_acquisition.utils import fetch_era5_daily, normalize_similarity, safe_mean


async def get_temperature(
    client: httpx.AsyncClient, lat: float, lon: float, profile: Dict[str, Any]
) -> Dict[str, Any]:
    targets = profile["targets"]
    try:
        daily = await fetch_era5_daily(client, lat, lon)
        t_mean_list = daily.get("temperature_2m_mean", [])
        t_max_list = daily.get("temperature_2m_max", [])
        t_min_list = daily.get("temperature_2m_min", [])

        t_mean = safe_mean(t_mean_list)
        if t_mean is None:
            raise ValueError("Temperature series unavailable")

        diurnal_vals = [
            mx - mn for mx, mn in zip(t_max_list, t_min_list)
            if mx is not None and mn is not None
        ]
        diurnal_mean = safe_mean(diurnal_vals) or 0.0

        t_mean_score = normalize_similarity(
            t_mean, targets["temp_mean_c"]["value"], targets["temp_mean_c"]["range"]
        )
        diurnal_score = normalize_similarity(
            diurnal_mean, targets["diurnal_range_c"]["value"], targets["diurnal_range_c"]["range"]
        )
        combined_score = round(0.65 * t_mean_score + 0.35 * diurnal_score, 4)

        return {
            "available": True,
            "normalized_score": combined_score,
            "raw_metrics": {
                "annual_mean_temp_c": round(t_mean, 2),
                "mean_diurnal_range_c": round(diurnal_mean, 2),
            },
            "target_reference": {
                "target_mean_temp_c": targets["temp_mean_c"]["value"],
                "target_diurnal_range_c": targets["diurnal_range_c"]["value"],
            },
            "evidence": {
                "source": "Open-Meteo ERA5-Land 2m Air Temperature (2025)",
                "spatial_resolution": "~9 km",
                "limitations": "Earth atmospheric damping prevents matching extreme lunar/Martian radiative swings.",
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
