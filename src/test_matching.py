from engine.matching import EntityMatcher


def main():
    matcher = EntityMatcher()

    print("\n" + "=" * 70)
    print("SUPPLYGUARD AI - ENTITY MATCHING TEST")
    print("=" * 70)

    # Test 1: Supplier
    print("\n1. Supplier matching")
    print("-" * 70)

    supplier = matcher.match_supplier(
        "Alpha Components Ltd"
    )

    print(supplier)

    # Test 2: Product
    print("\n2. Product matching")
    print("-" * 70)

    products = matcher.match_products(
        [
            "Industrial Control Boards",
            "Power Supply Modules",
        ]
    )

    for product in products:
        print(product)

    # Test 3: Shipment
    print("\n3. Shipment matching")
    print("-" * 70)

    shipment = matcher.match_shipment(
        "SHIP005"
    )

    print(shipment)

    # Test 4: Warehouse
    print("\n4. Warehouse matching")
    print("-" * 70)

    warehouse = matcher.match_warehouse(
        "Bengaluru Distribution Center"
    )

    print(warehouse)

    # Test 5: Complete extraction
    print("\n5. Complete resolution")
    print("-" * 70)

    extraction = {
        "supplier_name": "Alpha Components Ltd",
        "affected_products": [
            "Industrial Control Boards",
            "Power Supply Modules",
        ],
        "warehouse_name": None,
        "shipment_id": None,
    }

    resolved = matcher.resolve(extraction)

    print(resolved)

    print("\n✅ Matching tests completed")


if __name__ == "__main__":
    main()