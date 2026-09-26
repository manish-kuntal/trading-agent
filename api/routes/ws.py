import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
router = APIRouter()

@router.websocket("/ws/live")
async def live_feed(websocket: WebSocket):
    """Real-time P&L and position updates — Phase 6 mobile dashboard."""
    await websocket.accept()
    try:
        while True:
            # TODO: push actual broker state
            import json
            from datetime import datetime
            await websocket.send_text(json.dumps({
                "type": "heartbeat",
                "timestamp": datetime.utcnow().isoformat()
            }))
            await asyncio.sleep(2)
    except WebSocketDisconnect:
        pass
