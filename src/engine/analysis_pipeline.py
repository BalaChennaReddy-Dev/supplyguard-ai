
from typing import Any

from engine.impact_graph import ImpactGraphBuilder
from engine.priority import OrderPriorityEngine


class DisruptionAnalysisPipeline:
    """
    Coordinates deterministic disruption analysis stages.

    Pipeline:
        Impact Analysis
            ↓
        Order Prioritization
            ↓
        Impact Graph
    """

    def __init__(self):
        self.priority_engine = OrderPriorityEngine()
        self.graph_builder = ImpactGraphBuilder()

    def prioritize_impact(
        self,
        impact_result: dict[str, Any],
        analysis_date: str,
    ) -> dict[str, Any]:
        """
        Prioritize affected orders and build the impact graph.

        The priority engine performs deterministic calculations.
        The graph builder creates traceable relationships from
        the resulting operational data.
        """

        at_risk_orders = impact_result.get(
            "at_risk_orders",
            []
        )

        # ---------------------------------------------------------
        # Step 1: Prioritize affected orders
        # ---------------------------------------------------------

        if at_risk_orders:

            prioritized_orders = self.priority_engine.prioritize(
                at_risk_orders,
                analysis_date=analysis_date,
            )

        else:

            prioritized_orders = []

        # ---------------------------------------------------------
        # Step 2: Build impact graph
        # ---------------------------------------------------------

        impact_graph = self.graph_builder.build(
            impact_result=impact_result,
            prioritized_orders=prioritized_orders,
        )

        # ---------------------------------------------------------
        # Step 3: Return complete analysis result
        # ---------------------------------------------------------

        return {
            **impact_result,
            "prioritized_orders": prioritized_orders,
            "impact_graph": impact_graph,
        }

