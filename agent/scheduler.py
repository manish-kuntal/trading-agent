"""
Market Hours Scheduler
----------------------
All IST-aware cron jobs for the agent.
"""
import pytz
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from loguru import logger

IST = pytz.timezone("Asia/Kolkata")


def setup_scheduler(broker, risk, signals, watchlist: dict):
    scheduler = BlockingScheduler(timezone=IST)

    # ------------------------------------------------------------------
    def refresh_session():
        logger.info("[Scheduler] Refreshing daily session...")
        if not broker.login():
            logger.error("[Scheduler] Session refresh FAILED — check credentials!")

    def market_open():
        logger.info("[Scheduler] === MARKET OPEN 9:15 AM ===")
        risk.reset_daily()

    def scan_all():
        """Main agent loop — runs every 5 minutes 9:20 AM – 3:10 PM."""
        if not risk.is_market_hours():
            return
        if risk.daily_loss_exceeded():
            logger.warning("[Scan] Daily loss cap hit — skipping scan.")
            return

        from datetime import timedelta
        from agent.data.features import get_latest_features

        now_str  = datetime.now(IST).strftime("%Y-%m-%d %H:%M")
        from_str = (datetime.now(IST) - timedelta(days=3)).strftime("%Y-%m-%d %H:%M")

        for symbol, token in watchlist.items():
            try:
                if not risk.can_open_position():
                    break  # Max positions reached

                candles  = broker.get_candles(token, "FIVE_MINUTE", from_str, now_str)
                if len(candles) < 50:
                    continue

                features = get_latest_features(candles)
                signal   = signals.generate(features)

                logger.debug(
                    f"[{symbol}] {signal.action} conf={signal.confidence:.2f} | {signal.reason}"
                )

                if signal.action == "HOLD" or signal.confidence < 0.65:
                    continue

                # Check if already in position
                positions = broker.get_positions()
                in_pos    = any(p["tradingsymbol"] == symbol for p in positions
                                if int(p.get("netqty", 0)) != 0)
                if in_pos:
                    continue

                qty = risk.position_size(features["close"])
                order_id = broker.place_order(symbol, token, signal.action, qty)

                if order_id:
                    trigger, limit = risk.calc_stoploss(features["close"], signal.action)
                    sl_action = "SELL" if signal.action == "BUY" else "BUY"
                    broker.place_stoploss(symbol, token, sl_action, qty, trigger, limit)

            except Exception as e:
                logger.error(f"[Scan] Error on {symbol}: {e}")

    def check_paper_sl():
        """For VirtualBroker: check SL levels every minute."""
        if hasattr(broker, "positions"):
            risk.check_paper_sl()

    def square_off():
        logger.info("[Scheduler] === 3:15 PM SQUARE OFF ===")
        broker.close_all_positions()

    def end_of_day():
        logger.info("[Scheduler] === MARKET CLOSE 3:30 PM ===")
        if hasattr(broker, "summary"):
            s = broker.summary()
            logger.info(
                f"EOD Summary | PnL: ₹{s['daily_pnl']:+.2f} | "
                f"Trades: {s['trades_today']} | "
                f"Capital: ₹{s['total_value']:,.0f}"
            )

    # ------------------------------------------------------------------
    # Schedule jobs
    scheduler.add_job(refresh_session, "cron", hour=9,  minute=0)
    scheduler.add_job(market_open,     "cron", hour=9,  minute=15)
    # Scan every 5 min from 9:20 to 3:10
    scheduler.add_job(scan_all,        "cron",
                      hour="9-15", minute="20,25,30,35,40,45,50,55,0,5,10")
    scheduler.add_job(check_paper_sl,  "cron",
                      hour="9-15", minute="*")   # every minute
    scheduler.add_job(square_off,      "cron", hour=15, minute=15)
    scheduler.add_job(end_of_day,      "cron", hour=15, minute=30)

    return scheduler
