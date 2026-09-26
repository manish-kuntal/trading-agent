from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from api.deps import get_db
from agent.db import repository

router = APIRouter(tags=["positions"])

@router.get("/positions")
def get_positions(db: Session = Depends(get_db)):
    rows = repository.get_open_positions(db)
    data = [{"symbol": r.symbol, "qty": r.qty, "entry_price": r.entry_price,
              "sl_trigger": r.sl_trigger, "is_paper": r.is_paper,
              "entry_time": r.entry_time.isoformat() if r.entry_time else None}
             for r in rows]
    return {"positions": data, "count": len(data)}
