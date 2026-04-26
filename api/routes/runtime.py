"""
BharatGraph - Phase 31: /runtime endpoint
Returns current hardware detection results and active profile settings.
Pure ASCII.
"""
from fastapi import APIRouter
from config.runtime_profile import PROFILE

router = APIRouter()


@router.get("/runtime")
def get_runtime_profile():
    """
    Returns the auto-detected hardware profile and active settings.
    Useful for debugging deployment performance issues.
    Force a profile by setting: BHARATGRAPH_PROFILE=low|medium|high
    """
    return PROFILE.to_dict()
