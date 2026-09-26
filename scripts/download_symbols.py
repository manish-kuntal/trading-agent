"""One-time script to download and cache NSE symbol master."""
from agent.data.symbol_master import download_symbol_master
df = download_symbol_master(force=True)
print(f"Downloaded {len(df)} NSE symbols.")
print(df.head(5))
