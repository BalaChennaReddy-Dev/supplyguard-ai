import json
from pathlib import Path

from engine.impact import ImpactEngine
from engine.impact_graph import ImpactGraphBuilder
from engine.priority import OrderPriorityEngine


BASE_DIR = Path(__file__).resolve().parent.parent
FIXTURE_PATH = BASE_DIR / "data" / "extractions" / "supplier_shutdown.json"


def load_fixture():
    return json.loads(
        FIXTURE_PATH.read_text(
            encoding="utf-8"
        )
    )


def find_edge(
    edges,
    source,
    target,
    relationship,
):
    return any(
        edge["source"] == source
        and edge["target"] == target
        and edge["relationship"] == relationship
        for edge in edges
    )


def main():

    print("=" * 80)
    print("SUPPLYGUARD AI - IMPACT GRAPH TEST")
    print("=" * 80)

    extraction = load_fixture()

    impact_engine = ImpactEngine()

    # Resolve entities using the existing matcher.
    from engine.matching import EntityMatcher

    matcher = EntityMatcher()

    resolved = matcher.resolve(
        extraction
    )

    impact_result = impact_engine.analyze_disruption(
        extraction,
        resolved,
    )

    priority_engine = OrderPriorityEngine()

    prioritized_orders = priority_engine.prioritize(
        impact_result["at_risk_orders"],
        analysis_date="2026-09-05",
    )

    graph_builder = ImpactGraphBuilder()

    graph = graph_builder.build(
        impact_result,
        prioritized_orders,
    )

    nodes = graph["nodes"]
    edges = graph["edges"]

    node_ids = {
        node["id"]
        for node in nodes
    }

    print()
    print(f"Nodes: {graph['node_count']}")
    print(f"Edges: {graph['edge_count']}")

    print()
    print("NODES")
    print("-" * 80)

    for node in nodes:
        print(
            f"{node['id']} | "
            f"{node['type']} | "
            f"{node['label']}"
        )

    print()
    print("EDGES")
    print("-" * 80)

    for edge in edges:
        print(
            f"{edge['source']} "
            f"--{edge['relationship']}--> "
            f"{edge['target']}"
        )

    # ---------------------------------------------------------
    # Verify required nodes
    # ---------------------------------------------------------

    required_nodes = {
        "SUP001",
        "PROD001",
        "SHIP001",
        "WH001",
        "ORD013",
        "CUST002",
        "INV:WH001:PROD001",
    }

    assert required_nodes.issubset(
        node_ids
    ), (
        "Required graph nodes are missing: "
        f"{required_nodes - node_ids}"
    )

    # ---------------------------------------------------------
    # Verify supply-chain relationships
    # ---------------------------------------------------------

    assert find_edge(
        edges,
        "SUP001",
        "PROD001",
        "SUPPLIES",
    )

    assert find_edge(
        edges,
        "PROD001",
        "SHIP001",
        "SHIPPED_AS",
    )

    assert find_edge(
        edges,
        "SHIP001",
        "WH001",
        "DELIVERS_TO",
    )

    assert find_edge(
        edges,
        "WH001",
        "INV:WH001:PROD001",
        "STORES",
    )

    assert find_edge(
        edges,
        "INV:WH001:PROD001",
        "PROD001",
        "STOCKS",
    )

    assert find_edge(
        edges,
        "PROD001",
        "ORD013",
        "FULFILLS",
    )

    assert find_edge(
        edges,
        "WH001",
        "ORD013",
        "SERVES",
    )

    assert find_edge(
        edges,
        "ORD013",
        "CUST002",
        "PLACED_BY",
    )

    # ---------------------------------------------------------
    # Verify order priority information
    # ---------------------------------------------------------

    order_node = next(
        node
        for node in nodes
        if node["id"] == "ORD013"
    )

    assert order_node["priority"] == "HIGH"
    assert order_node["priority_score"] == 79.0
    assert order_node["shortage_quantity"] == 40

    # ---------------------------------------------------------
    # Save a readable graph fixture
    # ---------------------------------------------------------

    output_path = (
        BASE_DIR
        / "data"
        / "impact_graph_supplier_shutdown.json"
    )

    output_path.write_text(
        json.dumps(
            graph,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print()
    print("=" * 80)
    print("IMPACT GRAPH TEST PASSED")
    print("=" * 80)

    print()
    print(
        "Verified trace:"
    )

    print(
        "SUP001 -> PROD001 -> SHIP001 "
        "-> WH001 -> ORD013 -> CUST002"
    )

    print()
    print(
        f"Graph fixture saved to: {output_path}"
    )


if __name__ == "__main__":
    main()