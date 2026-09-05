from pydantic import BaseModel, Field


class AnalyzeRequest(BaseModel):
    notice: str = Field(
        ...,
        min_length=1,
        description="Unstructured supply-chain disruption notice.",
    )
    analysis_date: str | None = Field(
        default=None,
        description="Optional analysis date in YYYY-MM-DD format.",
    )