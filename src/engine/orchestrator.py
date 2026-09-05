from datetime import date
from typing import Any

from ai.extractor import DisruptionExtractor
from engine.analysis_pipeline import DisruptionAnalysisPipeline
from engine.impact import ImpactEngine
from engine.matching import EntityMatcher
from engine.recommendations import ResponseRecommendationEngine


class SupplyGuardOrchestrator:
    """
    Coordinates the complete disruption-analysis workflow.

    The orchestrator delegates:
    - AI interpretation to the Gemini extractor
    - entity resolution to EntityMatcher
    - deterministic impact calculation to ImpactEngine
    - prioritization, evidence, and graph construction to DisruptionAnalysisPipeline
    - response recommendation generation to ResponseRecommendationEngine
    """

    def __init__(self):
        self.extractor = DisruptionExtractor()
        self.matcher = EntityMatcher()
        self.impact_engine = ImpactEngine()
        self.analysis_pipeline = DisruptionAnalysisPipeline()
        self.recommendation_engine = ResponseRecommendationEngine()

    def analyze_notice(
        self,
        notice: str,
        analysis_date: str | None = None,
    ) -> dict[str, Any]:

        if not notice or not notice.strip():
            raise ValueError("Disruption notice cannot be empty.")

        if analysis_date is None:
            analysis_date = date.today().isoformat()

        # 1. Interpret the unstructured disruption notice with Gemini.
        extraction = self.extractor.extract(notice)

        # 2. Resolve extracted entities against local operational data.
        resolved = self.matcher.resolve(extraction)

        # 3. Calculate deterministic operational impact.
        impact_result = self.impact_engine.analyze_disruption(
            extraction=extraction,
            resolved=resolved,
        )

        # 4. Prioritize affected orders and attach evidence + impact graph.
        analysis_result = self.analysis_pipeline.prioritize_impact(
            impact_result=impact_result,
            analysis_date=analysis_date,
        )

        # 5. Generate deterministic response recommendations.
        recommendations = self.recommendation_engine.recommend(
            prioritized_orders=analysis_result.get(
                "prioritized_orders",
                []
            ),
            impact_result=analysis_result,
        )

        return {
            "notice": notice,
            "analysis_date": analysis_date,
            "extraction": extraction,
            "resolved": resolved,
            "impact": analysis_result,
            "recommendations": recommendations,
        }