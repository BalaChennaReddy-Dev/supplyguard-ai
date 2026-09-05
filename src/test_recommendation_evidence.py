import json
from pathlib import Path

from engine.impact import ImpactEngine
from engine.matching import EntityMatcher
from engine.recommendations import ResponseRecommendationEngine


BASE_DIR = Path(__file__).resolve().parent.parent

FIXTURE_PATH = (
    BASE_DIR
    / "data"
    / "extractions"
    / "supplier_shutdown.json"
)


def main():
    print("=" * 80)
    print("SUPPLYGUARD AI - RECOMMENDATION EVIDENCE TEST")
    print("=" * 80)

    extraction = json.loads(
        FIXTURE_PATH.read_text(
            encoding="utf-8"
        )
    )

    matcher = EntityMatcher()

    resolution = matcher.resolve(
        extraction
    )

    impact_engine = ImpactEngine()

    impact_result = impact_engine.analyze_disruption(
        extraction,
        resolution,
    )

    # Reuse the deterministic priority output
    # from the existing pipeline.
    from engine.priority import OrderPriorityEngine

    priority_engine = OrderPriorityEngine()

    prioritized_orders = priority_engine.prioritize(
        impact_result.get("at_risk_orders", []),
        analysis_date="2026-09-05",
    )

    recommendation_engine = ResponseRecommendationEngine()

    recommendations = recommendation_engine.recommend(
        prioritized_orders,
        impact_result,
    )

    print()
    print("RECOMMENDATIONS")
    print("-" * 80)

    for result in recommendations:
        print(
            f"{result['order_id']} | "
            f"{result['recommended_action']}"
        )

        print("Evidence:")

        for evidence in result.get(
            "evidence",
            []
        ):
            print(
                f"  {evidence['source']} | "
                f"{evidence['record_id']} | "
                f"{evidence['fact']}"
            )

    assert len(recommendations) > 0

    recommendation = recommendations[0]

    assert recommendation["order_id"] == "ORD013"

    assert (
        recommendation["recommended_action"]
        == "REALLOCATE"
    )

    assert (
        recommendation["requires_human_approval"]
        is True
    )

    evidence = recommendation.get(
        "evidence",
        []
    )

    assert len(evidence) >= 3

    sources = {
        item["source"]
        for item in evidence
    }

    assert "orders.csv" in sources
    assert "inventory.csv" in sources
    assert "customers.csv" in sources

    record_ids = {
        item["record_id"]
        for item in evidence
    }

    assert "ORD013" in record_ids
    assert "CUST002" in record_ids
    assert "WH001:PROD001" in record_ids

    for item in evidence:
        assert item["source"]
        assert item["record_id"]
        assert item["fact"]

    print()
    print("=" * 80)
    print("RECOMMENDATION EVIDENCE TEST PASSED")
    print("=" * 80)


if __name__ == "__main__":
    main()