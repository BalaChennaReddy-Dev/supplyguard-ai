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
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Disruption analysis failed.",
        ) from exc