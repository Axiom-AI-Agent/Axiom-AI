"""Legacy alias — prefer /dashboard/escalations."""

from api.routers.dashboard.escalations import router

__all__ = ["router"]
