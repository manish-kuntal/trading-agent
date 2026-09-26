"""
Feature Engineering
-------------------
Takes raw OHLCV candle list → pandas DataFrame with TA indicators.
All indicators via pandas-ta (no TA-Lib install required).
"""
import pandas as pd
import pandas_ta as ta
from loguru import logger


def candles_to_df(candles: list) -> pd.DataFrame:
    """Convert Angel API candle list to DataFrame."""
    df = pd.DataFrame(candles, columns=["timestamp", "open", "high", "low", "close", "volume"])
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.set_index("timestamp")
    df = df.astype(float)
    return df


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add all TA indicators used by the signal engine.
    Requires at least 50 candles for reliable values.
    """
    if len(df) < 50:
        logger.warning(f"Only {len(df)} candles — some indicators may be NaN")

    # Trend
    df.ta.ema(length=9,  append=True)    # EMA_9
    df.ta.ema(length=21, append=True)    # EMA_21
    df.ta.ema(length=50, append=True)    # EMA_50
    df.ta.vwap(append=True)              # VWAP_D

    # Momentum
    df.ta.rsi(length=14, append=True)    # RSI_14
    df.ta.macd(append=True)              # MACD_12_26_9, MACDs, MACDh

    # Volatility
    df.ta.bbands(length=20, append=True) # BBL, BBM, BBU, BBB, BBP
    df.ta.atr(length=14, append=True)    # ATRr_14

    # Volume
    df["volume_ma20"] = df["volume"].rolling(20).mean()
    df["volume_ratio"] = df["volume"] / df["volume_ma20"].replace(0, 1)

    # Price action
    df["candle_body"]  = (df["close"] - df["open"]).abs()
    df["candle_range"] = df["high"] - df["low"]
    df["body_ratio"]   = df["candle_body"] / df["candle_range"].replace(0, 1)

    df.dropna(inplace=True)
    return df


def get_latest_features(candles: list) -> dict:
    """Returns the most recent row as a plain dict for signal engine."""
    df  = add_indicators(candles_to_df(candles))
    row = df.iloc[-1].to_dict()
    row["prev_close"] = df.iloc[-2]["close"] if len(df) > 1 else row["close"]
    return row
