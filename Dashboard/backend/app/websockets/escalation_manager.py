from collections import defaultdict
from typing import DefaultDict

from fastapi import WebSocket


class EscalationConnectionManager:
    def __init__(self) -> None:
        self.connections: DefaultDict[str, list[WebSocket]] = defaultdict(list)

    async def connect(
        self,
        tenant_id: str,
        websocket: WebSocket,
    ) -> None:
        await websocket.accept()
        self.connections[tenant_id].append(websocket)

    def disconnect(
        self,
        tenant_id: str,
        websocket: WebSocket,
    ) -> None:
        tenant_connections = self.connections.get(tenant_id, [])

        if websocket in tenant_connections:
            tenant_connections.remove(websocket)

        if not tenant_connections:
            self.connections.pop(tenant_id, None)

    async def broadcast(
        self,
        tenant_id: str,
        message: dict,
    ) -> None:
        disconnected: list[WebSocket] = []

        for websocket in list(self.connections.get(tenant_id, [])):
            try:
                await websocket.send_json(message)
            except Exception:
                disconnected.append(websocket)

        for websocket in disconnected:
            self.disconnect(tenant_id, websocket)


escalation_manager = EscalationConnectionManager()