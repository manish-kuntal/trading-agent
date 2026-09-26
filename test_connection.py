"""
Test Angel SmartAPI connection.
Run this FIRST before starting the agent.
  python test_connection.py
"""
import sys
from datetime import datetime, timedelta
import pandas as pd

def main():
    print("\n" + "="*50)
    print("  Angel SmartAPI — Connection Test")
    print("="*50 + "\n")

    # 1. Login
    print("1. Testing login...")
    from agent.execution.angel_broker import AngelBroker
    broker = AngelBroker()
    if not broker.login():
        print("   ❌ Login FAILED. Check .env credentials.\n")
        sys.exit(1)
    print("   ✅ Login OK")

    # 2. Symbol master
    print("\n2. Loading symbol master (first run downloads ~5MB)...")
    from agent.data.symbol_master import download_symbol_master
    master = download_symbol_master()
    print(f"   ✅ {len(master)} NSE symbols loaded")
    reliance_token = master.loc["RELIANCE-EQ", "token"]
    print(f"   ✅ RELIANCE-EQ token: {reliance_token}")

    # 3. LTP
    print("\n3. Testing LTP fetch...")
    ltp = broker.get_ltp("NSE", "RELIANCE-EQ", reliance_token)
    print(f"   ✅ RELIANCE LTP: ₹{ltp}")

    # 4. Historical candles
    print("\n4. Testing historical candles (5-min, last 3 days)...")
    to_dt   = datetime.now().strftime("%Y-%m-%d %H:%M")
    from_dt = (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d %H:%M")
    candles = broker.get_candles(reliance_token, "FIVE_MINUTE", from_dt, to_dt)
    df = pd.DataFrame(candles, columns=["ts","open","high","low","close","volume"])
    print(f"   ✅ {len(df)} candles received")
    print("   Last 3 rows:")
    print(df.tail(3).to_string(index=False))

    # 5. Feature computation
    print("\n5. Testing feature engineering...")
    from agent.data.features import get_latest_features
    features = get_latest_features(candles)
    print(f"   ✅ Features computed: {len(features)} values")
    for k in ["close", "RSI_14", "EMA_9", "EMA_21", "volume_ratio"]:
        if k in features:
            print(f"   {k}: {features[k]:.2f}")

    # 6. Positions
    print("\n6. Testing positions fetch...")
    pos = broker.get_positions()
    print(f"   ✅ Open positions: {len(pos)}")

    # 7. Risk manager
    print("\n7. Testing risk manager...")
    from config.settings import settings
    from agent.strategy.risk import RiskManager
    from agent.execution.virtual_broker import VirtualBroker
    vb   = VirtualBroker(capital=settings.paper_capital)
    vb.login()
    risk = RiskManager(vb)
    print(f"   ✅ Daily loss limit: ₹{settings.paper_capital * settings.daily_loss_limit_pct:,.0f}")
    print(f"   ✅ Max position size: ₹{settings.paper_capital * settings.max_position_pct:,.0f}")
    qty = risk.position_size(ltp)
    print(f"   ✅ Position size for RELIANCE @ ₹{ltp}: {qty} shares")

    print("\n" + "="*50)
    print("  ✅ ALL CHECKS PASSED — Ready to run agent!")
    print("  Next: python -m agent.main")
    print("="*50 + "\n")


if __name__ == "__main__":
    main()
