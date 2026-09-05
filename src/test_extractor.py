from pathlib import Path

from ai.extractor import DisruptionExtractor


DISRUPTION_DIR = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "disruptions"
)


TEST_CASES = [
    "supplier_shutdown.txt",
    "carrier_delay.txt",
    "warehouse_incident.txt",
    "ambiguous_disruption.txt",
    "no_impact_disruption.txt",
]


def main():
    extractor = DisruptionExtractor()

    print("\n" + "=" * 70)
    print("SUPPLYGUARD AI - GEMINI EXTRACTION TESTS")
    print("=" * 70)

    for filename in TEST_CASES:
        print(f"\n\n### TEST: {filename}")
        print("-" * 70)

        notice_path = DISRUPTION_DIR / filename

        if not notice_path.exists():
            print(f"❌ File not found: {notice_path}")
            continue

        notice = notice_path.read_text(encoding="utf-8")

        try:
            result = extractor.extract(notice)

            print(f"event_type: {result['event_type']}")
            print(f"supplier_name: {result['supplier_name']}")
            print(f"location: {result['location']}")
            print(f"shipment_id: {result['shipment_id']}")
            print(f"warehouse_name: {result['warehouse_name']}")
            print(f"start_date: {result['start_date']}")
            print(f"duration_days: {result['duration_days']}")
            print(f"affected_products: {result['affected_products']}")
            print(f"description: {result['description']}")
            print(f"confidence: {result['confidence']}")
            print(
                f"missing_information: "
                f"{result['missing_information']}"
            )

            print("\n✅ Extraction successful")

        except Exception as exc:
            print(f"\n❌ Extraction failed: {exc}")


if __name__ == "__main__":
    main()