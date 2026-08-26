"""Dashboard REST routers."""

from api.routers.dashboard.broadcast import router as broadcast_router
from api.routers.dashboard.chat import router as chat_router
from api.routers.dashboard.chat_logs import router as chat_logs_router
from api.routers.dashboard.escalations import router as escalations_router
from api.routers.dashboard.overview import router as overview_router

__all__ = [
    "broadcast_router",
    "chat_router",
    "chat_logs_router",
    "escalations_router",
    "overview_router",
]
