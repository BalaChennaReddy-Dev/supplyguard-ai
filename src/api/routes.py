from fastapi import APIRouter, HTTPException

from api.schemas import AnalyzeRequest
from engine.orchestrator import SupplyGuardOrchestrator


router = APIRouter(prefix="/api", tags=["analysis"])

orchestrator = SupplyGuardOrchestrator()


@router.post("/analyze")
def analyze_disruption(request: AnalyzeRequest):
    try:
        return orchestrator.analyze_notice(
            notice=request.notice,
            analysis_date=request.analysis_date,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc
    except RuntimeError as exc:
        if "quota has been exhausted" in str(exc).lower():
            raise HTTPException(
                status_code=503,
                detail=(
                    "Gemini API quota is temporarily unavailable. "
                    "Please try again after the quota resets."
                ),
            ) from exc
        raise HTTPException(
            status_code=500,
            detail="Disruption analysis failed.",
        ) from exc
