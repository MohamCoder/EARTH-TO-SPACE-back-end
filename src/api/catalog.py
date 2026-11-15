from fastapi import APIRouter
from config.profiles import CANDIDATE_SITES, TARGET_PROFILES

router = APIRouter(tags=["Catalog"])


@router.get("/targets")
def list_target_profiles():
    """Returns all available Moon & Mars mission profiles and their default weights."""
    return {
        k: {
            "name": v["name"],
            "body": v["body"],
            "description": v["description"],
            "default_weights": v["weights"],
        }
        for k, v in TARGET_PROFILES.items()
    }


@router.get("/candidates")
def list_candidate_sites():
    """Returns the 7 baseline terrestrial analog candidate sites."""
    return {"candidates": CANDIDATE_SITES}
