from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import positions, trades, pnl, control, ws

app = FastAPI(title="Trading Agent API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # lock down in Phase 5/6
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(positions.router, prefix="/api/v1")
app.include_router(trades.router,    prefix="/api/v1")
app.include_router(pnl.router,       prefix="/api/v1")
app.include_router(control.router,   prefix="/api/v1")
app.include_router(ws.router)

@app.get("/health")
async def health():
    from datetime import datetime
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}
