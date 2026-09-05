
import json
from pathlib import Path

from engine.matching import EntityMatcher
from engine.impact import ImpactEngine
from engine.analysis_pipeline import DisruptionAnalysisPipeline


BASE_DIR = Path(__file__).resolve().parent.parent
FIXTURE_DIR = BASE_DIR / "data" / "extractions"


def load_fixture(filename: str) -> dict:
    """Load a saved Gemini extraction fixture."""

    fixture_path = FIXTURE_DIR / filename

    with open(
        fixture_path,
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def main():
    print("=" * 80)
    print("SUPPLYGUARD AI - IMPACT + PRIORITY PIPELINE")
    print("=" * 80)

    # --------------------------------------------------------------
    # Load saved extraction
    #
    # Gemini is NOT called during this test.
    # --------------------------------------------------------------

    extraction = load_fixture(
        "supplier_shutdown.json"
    )

    # --------------------------------------------------------------
    # Entity matching
    # --------------------------------------------------------------

    matcher = EntityMatcher()

    resolution = matcher.resolve(
        extraction
    )

    # --------------------------------------------------------------
    # Deterministic impact analysis
    # --------------------------------------------------------------

    impact_engine = ImpactEngine()

    impact_result = impact_engine.analyze_disruption(
        extraction,
        resolution,
    )

    print()
    print("IMPACT")
    print("-" * 80)

    print(
        f"Status: "
        f"{impact_result['impact_status']}"
    )

    print(
        f"Impact found: "
        f"{impact_result['impact_found']}"
    )

    # --------------------------------------------------------------
    # Priority pipeline
    # --------------------------------------------------------------

    pipeline = DisruptionAnalysisPipeline()

    analysis_result = pipeline.prioritize_impact(
        impact_result,
        analysis_date="2026-09-05",
    )

    prioritized_orders = analysis_result.get(
        "prioritized_orders",
        [],
    )

    print()
    print("PRIORITIZED AT-RISK ORDERS")
    print("-" * 80)

    for index, order in enumerate(
        prioritized_orders,
        start=1,
    ):
        print(
            f"{index}. "
            f"{order['order_id']} | "
            f"{order['customer_name']} | "
            f"{order['priority']} | "
            f"score={order['priority_score']} | "
            f"shortage={order['shortage_quantity']} | "
            f"required={order['required_date']}"
        )

        print("   Reasons:")

        for reason in order["reasons"]:
            print(
                f"   • {reason}"
            )

    # --------------------------------------------------------------
    # Assertions
    # --------------------------------------------------------------

    assert impact_result["impact_found"] is True

    assert (
        impact_result["impact_status"]
        == "confirmed_impact"
    )

    assert len(prioritized_orders) > 0

    # --------------------------------------------------------------
    # Verify required Phase 7 fields are preserved
    # --------------------------------------------------------------

    for order in prioritized_orders:
        assert "order_id" in order
        assert "customer_id" in order
        assert "customer_name" in order

        assert "product_id" in order
        assert "warehouse_id" in order

        assert "quantity" in order
        assert "fulfillable_quantity" in order
        assert "shortage_quantity" in order

        assert "required_date" in order
        assert "order_date" in order

        assert "priority_score" in order
        assert "priority" in order

        assert "score_breakdown" in order
        assert "reasons" in order

    # --------------------------------------------------------------
    # Verify deterministic ranking
    # --------------------------------------------------------------

    scores = [
        order["priority_score"]
        for order in prioritized_orders
    ]

    assert scores == sorted(
        scores,
        reverse=True,
    )

    # --------------------------------------------------------------
    # Expected supplier-shutdown result
    # --------------------------------------------------------------

    assert (
        prioritized_orders[0]["order_id"]
        == "ORD013"
    )

    assert (
        prioritized_orders[0]["priority_score"]
        == 79.0
    )

    assert (
        prioritized_orders[0]["shortage_quantity"]
        == 40.0
    )

    print()
    print("=" * 80)
    print("✅ IMPACT + PRIORITY PIPELINE PASSED")
    print("=" * 80)


if __name__ == "__main__":
    main()

