from typing import Any, Dict
import httpx
from src.data_acquisition.utils import fetch_era5_daily, normalize_similarity, safe_mean


async def get_aridity_and_soil_moisture(
    client: httpx.AsyncClient, lat: float, lon: float, profile: Dict[str, Any]
) -> Dict[str, Any]:
    targets = profile["targets"]
    try:
        daily = await fetch_era5_daily(client, lat, lon)
        precip_list = daily.get("precipitation_sum", [])
        pet_list = daily.get("et0_fao_evapotranspiration", [])
        sm_list = daily.get("soil_moisture_0_to_7cm_mean", [])

        if not precip_list and not pet_list:
            raise ValueError("Empty ERA5 precipitation/evapotranspiration series")

        total_precip_mm = sum(p for p in precip_list if p is not None)
        total_pet_mm = sum(e for e in pet_list if e is not None)
        aridity_index = total_precip_mm / max(total_pet_mm, 50.0)
        soil_moisture = safe_mean(sm_list)

        ai_score = normalize_similarity(
            aridity_index, targets["aridity_index"]["value"], targets["aridity_index"]["range"]
        )
        if soil_moisture is not None:
            sm_score = normalize_similarity(
                soil_moisture, targets["soil_moisture"]["value"], targets["soil_moisture"]["range"]
            )
            combined_score = round(0.6 * ai_score + 0.4 * sm_score, 4)
        else:
            combined_score = ai_score

        return {
            "available": True,
            "normalized_score": combined_score,
            "raw_metrics": {
                "aridity_index_p_pet": round(aridity_index, 4),
                "annual_precipitation_mm": round(total_precip_mm, 1),
                "annual_pet_mm": round(total_pet_mm, 1),
                "soil_moisture_0_7cm_m3m3": round(soil_moisture, 4) if soil_moisture is not None else None,
            },
            "target_reference": {
                "target_aridity_index": targets["aridity_index"]["value"],
                "target_soil_moisture_m3m3": targets["soil_moisture"]["value"],
            },
            "evidence": {
                "source": "Open-Meteo ERA5-Land Historical Reanalysis (2025 full year)",
                "spatial_resolution": "~9 km (0.1 deg grid)",
                "limitations": "Reanalysis soil moisture represents 0-7 cm bulk layer; local micro-habitats may vary.",
            },
        }
    except Exception as exc:
        return {
            "available": False,
            "normalized_score": None,
            "raw_metrics": {"error": str(exc)},
            "target_reference": {},
            "evidence": {
                "source": "Open-Meteo ERA5-Land",
                "spatial_resolution": "~9 km",
                "limitations": "Data unavailable",
            },
        }
