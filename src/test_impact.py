from engine.impact import ImpactEngine


def main():

    engine = ImpactEngine()

    print("\n" + "=" * 70)
    print("SUPPLYGUARD AI - DETERMINISTIC IMPACT ENGINE")
    print("=" * 70)

    result = engine.analyze(
        supplier_id="SUP001",
        product_ids=[
            "PROD001",
            "PROD002",
        ],
    )

    print("\nAFFECTED SHIPMENTS")
    print("-" * 70)

    for shipment in result["affected_shipments"]:
        print(
            shipment["shipment_id"],
            "|",
            shipment["product_id"],
            "|",
            shipment["quantity"],
            "|",
            shipment["expected_date"],
        )

    print("\nINVENTORY SUMMARY")
    print("-" * 70)

    for item in result["inventory_summary"]:
        print(item)

    print("\nORDER SUMMARY")
    print("-" * 70)

    for item in result["order_summary"]:
        print(item)

    print("\nAT-RISK ORDERS")
    print("-" * 70)

    for order in result["at_risk_orders"]:
        print(
            order["order_id"],
            "|",
            order["customer_name"],
            "|",
            order["product_id"],
            "|",
            "ordered:",
            order["quantity"],
            "|",
            "fulfillable:",
            order["fulfillable_quantity"],
            "|",
            "shortage:",
            order["shortage_quantity"],
            "|",
            "required:",
            order["required_date"],
        )

    print("\nAFFECTED CUSTOMERS")
    print("-" * 70)

    for customer in result["affected_customers"]:
        print(
            customer["customer_id"],
            "|",
            customer["customer_name"],
            "|",
            customer["service_level"],
        )

    print("\nIMPACT FOUND:", result["impact_found"])

    print("\n✅ Impact analysis completed")


if __name__ == "__main__":
    main()