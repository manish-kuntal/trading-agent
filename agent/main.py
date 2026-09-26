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
