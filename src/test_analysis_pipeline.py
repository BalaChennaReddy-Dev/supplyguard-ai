
import json
from pathlib import Path

from engine.analysis_pipeline import DisruptionAnalysisPipeline
from engine.impact import ImpactEngine
from engine.matching import EntityMatcher


BASE_DIR = Path(__file__).resolve().parent.parent

FIXTURE_PATH = (
    BASE_DIR
    / "data"
    / "extractions"
    / "supplier_shutdown.json"
)


def main():
    print("=" * 80)
    print("SUPPLYGUARD AI - PIPELINE + IMPACT GRAPH TEST")
    print("=" * 80)

    # ---------------------------------------------------------
    # Load extraction fixture
    # ---------------------------------------------------------

    extraction = json.loads(
        FIXTURE_PATH.read_text(
            encoding="utf-8"
        )
    )

    # ---------------------------------------------------------
    # Resolve entities
    # ---------------------------------------------------------

    matcher = EntityMatcher()

    resolution = matcher.resolve(
        extraction
    )

    # ---------------------------------------------------------
    # Run deterministic impact analysis
    #
    # IMPORTANT:
    # ImpactEngine uses the resolved entities as a positional
    # argument in the current implementation.
    # ---------------------------------------------------------

    impact_engine = ImpactEngine()

    impact_result = impact_engine.analyze_disruption(
        extraction,
        resolution,
    )

    # ---------------------------------------------------------
    # Run complete analysis pipeline
    # ---------------------------------------------------------

    pipeline = DisruptionAnalysisPipeline()

    result = pipeline.prioritize_impact(
        impact_result=impact_result,
        analysis_date="2026-09-05",
    )

    # ---------------------------------------------------------
    # Display summary
    # ---------------------------------------------------------

    print()
    print(
        f"Impact status: "
        f"{result.get('impact_status')}"
    )

    print(
        f"Impact found: "
        f"{result.get('impact_found')}"
    )

    print(
        f"Prioritized orders: "
        f"{len(result.get('prioritized_orders', []))}"
    )

    graph = result.get(
        "impact_graph",
        {}
    )

    print(
        f"Graph nodes: "
        f"{graph.get('node_count', 0)}"
    )

    print(
        f"Graph edges: "
        f"{graph.get('edge_count', 0)}"
    )

    # ---------------------------------------------------------
    # Display prioritized orders
    # ---------------------------------------------------------

    print()
    print("PRIORITIZED ORDERS")
    print("-" * 80)

    for order in result.get(
        "prioritized_orders",
        []
    ):

        print(
            f"{order['order_id']} | "
            f"{order['customer_name']} | "
            f"{order['priority']} | "
            f"score={order['priority_score']} | "
            f"shortage={order['shortage_quantity']}"
        )

    # ---------------------------------------------------------
    # Display graph trace
    # ---------------------------------------------------------

    print()
    print("IMPACT GRAPH TRACE")
    print("-" * 80)

    for edge in graph.get(
        "edges",
        []
    ):

        print(
            f"{edge['source']} "
            f"--{edge['relationship']}--> "
            f"{edge['target']}"
        )

    # ---------------------------------------------------------
    # Basic assertions
    # ---------------------------------------------------------

    assert result["impact_found"] is True, (
        "Expected impact_found=True"
    )

    assert result["impact_status"] == "confirmed_impact", (
        "Expected confirmed_impact"
    )

    assert len(
        result["prioritized_orders"]
    ) > 0, (
        "Expected at least one prioritized order"
    )

    assert "impact_graph" in result, (
        "Pipeline result does not contain impact_graph"
    )

    assert graph["node_count"] > 0, (
        "Impact graph contains no nodes"
    )

    assert graph["edge_count"] > 0, (
        "Impact graph contains no edges"
    )

    # ---------------------------------------------------------
    # Verify prioritized order ORD013
    # ---------------------------------------------------------

    orders = result[
        "prioritized_orders"
    ]

    ord013 = next(
        (
            order
            for order in orders
            if order["order_id"] == "ORD013"
        ),
        None,
    )

    assert ord013 is not None, (
        "ORD013 was not found in prioritized orders"
    )

    assert ord013["priority"] == "HIGH", (
        f"Expected ORD013 priority HIGH, "
        f"got {ord013['priority']}"
    )

    assert ord013["priority_score"] == 79.0, (
        f"Expected ORD013 score 79.0, "
        f"got {ord013['priority_score']}"
    )

    assert ord013["shortage_quantity"] == 40, (
        f"Expected ORD013 shortage 40, "
        f"got {ord013['shortage_quantity']}"
    )

    # ---------------------------------------------------------
    # Verify graph nodes
    # ---------------------------------------------------------

    node_ids = {
        node["id"]
        for node in graph["nodes"]
    }

    required_nodes = {
        "SUP001",
        "PROD001",
        "SHIP001",
        "WH001",
        "INV:WH001:PROD001",
        "ORD013",
        "CUST002",
    }

    for node_id in required_nodes:

        assert node_id in node_ids, (
            f"Missing graph node: {node_id}"
        )

    # ---------------------------------------------------------
    # Verify warehouse name
    # ---------------------------------------------------------

    warehouse_nodes = {
        node["id"]: node
        for node in graph["nodes"]
        if node["type"] == "warehouse"
    }

    assert "WH001" in warehouse_nodes, (
        "WH001 warehouse node missing"
    )

    assert (
        warehouse_nodes["WH001"]["label"]
        == "Chennai Central Warehouse"
    ), (
        "WH001 does not contain the expected warehouse name"
    )

    # ---------------------------------------------------------
    # Verify graph relationships
    # ---------------------------------------------------------

    edge_tuples = {
        (
            edge["source"],
            edge["target"],
            edge["relationship"],
        )
        for edge in graph["edges"]
    }

    required_edges = {
        (
            "SUP001",
            "PROD001",
            "SUPPLIES",
        ),
        (
            "PROD001",
            "SHIP001",
            "SHIPPED_AS",
        ),
        (
            "SHIP001",
            "WH001",
            "DELIVERS_TO",
        ),
        (
            "WH001",
            "INV:WH001:PROD001",
            "STORES",
        ),
        (
            "INV:WH001:PROD001",
            "PROD001",
            "STOCKS",
        ),
        (
            "PROD001",
            "ORD013",
            "FULFILLS",
        ),
        (
            "WH001",
            "ORD013",
            "SERVES",
        ),
        (
            "ORD013",
            "CUST002",
            "PLACED_BY",
        ),
    }

    for edge in required_edges:

        assert edge in edge_tuples, (
            f"Missing graph edge: {edge}"
        )

    # ---------------------------------------------------------
    # Save complete pipeline fixture
    # ---------------------------------------------------------

    output_path = (
        BASE_DIR
        / "data"
        / "pipeline_graph_supplier_shutdown.json"
    )

    output_path.write_text(
        json.dumps(
            result,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    # ---------------------------------------------------------
    # Success
    # ---------------------------------------------------------

    print()
    print("=" * 80)
    print("PIPELINE + IMPACT GRAPH TEST PASSED")
    print("=" * 80)

    print()
    print("Verified trace:")

    print(
        "SUP001 -> PROD001 -> SHIP001 "
        "-> WH001 -> ORD013 -> CUST002"
    )

    print()
    print(
        f"Pipeline fixture saved to: "
        f"{output_path}"
    )


if __name__ == "__main__":
    main()

