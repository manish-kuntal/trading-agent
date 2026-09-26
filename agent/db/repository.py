from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session
from agent.db.models import Trade, OpenPosition, DailyPnL, AgentLog


def save_trade_entry(db, symbol, token, action, qty, entry_price,
                     signal_conf=0.0, signal_reason="",
                     order_id="", is_paper=True) -> int:
    t = Trade(symbol=symbol, token=token, action=action, qty=qty,
              entry_price=entry_price, signal_conf=signal_conf,
              signal_reason=signal_reason, order_id=order_id,
              is_paper=is_paper, entry_time=datetime.now())
    db.add(t)
    db.flush()
    return t.id


def update_trade_exit(db, trade_id: int, exit_price: float):
    t = db.query(Trade).filter(Trade.id == trade_id).first()
    if not t:
        return
    t.exit_price = exit_price
    t.exit_time  = datetime.now()
    t.pnl = round((exit_price - t.entry_price) * t.qty, 2) if t.action == "BUY"             else round((t.entry_price - exit_price) * t.qty, 2)


def upsert_open_position(db, symbol, token, qty, entry_price,
                          sl_trigger=None, is_paper=True):
    pos = db.query(OpenPosition).filter(OpenPosition.symbol == symbol).first()
    if pos:
        pos.qty = qty; pos.sl_trigger = sl_trigger; pos.updated_at = datetime.now()
    else:
        db.add(OpenPosition(symbol=symbol, token=token, qty=qty,
                            entry_price=entry_price, sl_trigger=sl_trigger,
                            is_paper=is_paper, entry_time=datetime.now()))


def remove_open_position(db, symbol: str):
    db.query(OpenPosition).filter(OpenPosition.symbol == symbol).delete()


def get_open_positions(db) -> list:
    return db.query(OpenPosition).all()


def get_today_trades(db, is_paper=True) -> list:
    start = datetime.combine(date.today(), datetime.min.time())
    return (db.query(Trade)
              .filter(Trade.entry_time >= start, Trade.is_paper == is_paper)
              .order_by(Trade.entry_time.desc()).all())


def get_trade_history(db, days=1) -> list:
    from_dt = datetime.now() - timedelta(days=days)
    return (db.query(Trade)
              .filter(Trade.entry_time >= from_dt)
              .order_by(Trade.entry_time.desc()).all())


def get_today_pnl(db, is_paper=True) -> dict:
    trades = get_today_trades(db, is_paper)
    closed = [t for t in trades if t.pnl is not None]
    realized = round(sum(t.pnl for t in closed), 2)
    wins = sum(1 for t in closed if t.pnl > 0)
    return {
        "date":         date.today().isoformat(),
        "realized_pnl": realized,
        "trades_count": len(trades),
        "closed_count": len(closed),
        "open_count":   len(trades) - len(closed),
        "win_count":    wins,
        "win_rate":     round(wins / len(closed) * 100, 1) if closed else 0.0,
    }


def get_pnl_history(db, days=30) -> list:
    from_date = (date.today() - timedelta(days=days)).isoformat()
    return (db.query(DailyPnL)
              .filter(DailyPnL.date >= from_date)
              .order_by(DailyPnL.date.desc()).all())


def save_daily_pnl(db, realized_pnl, trades_count, win_count, capital_eod, is_paper=True):
    today = date.today().isoformat()
    row = db.query(DailyPnL).filter(DailyPnL.date == today).first()
    if row:
        row.realized_pnl = realized_pnl; row.trades_count = trades_count
        row.win_count = win_count;       row.capital_eod  = capital_eod
    else:
        db.add(DailyPnL(date=today, realized_pnl=realized_pnl,
                        trades_count=trades_count, win_count=win_count,
                        capital_eod=capital_eod, is_paper=is_paper))


def log_event(db, event, symbol=None, details="", is_paper=True):
    db.add(AgentLog(event=event, symbol=symbol, details=details, is_paper=is_paper))
