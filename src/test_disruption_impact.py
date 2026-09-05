import json
import sys
from pathlib import Path

from ai.extractor import DisruptionExtractor
from engine.impact import ImpactEngine
from engine.matching import EntityMatcher


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DISRUPTION_DIR = PROJECT_ROOT / "data" / "disruptions"
EXTRACTION_DIR = PROJECT_ROOT / "data" / "extractions"


TEST_CASES = [
    "supplier_shutdown.txt",
    "carrier_delay.txt",
    "warehouse_incident.txt",
    "ambiguous_disruption.txt",
    "no_impact_disruption.txt",
]


def load_fixture(filename):
    fixture_name = Path(filename).stem + ".json"
    fixture_path = EXTRACTION_DIR / fixture_name

    if not fixture_path.exists():
        raise FileNotFoundError(
            f"Extraction fixture not found: {fixture_path}"
        )

    with fixture_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def print_extraction(extraction):
    print("\nEXTRACTION")
    print("-" * 70)

    print("Event type:", extraction.get("event_type"))
    print("Supplier:", extraction.get("supplier_name"))
    print("Location:", extraction.get("location"))
    print("Shipment:", extraction.get("shipment_id"))
    print("Warehouse:", extraction.get("warehouse_name"))
    print("Start date:", extraction.get("start_date"))
    print("Duration:", extraction.get("duration_days"))
    print("Products:", extraction.get("affected_products"))
    print("Confidence:", extraction.get("confidence"))


def print_resolution(resolved):
    print("\nENTITY RESOLUTION")
    print("-" * 70)

    supplier = resolved.get("supplier")
    warehouse = resolved.get("warehouse")
    shipment = resolved.get("shipment")
    products = resolved.get("products", [])

    print(
        "Supplier:",
        supplier.get("supplier_id") if supplier else None
    )

    print(
        "Products:",
        [product.get("product_id") for product in products]
    )

    print(
        "Warehouse:",
        warehouse.get("warehouse_id") if warehouse else None
    )

    print(
        "Shipment:",
        shipment.get("shipment_id") if shipment else None
    )


def print_impact(result):
    print("\nIMPACT RESULT")
    print("-" * 70)

    print("Impact found:", result.get("impact_found"))
    print("Impact status:", result.get("impact_status"))
    print("Reason:", result.get("reason"))

    print("\nAFFECTED SHIPMENTS")

    shipments = result.get("affected_shipments", [])

    if not shipments:
        print("None")

    for shipment in shipments:
        print(
            shipment.get("shipment_id"),
            "|",
            shipment.get("product_id"),
            "| quantity:",
            shipment.get("quantity"),
            "| original expected:",
            shipment.get("original_expected_date"),
            "| projected expected:",
            shipment.get("projected_expected_date"),
        )

    print("\nAT-RISK ORDERS")

    orders = result.get("at_risk_orders", [])

    if not orders:
        print("None")

    for order in orders:
        print(
            order.get("order_id"),
            "|",
            order.get("customer_name"),
            "|",
            order.get("product_id"),
            "| shortage:",
            order.get("shortage_quantity"),
            "| required:",
            order.get("required_date"),
        )

    print("\nPOTENTIALLY AFFECTED ORDERS")

    potential_orders = result.get(
        "potentially_affected_orders",
        []
    )

    if not potential_orders:
        print("None")

    for order in potential_orders:
        print(
            order.get("order_id"),
            "|",
            order.get("customer_name"),
            "|",
            order.get("product_id"),
            "| status:",
            order.get("risk_status"),
        )

    print("\nAFFECTED CUSTOMERS")

    customers = result.get("affected_customers", [])

    if not customers:
        print("None")

    for customer in customers:
        print(
            customer.get("customer_id"),
            "|",
            customer.get("customer_name"),
            "|",
            customer.get("service_level"),
        )


def run_test(filename, use_fixtures=False):
    print("\n")
    print("#" * 75)
    print(f"TEST CASE: {filename}")
    print("#" * 75)

    notice_path = DISRUPTION_DIR / filename

    if not notice_path.exists():
        print(f"❌ Notice not found: {notice_path}")
        return False

    notice = notice_path.read_text(encoding="utf-8")

    # ---------------------------------------------------------
    # STEP 1 — Extract disruption information
    # ---------------------------------------------------------

    if use_fixtures:
        print("\n🧪 MODE: SAVED GEMINI EXTRACTION FIXTURE")

        try:
            extraction = load_fixture(filename)
        except Exception as exc:
            print("❌ FIXTURE LOAD FAILED")
            print("Error:", exc)
            return False

    else:
        print("\n🤖 MODE: LIVE GEMINI")

        extractor = DisruptionExtractor()

        try:
            extraction = extractor.extract(notice)
        except Exception as exc:
            print("\n❌ GEMINI EXTRACTION FAILED")
            print("Error:", exc)
            print(
                "Skipping this test case because the disruption "
                "could not be interpreted."
            )
            return False

    print_extraction(extraction)

    # ---------------------------------------------------------
    # STEP 2 — Resolve entities against operational data
    # ---------------------------------------------------------

    matcher = EntityMatcher()
    resolved = matcher.resolve(extraction)

    print_resolution(resolved)

    # ---------------------------------------------------------
    # STEP 3 — Deterministic impact analysis
    # ---------------------------------------------------------

    engine = ImpactEngine()

    result = engine.analyze_disruption(
        extraction,
        resolved,
    )

    print_impact(result)

    print("\n✅ TEST COMPLETED")

    return True


def main():
    use_fixtures = "--fixtures" in sys.argv

    print("\n" + "=" * 75)
    print("SUPPLYGUARD AI - END-TO-END DISRUPTION IMPACT TEST")
    print("=" * 75)

    if use_fixtures:
        print("\n🧪 Using saved extraction fixtures.")
        print("Gemini API will NOT be called.")
    else:
        print("\n🤖 Using live Gemini extraction.")

    successful = 0

    for filename in TEST_CASES:
        if run_test(filename, use_fixtures):
            successful += 1

    print("\n")
    print("=" * 75)
    print(
        f"TESTS COMPLETED: {successful}/{len(TEST_CASES)}"
    )
    print("=" * 75)


if __name__ == "__main__":
    main()