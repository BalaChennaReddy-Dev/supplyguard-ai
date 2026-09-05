
from engine.priority import OrderPriorityEngine


def main():
    print("=" * 75)
    print("SUPPLYGUARD AI - ORDER PRIORITY TEST")
    print("=" * 75)

    engine = OrderPriorityEngine()

    affected_orders = [
        {
            "order_id": "ORD013",
            "customer_id": "CUST002",
            "customer_name": "Vertex Robotics",
            "customer_type": "enterprise",
            "service_level": "high",
            "product_id": "PROD001",
            "warehouse_id": "WH001",
            "quantity": 50,
            "fulfillable_quantity": 10,
            "shortage_quantity": 40,
            "required_date": "2026-09-10",
            "order_date": "2026-09-04",
        },
        {
            "order_id": "ORD007",
            "customer_id": "CUST007",
            "customer_name": "FutureTech Manufacturing",
            "customer_type": "enterprise",
            "service_level": "high",
            "product_id": "PROD005",
            "warehouse_id": "WH002",
            "quantity": 60,
            "fulfillable_quantity": 40,
            "shortage_quantity": 20,
            "required_date": "2026-09-09",
            "order_date": "2026-09-03",
        },
    ]

    results = engine.prioritize(
        affected_orders,
        analysis_date="2026-09-05",
    )

    for result in results:
        print()
        print("ORDER")
        print("-" * 75)

        print(
            f"{result['order_id']} | "
            f"{result['customer_name']}"
        )

        print(
            f"Priority: {result['priority']} | "
            f"Score: {result['priority_score']}"
        )

        print(
            f"Required date: {result['required_date']} | "
            f"Days remaining: {result['days_until_required']}"
        )

        print(
            f"Shortage: "
            f"{result['shortage_quantity']} / "
            f"{result['quantity']}"
        )

        print()
        print("Score breakdown:")

        for key, value in result["score_breakdown"].items():
            print(f"  {key}: {value}")

        print()
        print("Reasons:")

        for reason in result["reasons"]:
            print(f"  • {reason}")

    # ------------------------------------------------------------------
    # Assertions
    # ------------------------------------------------------------------

    assert len(results) == 2

    # Verify shortage values.
    shortages = {
        result["order_id"]: result["shortage_quantity"]
        for result in results
    }

    assert shortages["ORD013"] == 40
    assert shortages["ORD007"] == 20

    # Verify operational fields are preserved for Phase 7.
    for result in results:
        assert "warehouse_id" in result
        assert "product_id" in result
        assert "quantity" in result
        assert "fulfillable_quantity" in result
        assert "shortage_quantity" in result
        assert "required_date" in result
        assert "order_date" in result

    # Verify scores are valid.
    assert all(
        0 <= result["priority_score"] <= 100
        for result in results
    )

    # Verify priority labels.
    assert all(
        result["priority"]
        in {"CRITICAL", "HIGH", "MEDIUM", "LOW"}
        for result in results
    )

    # Verify deterministic ranking.
    scores = [
        result["priority_score"]
        for result in results
    ]

    assert scores == sorted(
        scores,
        reverse=True,
    )

    # Verify expected ranking.
    assert results[0]["order_id"] == "ORD013"
    assert results[1]["order_id"] == "ORD007"

    # Verify expected scores.
    assert results[0]["priority_score"] == 79.0
    assert results[1]["priority_score"] == 78.0

    print()
    print("=" * 75)
    print("✅ PRIORITY TEST PASSED")
    print("=" * 75)


if __name__ == "__main__":
    main()

