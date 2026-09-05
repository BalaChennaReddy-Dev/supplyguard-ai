import json
from typing import Any

from ai.gemini import GeminiClient
from ai.prompts import EXTRACTION_PROMPT


class DisruptionExtractor:
    def __init__(self):
        self.client = GeminiClient()

    def extract(self, notice: str) -> dict[str, Any]:
        if not notice or not notice.strip():
            raise ValueError("Disruption notice cannot be empty.")

        raw_response = self.client.generate_json(
            EXTRACTION_PROMPT.format(notice=notice)
        )

        if isinstance(raw_response, dict):
            result = raw_response
        elif isinstance(raw_response, str):
            result = json.loads(raw_response)
        else:
            raise TypeError(
                "Gemini response must be a dict or JSON string, "
                f"got {type(raw_response).__name__}."
            )

        if not isinstance(result, dict):
            raise ValueError("Gemini extraction result must be a JSON object.")

        return result