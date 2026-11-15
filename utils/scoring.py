from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class CriterionOutput(BaseModel):
    criterion: str
    available: bool
    normalized_score: Optional[float] = Field(None, description="0.0 to 1.0 similarity score")
    assigned_weight: float
    effective_weight: float
    weighted_score: Optional[float] = Field(None, description="effective_weight * normalized_score")
    raw_metrics: Dict[str, Any]
    target_reference: Dict[str, Any]
    evidence: Dict[str, str]


class AnalogAnalysisResponse(BaseModel):
    coordinates: Dict[str, float]
    target_profile: str
    target_name: str
    planetary_body: str
    illustrative_weighted_score: float = Field(..., description="Overall 0.0-1.0 similarity score")
    illustrative_score_pct: float = Field(..., description="Percentage score (0-100%)")
    data_coverage: Dict[str, Any]
    criteria: Dict[str, CriterionOutput]
    scientific_disclaimer: str


def build_analog_response(
    lat: float,
    lon: float,
    target_key: str,
    profile: Dict[str, Any],
    weights: Dict[str, float],
    raw_criteria: Dict[str, Dict[str, Any]],
) -> AnalogAnalysisResponse:
    available_keys = [k for k, v in raw_criteria.items() if v["available"]]
    active_weight_sum = sum(weights[k] for k in available_keys)

    formatted_criteria: Dict[str, CriterionOutput] = {}
    overall_score = 0.0

    for k, item in raw_criteria.items():
        assigned_w = weights[k]
        if item["available"] and active_weight_sum > 0:
            eff_w = round(assigned_w / active_weight_sum, 4)
            w_score = round(eff_w * item["normalized_score"], 4)
            overall_score += w_score
        else:
            eff_w = 0.0
            w_score = None

        formatted_criteria[k] = CriterionOutput(
            criterion=k,
            available=item["available"],
            normalized_score=item["normalized_score"],
            assigned_weight=round(assigned_w, 4),
            effective_weight=eff_w,
            weighted_score=w_score,
            raw_metrics=item["raw_metrics"],
            target_reference=item["target_reference"],
            evidence=item["evidence"],
        )

    overall_score = round(overall_score, 4)

    return AnalogAnalysisResponse(
        coordinates={"lat": lat, "lon": lon},
        target_profile=target_key,
        target_name=profile["name"],
        planetary_body=profile["body"],
        illustrative_weighted_score=overall_score,
        illustrative_score_pct=round(overall_score * 100.0, 2),
        data_coverage={
            "available_criteria": len(available_keys),
            "total_criteria": 5,
            "coverage_ratio": round(len(available_keys) / 5.0, 2),
            "missing_criteria": [k for k in raw_criteria if k not in available_keys],
        },
        criteria=formatted_criteria,
        scientific_disclaimer=(
            "Decision-support index only. Terrestrial analogs replicate specific geological, thermal, "
            "or terrain properties and do not reproduce planetary gravity, atmospheric pressure, or radiation."
        ),
    )
