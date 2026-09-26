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
