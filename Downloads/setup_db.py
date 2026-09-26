"""
Run this from c:\trading-agent\
  python setup_db.py
Automatically updates all files for DB integration.
"""
import os

BASE = os.path.dirname(os.path.abspath(__file__))

files = {}

# ─────────────────────────────────────────────────────────────
files["agent/db/database.py"] = '''
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager

_engine       = None
_SessionLocal = None


def _init():
    global _engine, _SessionLocal
    if _engine is not None:
        return
    from config.settings import settings
    from agent.db.models import Base
    _engine = create_engine(
        settings.database_url,
        connect_args={"check_same_thread": False},
        pool_pre_ping=True
    )
    _SessionLocal = sessionmaker(bind=_engine, autocommit=False, autoflush=True)
    Base.metadata.create_all(bind=_engine)


@contextmanager
def get_session():
    """Use in agent code:  with get_session() as db: ..."""
    _init()
    db = _SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def get_db():
    """FastAPI dependency:  db: Session = Depends(get_db)"""
    _init()
    db = _SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
'''.lstrip()

# ─────────────────────────────────────────────────────────────
files["agent/db/models.py"] = '''
from sqlalchemy import Column, String, Float, Integer, DateTime, Boolean, Text
from sqlalchemy.orm import DeclarativeBase
from datetime import datetime


class Base(DeclarativeBase):
    pass


class Trade(Base):
    __tablename__ = "trades"
    id            = Column(Integer, primary_key=True, autoincrement=True)
    symbol        = Column(String(20), nullable=False, index=True)
    token         = Column(String(10), default="")
    action        = Column(String(4))
    qty           = Column(Integer)
    entry_price   = Column(Float)
    exit_price    = Column(Float, nullable=True)
    sl_price      = Column(Float, nullable=True)
    pnl           = Column(Float, nullable=True)
    signal_conf   = Column(Float, default=0.0)
    signal_reason = Column(Text,  default="")
    order_id      = Column(String(50), default="")
    is_paper      = Column(Boolean, default=True)
    entry_time    = Column(DateTime, default=datetime.now, index=True)
    exit_time     = Column(DateTime, nullable=True)


class OpenPosition(Base):
    __tablename__ = "open_positions"
    id          = Column(Integer, primary_key=True, autoincrement=True)
    symbol      = Column(String(20), nullable=False, unique=True)
    token       = Column(String(10), default="")
    qty         = Column(Integer)
    entry_price = Column(Float)
    sl_trigger  = Column(Float, nullable=True)
    is_paper    = Column(Boolean, default=True)
    entry_time  = Column(DateTime, default=datetime.now)
    updated_at  = Column(DateTime, default=datetime.now)


class DailyPnL(Base):
    __tablename__ = "daily_pnl"
    id           = Column(Integer, primary_key=True)
    date         = Column(String(10), unique=True, index=True)
    realized_pnl = Column(Float, default=0.0)
    trades_count = Column(Integer, default=0)
    win_count    = Column(Integer, default=0)
    capital_eod  = Column(Float, default=0.0)
    is_paper     = Column(Boolean, default=True)


class AgentLog(Base):
    __tablename__ = "agent_logs"
    id        = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.now, index=True)
    symbol    = Column(String(20), nullable=True)
    event     = Column(String(30))
    details   = Column(Text, default="")
    is_paper  = Column(Boolean, default=True)
'''.lstrip()

# ─────────────────────────────────────────────────────────────
files["agent/db/repository.py"] = '''
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
    t.pnl = round((exit_price - t.entry_price) * t.qty, 2) if t.action == "BUY" \
            else round((t.entry_price - exit_price) * t.qty, 2)


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
'''.lstrip()

