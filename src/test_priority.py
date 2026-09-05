
from engine.priority import OrderPriorityEngine


def main():
    engine = OrderPriorityEngine()

    affected_orders = [
        {
            "order_id": "ORD013",
            "customer_id": "CUST002",
            "customer_name": "Vertex Robotics",
            "product_id": "PROD001",
            "quantity": 50,
            "shortage_quantity": 40,
            "required_date": "2026-09-10",
            "service_level": "high",
            "customer_type": "enterprise",
        },
        {
            "order_id": "ORD007",
            "customer_id": "CUST007",
            "customer_name": "FutureTech Manufacturing",
            "product_id": "PROD005",
            "quantity": 60,
            "shortage_quantity": 20,
            "required_date": "2026-09-09",
            "service_level": "high",
            "customer_type": "enterprise",
        },
    ]

    results = engine.prioritize(
        affected_orders,
        analysis_date="2026-09-05"
    )

    print("\n" + "=" * 75)
    print("SUPPLYGUARD AI - ORDER PRIORITY TEST")
    print("=" * 75)

    for result in results:
        print("\nORDER")
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
            f"Shortage: {result['shortage']} / "
            f"{result['quantity']}"
        )

        print("\nScore breakdown:")

        for factor, value in result["score_breakdown"].items():
            print(f"  {factor}: {value}")

        print("\nReasons:")

        for reason in result["reasons"]:
            print(f"  • {reason}")

    # Basic validation
    assert len(results) == 2

    # Verify actual shortage values propagated correctly.
    shortages = {
        result["order_id"]: result["shortage"]
        for result in results
    }

    assert shortages["ORD013"] == 40
    assert shortages["ORD007"] == 20

    # Scores must be between 0 and 100.
    assert all(
        0 <= result["priority_score"] <= 100
        for result in results
    )

    # Priority must always be one of the supported levels.
    assert all(
        result["priority"] in {
            "CRITICAL",
            "HIGH",
            "MEDIUM",
            "LOW",
        }
        for result in results
    )

    # Results must be sorted by descending priority score.
    scores = [
        result["priority_score"]
        for result in results
    ]

    assert scores == sorted(
        scores,
        reverse=True
    )

    print("\n" + "=" * 75)
    print("✅ PRIORITY TEST PASSED")
    print("=" * 75)


if __name__ == "__main__":
    main()
