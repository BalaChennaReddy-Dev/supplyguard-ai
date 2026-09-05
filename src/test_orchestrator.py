import json
from pathlib import Path

from engine.orchestrator import SupplyGuardOrchestrator


BASE_DIR = Path(__file__).resolve().parent.parent
NOTICE_PATH = BASE_DIR / "data" / "disruptions" / "supplier_shutdown.txt"


def main():
    print("=" * 80)
    print("SUPPLYGUARD AI - END-TO-END ORCHESTRATOR TEST")
    print("=" * 80)

    notice = NOTICE_PATH.read_text(encoding="utf-8")

    orchestrator = SupplyGuardOrchestrator()

    result = orchestrator.analyze_notice(
        notice=notice,
        analysis_date="2026-09-05",
    )

    print("\nEXTRACTION")
    print("-" * 80)
    extraction = result["extraction"]
    print(f"Event: {extraction.get('event_type')}")
    print(f"Supplier: {extraction.get('supplier_name')}")
    print(f"Location: {extraction.get('location')}")
    print(f"Duration: {extraction.get('duration_days')} days")

    print("\nIMPACT")
    print("-" * 80)
    impact = result["impact"]
    print(f"Status: {impact.get('impact_status')}")
    print(f"Impact found: {impact.get('impact_found')}")
    print(f"Affected shipments: {len(impact.get('affected_shipments', []))}")
    print(f"At-risk orders: {len(impact.get('at_risk_orders', []))}")

    print("\nPRIORITIZED ORDERS")
    print("-" * 80)

    prioritized_orders = impact.get("prioritized_orders", [])

    for order in prioritized_orders:
        print(
            f"{order['order_id']} | "
            f"{order['customer_name']} | "
            f"{order['priority']} | "
            f"score={order['priority_score']} | "
            f"shortage={order['shortage_quantity']}"
        )

    print("\nRECOMMENDATIONS")
    print("-" * 80)

    recommendations = result.get("recommendations", [])

    for recommendation in recommendations:
        print(
            f"{recommendation['order_id']} | "
            f"{recommendation.get('recommended_action')} | "
            f"human approval="
            f"{recommendation.get('requires_human_approval')}"
        )

    print("\nIMPACT GRAPH")
    print("-" * 80)

    graph = impact.get("impact_graph", {})

    print(f"Nodes: {len(graph.get('nodes', []))}")
    print(f"Edges: {len(graph.get('edges', []))}")

    print("\nVERIFIED OUTPUT")
    print("-" * 80)

    assert result["extraction"]["event_type"] == "production_shutdown"
    assert result["extraction"]["supplier_name"] == "Alpha Components Ltd"

    assert impact["impact_found"] is True
    assert impact["impact_status"] == "confirmed_impact"

    assert len(prioritized_orders) >= 1
    assert prioritized_orders[0]["order_id"] == "ORD013"

    assert len(recommendations) >= 1
    assert recommendations[0]["order_id"] == "ORD013"
    assert recommendations[0]["recommended_action"] == "REALLOCATE"
    assert recommendations[0]["requires_human_approval"] is True

    assert len(graph["nodes"]) >= 1
    assert len(graph["edges"]) >= 1

    output_path = (
        BASE_DIR
        / "data"
        / "orchestrator_supplier_shutdown.json"
    )

    output_path.write_text(
        json.dumps(result, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print("End-to-end workflow completed successfully.")
    print(f"Fixture saved to: {output_path}")

    print("\n" + "=" * 80)
    print("END-TO-END ORCHESTRATOR TEST PASSED")
    print("=" * 80)


if __name__ == "__main__":
    main()