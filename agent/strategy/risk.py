"""
Risk Management Gate
--------------------
Every order MUST pass through this before execution.
Hard limits that cannot be overridden by strategy.
"""
from datetime import datetime
import pytz
from loguru import logger
from config.settings import settings

IST = pytz.timezone("Asia/Kolkata")


class RiskManager:

    def __init__(self, broker):
        self.broker              = broker
        self._daily_loss_hit     = False

    # ------------------------------------------------------------------
    def daily_loss_exceeded(self) -> bool:
        """Check P&L against daily loss cap. Once hit, stays True all day."""
        if self._daily_loss_hit:
            return True

        pnl = getattr(self.broker, "daily_pnl", 0.0)
        cap = getattr(self.broker, "initial_capital",
                      getattr(self.broker, "capital", settings.paper_capital))
        limit = cap * settings.daily_loss_limit_pct

        if pnl <= -abs(limit):
            logger.critical(
                f"DAILY LOSS LIMIT HIT: ₹{pnl:.2f} >= -₹{limit:.2f} | "
                f"Closing all positions."
            )
            self._daily_loss_hit = True
            self.broker.close_all_positions()
        return self._daily_loss_hit

    def can_open_position(self) -> bool:
        """Check max concurrent positions."""
        positions = self.broker.get_positions()
        open_count = sum(1 for p in positions if int(p.get("netqty", 0)) != 0)
        if open_count >= settings.max_open_positions:
            logger.debug(f"Max positions reached: {open_count}/{settings.max_open_positions}")
            return False
        return True

    def is_market_hours(self) -> bool:
        """True only during 9:15 AM – 3:15 PM IST on weekdays."""
        now = datetime.now(IST)
        if now.weekday() >= 5:           # Saturday / Sunday
            return False
        open_t  = now.replace(hour=9,  minute=15, second=0, microsecond=0)
        close_t = now.replace(hour=15, minute=15, second=0, microsecond=0)
        return open_t <= now <= close_t

    def is_square_off_time(self) -> bool:
        now = datetime.now(IST)
        return now.hour > settings.square_off_hour or (
            now.hour == settings.square_off_hour and
            now.minute >= settings.square_off_minute
        )

    # ------------------------------------------------------------------
    def position_size(self, ltp: float) -> int:
        """Fixed-fractional: max_position_pct of available capital."""
        capital = getattr(self.broker, "capital",
                          getattr(self.broker, "initial_capital", settings.paper_capital))
        max_value = capital * settings.max_position_pct
        qty = int(max_value / ltp)
        return max(qty, 1)

    def calc_stoploss(self, entry_price: float,
                      action: str) -> tuple[float, float]:
        """
        Returns (trigger_price, limit_price) for SL-Limit order.
        Buffer of ₹0.50 between trigger and limit avoids partial fills.
        """
        sl_amt = entry_price * settings.stop_loss_pct
        if action == "BUY":
            trigger = round(entry_price - sl_amt, 2)
            limit   = round(trigger - 0.50, 2)
        else:
            trigger = round(entry_price + sl_amt, 2)
            limit   = round(trigger + 0.50, 2)
        return trigger, limit

    def check_paper_sl(self):
        """
        For VirtualBroker: manually check if any position hit its SL.
        Call every candle close from the main loop.
        """
        if not hasattr(self.broker, "positions"):
            return
        for symbol, pos in list(self.broker.positions.items()):
            sl = pos.get("sl_trigger")
            if sl is None:
                continue
            ltp = self.broker.get_ltp("NSE", symbol, pos["token"])
            if ltp <= sl:
                logger.warning(f"[Paper SL] {symbol} LTP ₹{ltp} hit SL ₹{sl}")
                self.broker.place_order(symbol, pos["token"], "SELL", pos["qty"])

    def reset_daily(self):
        """Call at EOD / 3:30 PM to reset for next trading day."""
        self._daily_loss_hit = False
        logger.info("Risk manager reset for new trading day.")
