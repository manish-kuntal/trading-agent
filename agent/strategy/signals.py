"""
Signal Engine
-------------
Takes feature dict → BUY / SELL / HOLD + confidence score.

Approach (3-layer):
  Layer 1: Rule-based TA signals  (weight: 0.4)
  Layer 2: ML model (XGBoost)     (weight: 0.4)  [Phase 2+]
  Layer 3: LLM filter             (weight: 0.2)  [Phase 2+]
"""
from dataclasses import dataclass
from pathlib import Path
import joblib
from loguru import logger


@dataclass
class Signal:
    action:     str    # BUY | SELL | HOLD
    confidence: float  # 0.0 – 1.0
    reason:     str    # human-readable explanation


MODEL_PATH = Path("ml/models/signal_model.pkl")


class SignalEngine:

    def __init__(self):
        self.ml_model = None
        self._load_model()

    def _load_model(self):
        if MODEL_PATH.exists():
            self.ml_model = joblib.load(MODEL_PATH)
            logger.info("ML signal model loaded.")
        else:
            logger.warning("No ML model found — rule-based signals only (Phase 1 OK).")

    # ------------------------------------------------------------------
    def generate(self, features: dict) -> Signal:
        """Main entry point. Returns best signal."""
        rule_signal, rule_conf  = self._rule_based(features)
        ml_signal,   ml_conf    = self._ml_signal(features) if self.ml_model else (rule_signal, 0.0)

        # Weighted aggregation
        if self.ml_model:
            if rule_signal == ml_signal:
                confidence = rule_conf * 0.4 + ml_conf * 0.6
            else:
                # Conflicting signals → hold with low confidence
                return Signal("HOLD", 0.3, "Rule/ML conflict")
        else:
            confidence = rule_conf

        reason = self._build_reason(features, rule_signal)
        return Signal(rule_signal if not self.ml_model else ml_signal,
                      round(confidence, 3), reason)

    # ------------------------------------------------------------------
    def _rule_based(self, f: dict) -> tuple[str, float]:
        """
        Simple rules — a baseline that always runs.
        Add / tune these as you backtest.
        """
        signals = []

        # Rule 1: EMA crossover
        ema9  = f.get("EMA_9",  0)
        ema21 = f.get("EMA_21", 0)
        if ema9 > ema21:   signals.append(("BUY",  0.6))
        elif ema9 < ema21: signals.append(("SELL", 0.6))

        # Rule 2: Price vs VWAP
        close = f.get("close",  0)
        vwap  = f.get("VWAP_D", close)
        if close > vwap * 1.002: signals.append(("BUY",  0.65))
        elif close < vwap * 0.998: signals.append(("SELL", 0.65))

        # Rule 3: RSI
        rsi = f.get("RSI_14", 50)
        if rsi < 35:   signals.append(("BUY",  0.7))
        elif rsi > 65: signals.append(("SELL", 0.7))

        # Rule 4: MACD histogram cross
        macdh     = f.get("MACDh_12_26_9", 0)
        prev_macdh= f.get("prev_macdh", 0)  # set by fetcher if available
        if prev_macdh <= 0 < macdh:  signals.append(("BUY",  0.75))
        elif prev_macdh >= 0 > macdh: signals.append(("SELL", 0.75))

        # Rule 5: Volume confirmation
        vol_ratio = f.get("volume_ratio", 1.0)
        if vol_ratio < 0.8:   # Low volume = weak signal
            signals = [(s, c * 0.7) for s, c in signals]

        if not signals:
            return "HOLD", 0.0

        buys  = [c for s, c in signals if s == "BUY"]
        sells = [c for s, c in signals if s == "SELL"]

        if len(buys) > len(sells):
            return "BUY",  sum(buys) / len(buys)
        elif len(sells) > len(buys):
            return "SELL", sum(sells) / len(sells)
        return "HOLD", 0.0

    def _ml_signal(self, features: dict) -> tuple[str, float]:
        """XGBoost prediction. Placeholder until model is trained."""
        try:
            feat_cols = [
                "RSI_14", "MACD_12_26_9", "MACDh_12_26_9",
                "EMA_9", "EMA_21", "BBP_5_2.0", "ATRr_14",
                "volume_ratio", "body_ratio",
            ]
            X = [[features.get(c, 0) for c in feat_cols]]
            proba = self.ml_model.predict_proba(X)[0]
            label = self.ml_model.classes_[proba.argmax()]
            return label, float(proba.max())
        except Exception as e:
            logger.warning(f"ML predict failed: {e}")
            return "HOLD", 0.0

    def _build_reason(self, f: dict, action: str) -> str:
        return (
            f"{action} | RSI={f.get('RSI_14', 0):.1f} "
            f"EMA9={f.get('EMA_9', 0):.1f} "
            f"VWAP={f.get('VWAP_D', 0):.1f} "
            f"Vol×{f.get('volume_ratio', 1):.1f}"
        )
