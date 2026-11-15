import math
from typing import Any, Dict
import httpx
from src.data_acquisition.utils import normalize_similarity


async def get_elevation_and_slope(
    client: httpx.AsyncClient, lat: float, lon: float, profile: Dict[str, Any]
) -> Dict[str, Any]:
    targets = profile["targets"]
    delta_deg = 0.0009  # ~100 m cross stencil
    cos_lat = max(0.05, math.cos(math.radians(lat)))
    delta_lon = delta_deg / cos_lat

    lat_n = min(89.99, lat + delta_deg)
    lat_s = max(-89.99, lat - delta_deg)
    lon_e = ((lon + delta_lon + 180) % 360) - 180
    lon_w = ((lon - delta_lon + 180) % 360) - 180

    lats = f"{lat},{lat_n},{lat_s},{lat},{lat}"
    lons = f"{lon},{lon},{lon},{lon_e},{lon_w}"

    try:
        resp = await client.get(
            "https://api.open-meteo.com/v1/elevation",
            params={"latitude": lats, "longitude": lons},
            timeout=8.0,
        )
        resp.raise_for_status()
        elevs = resp.json().get("elevation", [])
        if len(elevs) < 5 or elevs[0] is None:
            raise ValueError("Elevation unavailable at coordinate")

        z_c, z_n, z_s, z_e, z_w = elevs[:5]
        dy_m = (lat_n - lat_s) * 111_320.0
        dx_m = (2.0 * delta_lon) * 111_320.0 * cos_lat

        dz_dy = (z_n - z_s) / max(dy_m, 1.0)
        dz_dx = (z_e - z_w) / max(dx_m, 1.0)
        slope_deg = math.degrees(math.atan(math.sqrt(dz_dx**2 + dz_dy**2)))

        elev_m = round(float(z_c), 1)
        slope_rounded = round(slope_deg, 2)

        elev_score = normalize_similarity(
            elev_m, targets["elevation_m"]["value"], targets["elevation_m"]["range"]
        )
        slope_score = normalize_similarity(
            slope_rounded, targets["slope_deg"]["value"], targets["slope_deg"]["range"]
        )
        combined_score = round(0.45 * elev_score + 0.55 * slope_score, 4)

        return {
            "available": True,
            "normalized_score": combined_score,
            "raw_metrics": {
                "elevation_m": elev_m,
                "slope_deg": slope_rounded,
            },
            "target_reference": {
                "target_elevation_m": targets["elevation_m"]["value"],
                "target_slope_deg": targets["slope_deg"]["value"],
            },
            "evidence": {
                "source": "Open-Meteo Copernicus DEM GLO-90 (5-point finite difference)",
                "spatial_resolution": "90 m",
                "limitations": "Sub-90m boulder fields and micro-topography require local LiDAR/drone DEMs.",
            },
        }
    except Exception as exc:
        return {
            "available": False,
            "normalized_score": None,
            "raw_metrics": {"error": str(exc)},
            "target_reference": {},
            "evidence": {
                "source": "Copernicus DEM 90m",
                "spatial_resolution": "90 m",
                "limitations": "Data unavailable",
            },
        }