# ─────────────────────────────────────────────────────────────
files["agent/execution/virtual_broker.py"] = '''
import uuid
from datetime import datetime
from loguru import logger
from .base_broker import BaseBroker


class VirtualBroker(BaseBroker):
    """Paper trading — real market data, virtual money, saves every trade to SQLite."""

    def __init__(self, capital: float = 100_000.0):
        self.initial_capital = capital
        self.capital         = capital
        self.positions: dict = {}
        self.trades:    list = []
        self._angel          = None

    def login(self) -> bool:
        from .angel_broker import AngelBroker
        from agent.db.database import get_session
        from agent.db import repository
        self._angel = AngelBroker()
        ok = self._angel.login()
        if ok:
            logger.info(f"[VirtualBroker] PAPER MODE — capital ₹{self.capital:,.0f}")
            with get_session() as db:
                repository.log_event(db, "LOGIN", details="Agent started (paper)")
        return ok

    def get_ltp(self, exchange, symbol, token) -> float:
        return self._angel.get_ltp(exchange, symbol, token)

    def get_candles(self, token, interval, from_date, to_date) -> list:
        return self._angel.get_candles(token, interval, from_date, to_date)

    def place_order(self, symbol, token, action, qty,
                    signal_conf=0.0, signal_reason="") -> str:
        from agent.db.database import get_session
        from agent.db import repository

        ltp      = self.get_ltp("NSE", symbol, token)
        order_id = f"V{uuid.uuid4().hex[:6].upper()}"

        if action == "BUY":
            if ltp * qty > self.capital:
                logger.warning(f"[Paper] Low capital — skipping {symbol}")
                return ""
            self.capital -= ltp * qty
            with get_session() as db:
                tid = repository.save_trade_entry(
                    db, symbol, token, "BUY", qty, ltp,
                    signal_conf=signal_conf, signal_reason=signal_reason,
                    order_id=order_id)
                repository.upsert_open_position(db, symbol, token, qty, ltp)
                repository.log_event(db, "ORDER", symbol,
                                     f"BUY {qty}x @ ₹{ltp} conf={signal_conf:.2f}")
            self.positions[symbol] = {
                "qty": qty, "entry_price": ltp, "token": token,
                "entry_time": datetime.now(), "sl_trigger": None, "trade_id": tid
            }
            logger.info(f"[Paper] BUY  {qty}x {symbol} @ ₹{ltp} | Capital ₹{self.capital:,.0f}")

        elif action == "SELL":
            if symbol not in self.positions:
                logger.warning(f"[Paper] No position in {symbol}")
                return ""
            pos = self.positions.pop(symbol)
            pnl = round((ltp - pos["entry_price"]) * qty, 2)
            self.capital += ltp * qty
            with get_session() as db:
                repository.update_trade_exit(db, pos["trade_id"], ltp)
                repository.remove_open_position(db, symbol)
                repository.log_event(db, "ORDER", symbol, f"SELL {qty}x @ ₹{ltp} PnL ₹{pnl:+.2f}")
            self.trades.append({"symbol": symbol, "pnl": pnl})
            logger.info(f"[Paper] SELL {qty}x {symbol} @ ₹{ltp} | PnL ₹{pnl:+.2f}")

        return order_id

    def place_stoploss(self, symbol, token, action, qty, trigger, price) -> str:
        from agent.db.database import get_session
        from agent.db import repository
        if symbol in self.positions:
            self.positions[symbol]["sl_trigger"] = trigger
            pos = self.positions[symbol]
            with get_session() as db:
                repository.upsert_open_position(db, symbol, token, pos["qty"],
                                                pos["entry_price"], sl_trigger=trigger)
        return f"VSL_{symbol}"

    def get_positions(self) -> list:
        result = []
        for symbol, pos in self.positions.items():
            try:
                ltp = self.get_ltp("NSE", symbol, pos["token"])
                unreal = round((ltp - pos["entry_price"]) * pos["qty"], 2)
            except Exception:
                ltp, unreal = pos["entry_price"], 0.0
            result.append({
                "tradingsymbol": symbol, "symboltoken": pos["token"],
                "netqty": str(pos["qty"]), "ltp": str(ltp),
                "unrealised": str(unreal), "entry_price": str(pos["entry_price"]),
            })
        return result

    def close_all_positions(self):
        from agent.db.database import get_session
        from agent.db import repository
        logger.info(f"[Paper] Squaring off {len(self.positions)} position(s)")
        for symbol, pos in list(self.positions.items()):
            self.place_order(symbol, pos["token"], "SELL", pos["qty"])
        with get_session() as db:
            closed = self.trades
            wins   = sum(1 for t in closed if t["pnl"] > 0)
            repository.save_daily_pnl(db, self.daily_pnl, len(closed), wins, self.total_value)

    @property
    def daily_pnl(self) -> float:
        return round(sum(t["pnl"] for t in self.trades), 2)

    @property
    def total_value(self) -> float:
        extra = 0.0
        for s, p in self.positions.items():
            try:
                extra += (self.get_ltp("NSE", s, p["token"]) - p["entry_price"]) * p["qty"]
            except Exception:
                pass
        return round(self.capital + extra, 2)

    def summary(self) -> dict:
        return {"capital": round(self.capital, 2), "initial_capital": self.initial_capital,
                "daily_pnl": self.daily_pnl, "total_value": self.total_value,
                "open_positions": len(self.positions), "trades_today": len(self.trades)}
'''.lstrip()

