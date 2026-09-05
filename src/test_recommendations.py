import json
from pathlib import Path

from engine.matching import EntityMatcher
from engine.impact import ImpactEngine
from engine.analysis_pipeline import DisruptionAnalysisPipeline
from engine.recommendations import ResponseRecommendationEngine


BASE_DIR = Path(__file__).resolve().parent.parent
FIXTURE_DIR = BASE_DIR / "data" / "extractions"


def load_fixture(name):
    with open(FIXTURE_DIR / name, "r", encoding="utf-8") as file:
        return json.load(file)


def main():
    print("=" * 80)
    print("SUPPLYGUARD AI - RESPONSE RECOMMENDATION TEST")
    print("=" * 80)

    extraction = load_fixture("supplier_shutdown.json")

    matcher = EntityMatcher()
    resolution = matcher.resolve(extraction)

    impact_engine = ImpactEngine()

    impact_result = impact_engine.analyze_disruption(
        extraction,
        resolution,
    )

    pipeline = DisruptionAnalysisPipeline()

    analysis_result = pipeline.prioritize_impact(
        impact_result,
        analysis_date="2026-09-05",
    )

    prioritized_orders = analysis_result["prioritized_orders"]

    recommendation_engine = ResponseRecommendationEngine()

    recommendations = recommendation_engine.recommend(
        prioritized_orders,
        impact_result,
    )

    print()
    print("DISRUPTION")
    print("-" * 80)
    print(f"Event: {extraction['event_type']}")
    print(f"Supplier: {extraction['supplier_name']}")

    print()
    print("AFFECTED ORDERS")
    print("-" * 80)

    for recommendation in recommendations:
        print()
        print(
            f"{recommendation['order_id']} | "
            f"{recommendation['customer_name']}"
        )

        print(
            f"Shortage: "
            f"{recommendation['shortage_quantity']:g} units"
        )

        print(
            f"Recommended action: "
            f"{recommendation['recommended_action']}"
        )

        print(
            f"Human approval required: "
            f"{recommendation['requires_human_approval']}"
        )

        print()
        print("OPTIONS:")

        for option in recommendation["options"]:
            status = "FEASIBLE" if option["feasible"] else "NOT FEASIBLE"

            print(
                f"  • {option['action']}: {status}"
            )

            print(
                f"    Reason: {option['reason']}"
            )

            if option.get("trade_off"):
                print(
                    f"    Trade-off: {option['trade_off']}"
                )

    # --------------------------------------------------------------
    # Assertions
    # --------------------------------------------------------------

    assert impact_result["impact_found"] is True
    assert len(prioritized_orders) > 0
    assert len(recommendations) > 0

    for recommendation in recommendations:
        assert recommendation["recommended_action"] is not None
        assert recommendation["requires_human_approval"] is True

        assert len(recommendation["options"]) == 4

        for option in recommendation["options"]:
            assert "action" in option
            assert "feasible" in option
            assert "reason" in option

    print()
    print("=" * 80)
    print("✅ RESPONSE RECOMMENDATION TEST PASSED")
    print("=" * 80)


if __name__ == "__main__":
    main()