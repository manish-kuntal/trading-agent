from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from api.deps import get_db
from agent.db import repository

router = APIRouter(tags=["pnl"])

@router.get("/pnl/today")
def today_pnl(db: Session = Depends(get_db)):
    return repository.get_today_pnl(db, is_paper=True)

@router.get("/pnl/history")
def pnl_history(days: int = Query(default=30), db: Session = Depends(get_db)):
    rows = repository.get_pnl_history(db, days=days)
    data = [{"date": r.date, "realized_pnl": r.realized_pnl,
              "trades_count": r.trades_count, "win_count": r.win_count,
              "capital_eod": r.capital_eod} for r in rows]
    return {"history": data}
