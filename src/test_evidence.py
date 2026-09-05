from engine.evidence import EvidenceEngine


def main():
    print("=" * 80)
    print("SUPPLYGUARD AI - EVIDENCE ENGINE TEST")
    print("=" * 80)

    engine = EvidenceEngine()

    order = {
        "order_id": "ORD013",
        "customer_id": "CUST002",
        "product_id": "PROD001",
        "warehouse_id": "WH001",
        "quantity": 50,
        "fulfillable_quantity": 10,
        "shortage_quantity": 40,
        "required_date": "2026-09-10",
    }

    evidence = engine.order_evidence(order)

    print()
    print("ORDER EVIDENCE")
    print("-" * 80)

    for item in evidence:
        print(
            f"{item['source']} | "
            f"{item['record_id']} | "
            f"{item['fact']}"
        )

    assert len(evidence) == 4

    for item in evidence:
        assert "source" in item
        assert "record_id" in item
        assert "fact" in item

        assert item["source"]
        assert item["record_id"]
        assert item["fact"]

    assert evidence[0]["source"] == "orders.csv"
    assert evidence[0]["record_id"] == "ORD013"

    assert evidence[1]["source"] == "inventory.csv"
    assert evidence[1]["record_id"] == "WH001:PROD001"

    assert evidence[2]["record_id"] == "ORD013"

    assert evidence[3]["source"] == "customers.csv"
    assert evidence[3]["record_id"] == "CUST002"

    print()
    print("SHIPMENT EVIDENCE")
    print("-" * 80)

    shipment = {
        "shipment_id": "SHIP001",
        "product_id": "PROD001",
        "warehouse_id": "WH001",
        "quantity": 100,
        "original_expected_date": "2026-09-08",
    }

    shipment_evidence = engine.shipment_evidence(
        shipment
    )

    print(
        f"{shipment_evidence['source']} | "
        f"{shipment_evidence['record_id']} | "
        f"{shipment_evidence['fact']}"
    )

    assert shipment_evidence["source"] == "shipments.csv"
    assert shipment_evidence["record_id"] == "SHIP001"

    print()
    print("INVENTORY EVIDENCE")
    print("-" * 80)

    inventory = {
        "warehouse_id": "WH001",
        "product_id": "PROD001",
        "quantity": 120,
        "reserved_quantity": 80,
    }

    inventory_evidence = engine.inventory_evidence(
        inventory
    )

    print(
        f"{inventory_evidence['source']} | "
        f"{inventory_evidence['record_id']} | "
        f"{inventory_evidence['fact']}"
    )

    assert inventory_evidence["source"] == "inventory.csv"
    assert inventory_evidence["record_id"] == "WH001:PROD001"

    assert "40 available" in inventory_evidence["fact"]

    print()
    print("=" * 80)
    print("EVIDENCE ENGINE TEST PASSED")
    print("=" * 80)


if __name__ == "__main__":
    main()