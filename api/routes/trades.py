from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from api.deps import get_db
from agent.db import repository

router = APIRouter(tags=["trades"])

@router.get("/trades")
def get_trades(days: int = Query(default=1), db: Session = Depends(get_db)):
    rows = repository.get_trade_history(db, days=days)
    data = [{"id": t.id, "symbol": t.symbol, "action": t.action, "qty": t.qty,
              "entry_price": t.entry_price, "exit_price": t.exit_price, "pnl": t.pnl,
              "signal_conf": t.signal_conf, "is_paper": t.is_paper,
              "status": "OPEN" if t.exit_price is None else "CLOSED",
              "entry_time": t.entry_time.isoformat() if t.entry_time else None,
              "exit_time":  t.exit_time.isoformat()  if t.exit_time  else None}
             for t in rows]
    return {"trades": data, "count": len(data)}
