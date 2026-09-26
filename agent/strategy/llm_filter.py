"""
LLM Filter — supports 3 providers (priority order):
  1. Google Gemini API   (USE_GEMINI=true)
  2. Local Ollama/Qwen3  (USE_LOCAL_LLM=true)
  3. Anthropic Claude    (fallback)
"""
import json
import httpx
from loguru import logger
from config.settings import settings

PROMPT_TEMPLATE = """You are an intraday trading assistant for NSE Indian stock market.
Analyze this data and reply with ONLY a JSON object, no extra text, no markdown.

Stock: {symbol}
Price: ₹{ltp}
Signal: {signal} (confidence: {confidence:.0%})
RSI: {rsi:.1f} | EMA9: {ema9:.1f} | EMA21: {ema21:.1f} | VWAP: {vwap:.1f}
Volume ratio: {vol_ratio:.1f}x average

Reply format (JSON only, no backticks):
{{"decision": "BUY", "reason": "one sentence"}}
decision must be exactly one of: BUY, SELL, HOLD"""


class LLMFilter:

    def __init__(self):
        self.enabled = True

    def _build_prompt(self, symbol, signal_action, confidence, features) -> str:
        return PROMPT_TEMPLATE.format(
            symbol=symbol,
            ltp=features.get("close", 0),
            signal=signal_action,
            confidence=confidence,
            rsi=features.get("RSI_14", 50),
            ema9=features.get("EMA_9", 0),
            ema21=features.get("EMA_21", 0),
            vwap=features.get("VWAP_D", 0),
            vol_ratio=features.get("volume_ratio", 1.0),
        )

    def _parse(self, text: str, fallback: str) -> tuple[str, str]:
        try:
            text = text.strip().strip("```json").strip("```").strip()
            data = json.loads(text)
            decision = data.get("decision", fallback).upper()
            if decision not in ("BUY", "SELL", "HOLD"):
                decision = fallback
            return decision, data.get("reason", "")
        except Exception:
            return fallback, "parse error"

    # ── GEMINI ────────────────────────────────────────────────────────
    async def _gemini(self, prompt: str, fallback: str) -> tuple[str, str]:
        try:
            import google.generativeai as genai
            genai.configure(api_key=settings.gemini_api_key)
            model = genai.GenerativeModel(settings.gemini_model)
            resp  = model.generate_content(
                prompt,
                generation_config={"temperature": 0.1, "max_output_tokens": 100}
            )
            return self._parse(resp.text, fallback)
        except Exception as e:
            logger.warning(f"[Gemini] Failed: {e}")
            return fallback, "Gemini unavailable"

    # ── OLLAMA (local Qwen3) ──────────────────────────────────────────
    async def _ollama(self, prompt: str, fallback: str) -> tuple[str, str]:
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.post(
                    f"{settings.ollama_base_url}/api/generate",
                    json={"model": settings.ollama_model,
                          "prompt": prompt, "stream": False,
                          "options": {"temperature": 0.1}}
                )
            return self._parse(resp.json()["response"], fallback)
        except Exception as e:
            logger.warning(f"[Ollama] Failed: {e}")
            return fallback, "Ollama unavailable"

    # ── CLAUDE ────────────────────────────────────────────────────────
    async def _claude(self, prompt: str, fallback: str) -> tuple[str, str]:
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
            msg = client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=100,
                messages=[{"role": "user", "content": prompt}]
            )
            return self._parse(msg.content[0].text, fallback)
        except Exception as e:
            logger.warning(f"[Claude] Failed: {e}")
            return fallback, "Claude unavailable"

    # ── MAIN ENTRY ────────────────────────────────────────────────────
    async def validate(self, symbol: str, signal_action: str,
                       confidence: float, features: dict) -> tuple[str, str]:
        """
        Returns (decision, reason).
        Falls through providers in order until one works.
        """
        prompt = self._build_prompt(symbol, signal_action, confidence, features)

        if settings.use_gemini and settings.gemini_api_key:
            decision, reason = await self._gemini(prompt, signal_action)
            if decision != signal_action or reason != "Gemini unavailable":
                logger.debug(f"[Gemini] {symbol} → {decision} | {reason}")
                return decision, reason

        if settings.use_local_llm:
            decision, reason = await self._ollama(prompt, signal_action)
            if reason != "Ollama unavailable":
                logger.debug(f"[Ollama] {symbol} → {decision} | {reason}")
                return decision, reason

        if settings.anthropic_api_key:
            return await self._claude(prompt, signal_action)

        # No LLM available — pass signal through unchanged
        logger.debug(f"[LLM] No provider available — using signal as-is")
        return signal_action, "no LLM"