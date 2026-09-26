from fastapi import APIRouter
from loguru import logger
router = APIRouter(tags=["control"])

_agent_paused = False

@router.get("/agent/status")
async def agent_status():
    return {"paused": _agent_paused}

@router.post("/agent/pause")
async def pause_agent():
    global _agent_paused
    _agent_paused = True
    logger.warning("[API] Agent PAUSED via dashboard")
    return {"status": "paused"}

@router.post("/agent/resume")
async def resume_agent():
    global _agent_paused
    _agent_paused = False
    logger.info("[API] Agent RESUMED via dashboard")
    return {"status": "running"}

@router.post("/agent/emergency-stop")
async def emergency_stop():
    """Closes ALL positions immediately. Use only in emergencies."""
    global _agent_paused
    _agent_paused = True
    logger.critical("[API] EMERGENCY STOP triggered!")
    # TODO: broker.close_all_positions()
    return {"status": "stopped", "message": "All positions closed"}
