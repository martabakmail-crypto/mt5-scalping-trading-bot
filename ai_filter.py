import json
import logging
import requests
from typing import Tuple, Dict, Any
from config import BotConfig

logger = logging.getLogger("ScalpingBot.AIFilter")

class AIMarketFilter:
    """Evaluates market context and trade signals using Google Gemini AI."""

    def __init__(self, config: BotConfig):
        self.config = config
        self.api_key = config.GEMINI_API_KEY
        self.enabled = config.USE_AI_FILTER and bool(self.api_key)
        self.model = config.AI_MODEL_NAME or "gemini-2.5-flash"

    def verify_trade(
        self,
        symbol: str,
        signal: str,
        confidence_score: float,
        details: Dict[str, Any]
    ) -> Tuple[bool, str]:
        """
        Consults Google Gemini AI to approve or reject a technical trade signal.
        Returns: (approved: bool, reasoning: str)
        """
        if not self.enabled:
            logger.info("AI Market Filter disabled or API key missing. Passing trade by default.")
            return True, "AI Filter Disabled (Technical Signal Approved)"

        endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"

        prompt = (
            f"You are an expert algorithmic quantitative trader and market risk manager.\n"
            f"Review the following technical trading signal for instrument {symbol}:\n\n"
            f"- Signal Proposed: {signal}\n"
            f"- Technical Confidence Score: {confidence_score:.1f}%\n"
            f"- Trend Analysis: {details.get('trend', 'N/A')}\n"
            f"- RSI Status: {details.get('rsi', 'N/A')}\n"
            f"- Price Action: {details.get('price_action', 'N/A')}\n"
            f"- Volatility (ATR): {details.get('volatility', 'N/A')}\n"
            f"- Current Price: {details.get('current_price', 'N/A')}\n\n"
            f"Your Task:\n"
            f"Determine if this setup is safe to execute for a short-term M5 scalp trade.\n"
            f"Provide your verdict in STRICT JSON format with EXACTLY two keys:\n"
            f"{{\n"
            f'  "approved": true/false,\n'
            f'  "reasoning": "Brief explanation in 1-2 sentences in Indonesian"\n'
            f"}}\n"
            f"Return ONLY valid JSON. No markdown codeblocks, no commentary."
        )

        payload = {
            "contents": [
                {
                    "parts": [{"text": prompt}]
                }
            ],
            "generationConfig": {
                "temperature": 0.2,
                "maxOutputTokens": 200
            }
        }

        try:
            res = requests.post(endpoint, json=payload, timeout=12)
            if res.status_code == 200:
                data = res.json()
                text_resp = data['candidates'][0]['content']['parts'][0]['text'].strip()

                # Clean markdown code blocks if present
                if text_resp.startswith("```"):
                    text_resp = text_resp.strip("`").replace("json\n", "").strip()

                parsed = json.loads(text_resp)
                approved = bool(parsed.get("approved", True))
                reasoning = str(parsed.get("reasoning", "AI Approved setup."))

                logger.info(f"AI Decision: Approved={approved} | Reasoning: {reasoning}")
                return approved, reasoning
            else:
                logger.error(f"Gemini API Error ({res.status_code}): {res.text}")
                # Fallback to technical signal if API errors out
                return True, f"AI API Error ({res.status_code}) - Technical Fallback"
        except Exception as e:
            logger.error(f"AI Verification failed with exception: {e}")
            return True, "AI Exception - Technical Fallback"
