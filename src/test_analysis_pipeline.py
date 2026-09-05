import json
from pathlib import Path

from engine.impact import ImpactEngine
from engine.matching import EntityMatcher
from engine.analysis_pipeline import DisruptionAnalysisPipeline


BASE_DIR = Path(__file__).resolve().parent.parent
EXTRACTIONS_DIR = BASE_DIR / "data" / "extractions"


def load_extraction(filename):
    path = EXTRACTIONS_DIR / filename

    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def main():
    extraction = load_extraction(
        "supplier_shutdown.json"
    )

    matcher = EntityMatcher()
    resolution = matcher.resolve(extraction)

    impact_engine = ImpactEngine()

    impact_result = impact_engine.analyze_disruption(
        extraction,
        resolution,
    )

    pipeline = DisruptionAnalysisPipeline()

    final_result = pipeline.prioritize_impact(
        impact_result,
        analysis_date="2026-09-05",
    )

    print("\n" + "=" * 80)
    print("SUPPLYGUARD AI - IMPACT + PRIORITY PIPELINE")
    print("=" * 80)

    print("\nIMPACT")
    print("-" * 80)

    print(
        "Status:",
        final_result["impact_status"]
    )

    print(
        "Impact found:",
        final_result["impact_found"]
    )

    print("\nPRIORITIZED AT-RISK ORDERS")
    print("-" * 80)

    orders = final_result.get(
        "prioritized_orders",
        []
    )

    for index, order in enumerate(orders, start=1):

        print(
            f"{index}. "
            f"{order['order_id']} | "
            f"{order['customer_name']} | "
            f"{order['priority']} | "
            f"score={order['priority_score']} | "
            f"shortage={order['shortage']} | "
            f"required={order['required_date']}"
        )

        print("   Reasons:")

        for reason in order["reasons"]:
            print(f"   • {reason}")

    assert final_result["impact_found"] is True
    assert len(orders) > 0
    assert orders[0]["shortage"] > 0

    scores = [
        order["priority_score"]
        for order in orders
    ]

    assert scores == sorted(
        scores,
        reverse=True
    )

    print("\n" + "=" * 80)
    print("✅ IMPACT + PRIORITY PIPELINE PASSED")
    print("=" * 80)


if __name__ == "__main__":
    main()