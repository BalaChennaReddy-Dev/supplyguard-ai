import json
from typing import Any

from .gemini import GeminiClient
from .prompts import SYSTEM_PROMPT, EXTRACTION_PROMPT


class DisruptionExtractor:
    def __init__(self):
        self.gemini = GeminiClient()

    def extract(self, notice: str) -> dict[str, Any]:
        if not notice or not notice.strip():
            raise ValueError("Disruption notice cannot be empty.")

        prompt = (
            SYSTEM_PROMPT
            + "\n\n"
            + EXTRACTION_PROMPT.format(notice=notice)
        )

        raw_response = self.gemini.generate_json(prompt)

        try:
            result = json.loads(raw_response)
        except json.JSONDecodeError as exc:
            raise RuntimeError(
                "Gemini returned invalid JSON."
            ) from exc

        return self._validate(result)

    def _validate(self, result: dict[str, Any]) -> dict[str, Any]:
        required_fields = {
            "event_type",
            "supplier_name",
            "location",
            "shipment_id",
            "warehouse_name",
            "start_date",
            "duration_days",
            "affected_products",
            "description",
            "confidence",
            "missing_information",
        }

        missing = required_fields - result.keys()

        if missing:
            raise RuntimeError(
                f"Gemini response is missing fields: {sorted(missing)}"
            )

        if not isinstance(result["affected_products"], list):
            raise RuntimeError(
                "affected_products must be a list."
            )

        if not isinstance(result["missing_information"], list):
            raise RuntimeError(
                "missing_information must be a list."
            )

        confidence = result["confidence"]

        if not isinstance(confidence, (int, float)):
            raise RuntimeError(
                "confidence must be numeric."
            )

        if not 0 <= confidence <= 1:
            raise RuntimeError(
                "confidence must be between 0 and 1."
            )

        return result