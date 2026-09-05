from typing import Any

from engine.priority import OrderPriorityEngine


class DisruptionAnalysisPipeline:

    def __init__(self):
        self.priority_engine = OrderPriorityEngine()

    def prioritize_impact(
        self,
        impact_result: dict[str, Any],
        analysis_date: str,
    ) -> dict[str, Any]:

        at_risk_orders = impact_result.get(
            "at_risk_orders",
            []
        )

        if not at_risk_orders:
            return {
                **impact_result,
                "prioritized_orders": [],
            }

        prioritized_orders = self.priority_engine.prioritize(
            at_risk_orders,
            analysis_date=analysis_date,
        )

        return {
            **impact_result,
            "prioritized_orders": prioritized_orders,
        }