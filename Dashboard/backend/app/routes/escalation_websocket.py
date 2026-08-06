from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect

from app.websockets.escalation_manager import escalation_manager

router = APIRouter(tags=["Escalation WebSocket"])


@router.websocket("/ws/escalations")
async def escalation_websocket(
    websocket: WebSocket,
    tenant_id: str = Query(...),
) -> None:
    await escalation_manager.connect(tenant_id, websocket)

    await websocket.send_json(
        {
            "type": "connection.ready",
            "tenant_id": tenant_id,
        }
    )

    try:
        while True:
            # Keeps the connection open and allows optional client pings.
            message = await websocket.receive_text()

            if message == "ping":
                await websocket.send_json({"type": "pong"})

    except WebSocketDisconnect:
        escalation_manager.disconnect(tenant_id, websocket)

    except Exception:
        escalation_manager.disconnect(tenant_id, websocket)