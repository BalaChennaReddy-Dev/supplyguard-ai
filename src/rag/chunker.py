from pathlib import Path
from typing import Any


BASE_DIR = Path(__file__).resolve().parent.parent.parent
DOCUMENTS_DIR = BASE_DIR / "documents"


class PlaybookChunker:
    """Split the response playbook into rule-level chunks."""

    def __init__(self, document_path: Path | None = None):
        self.document_path = document_path or (
            DOCUMENTS_DIR / "response_playbook.md"
        )

    def load_document(self) -> str:
        if not self.document_path.exists():
            raise FileNotFoundError(
                f"Playbook not found: {self.document_path}"
            )

        return self.document_path.read_text(encoding="utf-8")

    def chunk(self) -> list[dict[str, Any]]:
        text = self.load_document()
        lines = text.splitlines()

        chunks = []
        current_rule = None
        current_lines = []

        for line in lines:
            cleaned = line.strip().replace("**", "")

            # Detect headings such as:
            # ## R01 — Full Reallocation Preferred
            if cleaned.startswith("## R") and "—" in cleaned:
                if current_rule is not None:
                    chunks.append(
                        self._create_chunk(
                            current_rule,
                            current_lines
                        )
                    )

                rule_text = cleaned[3:].strip()
                rule_id, rule_title = rule_text.split(" — ", 1)

                current_rule = {
                    "rule_id": rule_id.strip(),
                    "title": rule_title.strip()
                }

                current_lines = [cleaned]

            elif current_rule is not None:
                current_lines.append(line)

        # Add the final rule.
        if current_rule is not None:
            chunks.append(
                self._create_chunk(
                    current_rule,
                    current_lines
                )
            )

        return chunks

    @staticmethod
    def _create_chunk(
        rule: dict[str, str],
        lines: list[str]
    ) -> dict[str, Any]:

        content = "\n".join(lines).strip()

        return {
            "chunk_id": rule["rule_id"],
            "rule_id": rule["rule_id"],
            "title": rule["title"],
            "content": content,
            "source": "documents/response_playbook.md"
        }