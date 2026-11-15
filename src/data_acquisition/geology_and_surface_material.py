import asyncio
from typing import Any, Dict, List, Optional, Tuple
import httpx
from src.data_acquisition.utils import normalize_similarity


def _score_lithology(lith_text: str, preferred_keywords: List[str]) -> Tuple[float, str]:
    text = lith_text.lower()
    if not text or text == "unknown":
        return 0.45, "Unmapped bedrock unit (neutral baseline prior)"

    exact_matches = [kw for kw in preferred_keywords if kw in text]
    if len(exact_matches) >= 2:
        return 0.95, f"Strong lithological match ({', '.join(exact_matches)})"
    if len(exact_matches) == 1:
        return 0.85, f"Direct lithological match ({exact_matches[0]})"

    secondary = ["igneous", "sedimentary", "sandstone", "siltstone", "quartz", "clay", "carbonate", "metamorphic"]
    sec_matches = [kw for kw in secondary if kw in text]
    if sec_matches:
        return 0.55, f"Partial geological analog ({', '.join(sec_matches)})"

    return 0.30, "Low planetary lithological affinity"


async def _fetch_macrostrat(client: httpx.AsyncClient, lat: float, lon: float) -> Optional[Dict[str, str]]:
    try:
        r = await client.get(
            "https://macrostrat.org/api/v2/geologic_units/map",
            params={"lat": lat, "lng": lon},
            timeout=8.0,
        )
        r.raise_for_status()
        units = r.json().get("success", {}).get("data", [])
        if not units:
            return None
        top = units[0]
        return {
            "unit_name": top.get("strat_name_long") or top.get("name") or "Unnamed unit",
            "lithology": top.get("lith") or top.get("descrip") or "Unknown",
        }
    except Exception:
        return None


async def _fetch_soilgrids(client: httpx.AsyncClient, lat: float, lon: float) -> Optional[Dict[str, float]]:
    try:
        r = await client.get(
            "https://rest.isric.org/soilgrids/v2.0/properties/query",
            params={
                "lat": lat,
                "lon": lon,
                "property": ["sand", "clay"],
                "depth": "0-5cm",
                "value": "mean",
            },
            timeout=8.0,
        )
        r.raise_for_status()
        layers = r.json().get("properties", {}).get("layers", [])
        parsed: Dict[str, float] = {}
        for layer in layers:
            name = layer.get("name")
            depths = layer.get("depths", [])
            if depths:
                mean_val = depths[0].get("values", {}).get("mean")
                if mean_val is not None:
                    parsed[name] = round(mean_val / 10.0, 1)  # g/kg -> %
        return parsed if parsed else None
    except Exception:
        return None


async def get_geology_and_surface_material(
    client: httpx.AsyncClient, lat: float, lon: float, profile: Dict[str, Any]
) -> Dict[str, Any]:
    targets = profile["targets"]
    bedrock, topsoil = await asyncio.gather(
        _fetch_macrostrat(client, lat, lon),
        _fetch_soilgrids(client, lat, lon),
    )

    if not bedrock and not topsoil:
        return {
            "available": False,
            "normalized_score": None,
            "raw_metrics": {"error": "No geological or soil surface records at coordinate"},
            "target_reference": {},
            "evidence": {
                "source": "Macrostrat / SoilGrids v2.0",
                "spatial_resolution": "250 m+",
                "limitations": "Unmapped or ice/water covered",
            },
        }

    bedrock = bedrock or {}
    topsoil = topsoil or {}

    lith_str = bedrock.get("lithology", "Unknown")
    lith_score, lith_note = _score_lithology(lith_str, profile["preferred_lithologies"])

    if "sand" in topsoil:
        sand_score = normalize_similarity(
            topsoil["sand"], targets["sand_fraction_pct"]["value"], targets["sand_fraction_pct"]["range"]
        )
        combined_score = round(0.65 * lith_score + 0.35 * sand_score, 4) if bedrock else sand_score
    else:
        combined_score = lith_score

    return {
        "available": True,
        "normalized_score": combined_score,
        "raw_metrics": {
            "bedrock_unit": bedrock.get("unit_name", "Unmapped"),
            "lithology": lith_str,
            "lithology_assessment": lith_note,
            "topsoil_sand_pct": topsoil.get("sand"),
            "topsoil_clay_pct": topsoil.get("clay"),
        },
        "target_reference": {
            "preferred_lithologies": profile["preferred_lithologies"],
            "target_granular_sand_pct": targets["sand_fraction_pct"]["value"],
        },
        "evidence": {
            "source": "Macrostrat Geologic Map API & ISRIC SoilGrids v2.0",
            "spatial_resolution": "Regional polygon (Macrostrat) / 250 m (SoilGrids)",
            "limitations": "Earth weathering and organics alter regolith cohesion compared to anhydrous planetary soils.",
        },
    }
