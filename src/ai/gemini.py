import json
import os
import time

from dotenv import load_dotenv
from google import genai


load_dotenv()


class GeminiClient:

    def __init__(self):

        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise RuntimeError(
                "GEMINI_API_KEY is not configured."
            )

        self.client = genai.Client(
            api_key=api_key
        )

        self.model = "gemini-3.6-flash"

    def generate_json(self, prompt: str, max_retries: int = 3) -> dict:
        last_error = None

        for attempt in range(max_retries):
            try:
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=prompt,
                    config={
                        "response_mime_type": "application/json",
                    },
                )

                # Gemini may return already-parsed JSON.
                parsed = getattr(response, "parsed", None)

                if isinstance(parsed, dict):
                    return parsed

                # Otherwise read the text response.
                text = getattr(response, "text", None)

                if isinstance(text, dict):
                    return text

                if text:
                    return json.loads(text)

                raise RuntimeError("Gemini returned an empty response.")

            except Exception as exc:
                last_error = exc
                error_text = str(exc)

                # Daily/free-tier quota exhaustion is NOT a temporary error.
                if (
                    "RESOURCE_EXHAUSTED" in error_text
                    and "generate_content_free_tier_requests" in error_text
                ):
                    raise RuntimeError(
                        "Gemini API quota has been exhausted. "
                        "Please wait for the quota to reset or use an available "
                        "Gemini API plan."
                    ) from exc

                # Retry temporary service/rate-limit errors.
                if (
                    "503" in error_text
                    or "UNAVAILABLE" in error_text
                    or "429" in error_text
                ):
                    if attempt < max_retries - 1:
                        wait_seconds = 2 ** attempt

                        print(
                            f"\n⚠️ Gemini temporarily unavailable. "
                            f"Retrying in {wait_seconds}s..."
                        )

                        time.sleep(wait_seconds)
                        continue

                raise RuntimeError(
                    f"Gemini request failed: {exc}"
                ) from exc

        raise RuntimeError(
            f"Gemini request failed after {max_retries} attempts: {last_error}"
        )