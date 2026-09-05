from pathlib import Path

from ai.extractor import DisruptionExtractor


DISRUPTION_DIR = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "disruptions"
)


def main():
    notice_path = DISRUPTION_DIR / "carrier_delay.txt"

    notice = notice_path.read_text(
        encoding="utf-8"
    )

    extractor = DisruptionExtractor()

    result = extractor.extract(notice)

    print("\n===== GEMINI EXTRACTION =====\n")

    for key, value in result.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()