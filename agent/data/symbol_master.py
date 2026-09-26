"""
NSE Symbol Master
-----------------
Download token list ONCE and cache locally.
Angel SmartAPI needs token numbers, not just ticker names.
"""
import json
import requests
import pandas as pd
from pathlib import Path
from loguru import logger

MASTER_URL  = "https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json"
CACHE_PATH  = Path("data/cache/nse_symbols.parquet")


def download_symbol_master(force: bool = False) -> pd.DataFrame:
    """
    Returns DataFrame with columns: symbol, token, name
    Indexed by symbol (e.g. 'RELIANCE-EQ').
    Cached locally — re-download only if force=True or file missing.
    """
    if CACHE_PATH.exists() and not force:
        logger.info(f"Loading symbol master from cache: {CACHE_PATH}")
        return pd.read_parquet(CACHE_PATH).set_index("symbol")

    logger.info("Downloading NSE symbol master...")
    resp = requests.get(MASTER_URL, timeout=30)
    df   = pd.DataFrame(resp.json())

    nse_eq = df[
        (df["exch_seg"] == "NSE") &
        (df["symbol"].str.endswith("-EQ"))
    ][["symbol", "token", "name", "lotsize"]].copy()

    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    nse_eq.to_parquet(CACHE_PATH, index=False)
    logger.info(f"Cached {len(nse_eq)} NSE symbols → {CACHE_PATH}")

    return nse_eq.set_index("symbol")


def get_token(symbol: str, master: pd.DataFrame = None) -> str:
    """Quick lookup: get_token('RELIANCE-EQ') → '2885'"""
    if master is None:
        master = download_symbol_master()
    sym = symbol if symbol.endswith("-EQ") else f"{symbol}-EQ"
    return master.loc[sym, "token"]


# Nifty 50 watchlist — pre-filled tokens (stable, rarely change)
NIFTY50_WATCHLIST: dict[str, str] = {
    "RELIANCE-EQ":    "2885",
    "HDFCBANK-EQ":    "1333",
    "INFY-EQ":        "1594",
    "TCS-EQ":         "11536",
    "ICICIBANK-EQ":   "4963",
    "SBIN-EQ":        "3045",
    "BHARTIARTL-EQ":  "10604",
    "ADANIENT-EQ":    "25",
    "WIPRO-EQ":       "3787",
    "AXISBANK-EQ":    "5900",
    "LT-EQ":          "11483",
    "KOTAKBANK-EQ":   "1922",
    "BAJFINANCE-EQ":  "317",
    "HCLTECH-EQ":     "7229",
    "TITAN-EQ":       "3506",
}
