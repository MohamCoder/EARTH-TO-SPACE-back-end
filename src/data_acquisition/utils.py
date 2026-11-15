import asyncio
import math
from typing import Any, Dict, List, Optional, Tuple

import httpx

# Deduplicates concurrent ERA5-Land requests for the same coordinate (~100m grid)
_ERA5_CACHE: Dict[Tuple[float, float], asyncio.Task] = {}
_MAX_CACHE_SIZE = 256


def normalize_similarity(earth_val: float, target_val: float, ref_range: float) -> float:
    """Clamped linear similarity: 1 - |Earth - Target| / Reference_Range."""
    if ref_range <= 0:
        return 0.0
    score = 1.0 - abs(earth_val - target_val) / ref_range
    return round(max(0.0, min(1.0, score)), 4)


def safe_mean(values: List[Optional[float]]) -> Optional[float]:
    clean = [v for v in values if v is not None and not math.isnan(v)]
    return sum(clean) / len(clean) if clean else None


async def _download_era5_daily(client: httpx.AsyncClient, lat: float, lon: float) -> Dict[str, Any]:
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": "2025-01-01",
        "end_date": "2025-12-31",
        "daily": ",".join([
            "temperature_2m_mean",
            "temperature_2m_max",
            "temperature_2m_min",
            "precipitation_sum",
            "snowfall_sum",
            "et0_fao_evapotranspiration",
            "soil_moisture_0_to_7cm_mean",
        ]),
        "timezone": "UTC",
    }
    resp = await client.get(url, params=params, timeout=12.0)
    resp.raise_for_status()
    return resp.json().get("daily", {})


async def fetch_era5_daily(client: httpx.AsyncClient, lat: float, lon: float) -> Dict[str, Any]:
    """
    Shares a single 2025 ERA5-Land daily payload (~15 KB) across Aridity,
    Ice/Water, and Temperature modules when queried concurrently.
    """
    key = (round(lat, 3), round(lon, 3))

    if len(_ERA5_CACHE) >= _MAX_CACHE_SIZE:
        _ERA5_CACHE.clear()

    task = _ERA5_CACHE.get(key)
    if task is None:
        task = asyncio.create_task(_download_era5_daily(client, lat, lon))
        _ERA5_CACHE[key] = task

    try:
        return await task
    except Exception:
        _ERA5_CACHE.pop(key, None)
        raise
