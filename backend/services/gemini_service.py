"""Google Gemini API service — replacement for Ollama."""

import json
import re
import logging
import google.generativeai as genai
from config import settings

logger = logging.getLogger(__name__)


class GeminiService:
    """Wrapper around Google Gemini API for LLM operations."""

    def __init__(self):
        key = settings.GEMINI_API_KEY
        # Clean the key (remove quotes or whitespace that might be accidentally included)
        if key:
            key = key.strip().strip("'").strip('"')
            
        if not key or key == "your_gemini_api_key_here" or len(key) < 10:
            logger.error("Gemini API key is invalid or not set correctly.")
            raise ValueError("GEMINI_API_KEY is missing, invalid, or still using the placeholder. "
                            "Please ensure a valid key from https://aistudio.google.com/ is set in your environment.")
        
        genai.configure(api_key=key)
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

    def _extract_json(self, raw: str) -> dict:
        """Robustly extract JSON from a Gemini response that may contain
        markdown fences, preamble text, or trailing characters."""
        text = raw.strip()

        # Strip markdown code fences (```json ... ``` or ``` ... ```)
        fence_pattern = r"```(?:json)?\s*\n?(.*?)```"
        fence_match = re.search(fence_pattern, text, re.DOTALL)
        if fence_match:
            text = fence_match.group(1).strip()

        # Try direct parse first
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # Try to find the outermost { ... } or [ ... ]
        for start_char, end_char in [('{', '}'), ('[', ']')]:
            start_idx = text.find(start_char)
            if start_idx == -1:
                continue
            # Find matching closing bracket by counting nesting
            depth = 0
            end_idx = -1
            in_string = False
            escape = False
            for i in range(start_idx, len(text)):
                c = text[i]
                if escape:
                    escape = False
                    continue
                if c == '\\' and in_string:
                    escape = True
                    continue
                if c == '"' and not escape:
                    in_string = not in_string
                    continue
                if in_string:
                    continue
                if c == start_char:
                    depth += 1
                elif c == end_char:
                    depth -= 1
                    if depth == 0:
                        end_idx = i
                        break
            if end_idx != -1:
                try:
                    return json.loads(text[start_idx:end_idx + 1])
                except json.JSONDecodeError:
                    pass

        raise json.JSONDecodeError("Could not extract valid JSON from response", text, 0)

    async def generate_json(self, system_prompt: str, user_prompt: str,
                            max_retries: int = 2) -> dict:
        """Generate and auto-parse JSON response from Gemini with retry logic."""
        last_error = None

        for attempt in range(1, max_retries + 2):  # max_retries + 1 total attempts
            try:
                full_prompt = (
                    f"{system_prompt}\n\n{user_prompt}\n\n"
                    "IMPORTANT: Return ONLY valid JSON. No markdown fences, no extra text."
                )

                # Use JSON mime type on first attempt; fall back to text on retries
                config = genai.GenerationConfig(
                    max_output_tokens=4096,
                    temperature=0.2,
                )
                if attempt == 1:
                    config = genai.GenerationConfig(
                        max_output_tokens=4096,
                        temperature=0.2,
                        response_mime_type="application/json",
                    )

                response = self.model.generate_content(full_prompt, generation_config=config)
                raw = response.text.strip()
                result = self._extract_json(raw)

                # Basic sanity check — must be a dict with at least one key
                if isinstance(result, dict) and len(result) > 0:
                    logger.info(f"Gemini JSON parsed successfully on attempt {attempt}")
                    return result
                elif isinstance(result, list):
                    logger.info(f"Gemini returned JSON array on attempt {attempt}")
                    return result
                else:
                    raise ValueError("Empty or invalid JSON structure returned")

            except (json.JSONDecodeError, ValueError) as e:
                last_error = e
                logger.warning(
                    f"JSON parse attempt {attempt}/{max_retries + 1} failed: {e}"
                )
                if attempt <= max_retries:
                    logger.info(f"Retrying Gemini JSON generation (attempt {attempt + 1})...")
                continue
            except Exception as e:
                logger.error(f"Gemini JSON generation error: {e}")
                raise

        logger.error(f"All {max_retries + 1} attempts at JSON generation failed")
        raise last_error


# Singleton instance
llm = GeminiService()