# ─────────────────────────────────────────────────────────────
files["agent/main.py"] = '''
import sys
from loguru import logger
from config.settings import settings
from agent.scheduler import setup_scheduler


def create_broker():
    if settings.paper_trading:
        from agent.execution.virtual_broker import VirtualBroker
        logger.info("=" * 50)
        logger.info("MODE: PAPER TRADING (no real money)")
        logger.info("=" * 50)
        return VirtualBroker(capital=settings.paper_capital)
    else:
        from agent.execution.angel_broker import AngelBroker
        logger.warning("=" * 50)
        logger.warning("MODE: LIVE TRADING — REAL MONEY")
        logger.warning("=" * 50)
        return AngelBroker()


def main():
    logger.remove()
    logger.add(sys.stdout, level="INFO",
               format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | {message}")
    logger.add("logs/agent_{time:YYYY-MM-DD}.log",
               rotation="1 day", retention="30 days", level="DEBUG")

    logger.info("Starting Trading Agent...")

    broker = create_broker()
    if not broker.login():
        logger.critical("Login failed. Exiting.")
        sys.exit(1)

    from agent.strategy.risk    import RiskManager
    from agent.strategy.signals import SignalEngine
    from agent.data.symbol_master import NIFTY50_WATCHLIST

    risk    = RiskManager(broker)
    signals = SignalEngine()
    scheduler = setup_scheduler(broker, risk, signals, NIFTY50_WATCHLIST)

    logger.info(f"Watching {len(NIFTY50_WATCHLIST)} symbols | Scheduler running. Ctrl+C to stop.")
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Agent stopped.")


if __name__ == "__main__":
    main()
'''.lstrip()

# ─────────────────────────────────────────────────────────────
files["api/deps.py"] = '''
from agent.db.database import get_db  # noqa — re-export for routes
'''.lstrip()

files["api/routes/positions.py"] = '''
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
'''.lstrip()

files["api/routes/trades.py"] = '''
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
'''.lstrip()

files["api/routes/pnl.py"] = '''
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
'''.lstrip()

# ─────────────────────────────────────────────────────────────
# Write all files
ok, fail = 0, 0
for rel_path, content in files.items():
    abs_path = os.path.join(BASE, rel_path)
    os.makedirs(os.path.dirname(abs_path), exist_ok=True)
    try:
        with open(abs_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"  ✅ {rel_path}")
        ok += 1
    except Exception as e:
        print(f"  ❌ {rel_path} — {e}")
        fail += 1

print(f"\n{'='*40}")
print(f"  {ok} files updated, {fail} failed")
if fail == 0:
    print("  Run: python -m agent.main")
    print("  Run: python -m uvicorn api.main:app --port 8000")
print(f"{'='*40}")
