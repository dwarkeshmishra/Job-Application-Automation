"""Google Gemini API service — replacement for Ollama."""

import json
import logging
import google.generativeai as genai
from config import settings

logger = logging.getLogger(__name__)


class GeminiService:
    """Wrapper around Google Gemini API for LLM operations."""

    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(settings.GEMINI_MODEL)
        logger.info(f"Gemini service initialized with model: {settings.GEMINI_MODEL}")

    async def generate(self, system_prompt: str, user_prompt: str,
                       max_tokens: int = 4096) -> str:
        """Single generation call to Gemini."""
        try:
            full_prompt = f"{system_prompt}\n\n{user_prompt}"
            response = self.model.generate_content(
                full_prompt,
                generation_config=genai.GenerationConfig(
                    max_output_tokens=max_tokens,
                    temperature=0.3,
                ),
            )
            return response.text
        except Exception as e:
            logger.error(f"Gemini generation error: {e}")
            raise

    async def generate_json(self, system_prompt: str, user_prompt: str) -> dict:
        """Generate and auto-parse JSON response from Gemini."""
        try:
            full_prompt = (
                f"{system_prompt}\n\n{user_prompt}\n\n"
                "IMPORTANT: Return ONLY valid JSON. No markdown fences, no extra text."
            )
            response = self.model.generate_content(
                full_prompt,
                generation_config=genai.GenerationConfig(
                    max_output_tokens=4096,
                    temperature=0.2,
                    response_mime_type="application/json",
                ),
            )
            raw = response.text.strip()
            # Strip markdown code fences if present
            if raw.startswith("```"):
                raw = raw.split("\n", 1)[1] if "\n" in raw else raw[3:]
                if raw.endswith("```"):
                    raw = raw[:-3]
                raw = raw.strip()
            return json.loads(raw)
        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error from Gemini: {e}\nRaw: {raw[:500]}")
            raise
        except Exception as e:
            logger.error(f"Gemini JSON generation error: {e}")
            raise


# Singleton instance
llm = GeminiService()
