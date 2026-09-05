from typing import Any

from engine.evidence import EvidenceEngine
from engine.impact_graph import ImpactGraphBuilder
from engine.priority import OrderPriorityEngine


class DisruptionAnalysisPipeline:

    def __init__(self):
        self.priority_engine = OrderPriorityEngine()
        self.graph_builder = ImpactGraphBuilder()
        self.evidence_engine = EvidenceEngine()

    def prioritize_impact(
        self,
        impact_result: dict[str, Any],
        analysis_date: str,
    ) -> dict[str, Any]:

        at_risk_orders = impact_result.get(
            "at_risk_orders",
            []
        )

        if at_risk_orders:
            prioritized_orders = self.priority_engine.prioritize(
                at_risk_orders,
                analysis_date=analysis_date,
            )
        else:
            prioritized_orders = []

        # ---------------------------------------------------------
        # Attach traceable evidence to every prioritized order
        # ---------------------------------------------------------

        for order in prioritized_orders:
            order["evidence"] = (
                self.evidence_engine.order_evidence(
                    order
                )
            )

        # ---------------------------------------------------------
        # Build impact graph after prioritization
        # ---------------------------------------------------------

        impact_graph = self.graph_builder.build(
            impact_result=impact_result,
            prioritized_orders=prioritized_orders,
        )

        return {
            **impact_result,
            "prioritized_orders": prioritized_orders,
            "impact_graph": impact_graph,
        }