from pathlib import Path


DISRUPTION_DIR = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "disruptions"
)


def main():
    files = sorted(DISRUPTION_DIR.glob("*.txt"))

    print("Disruption scenarios found:")
    print()

    for file in files:
        content = file.read_text(encoding="utf-8")

        print(f"✓ {file.name}")
        print(f"  Characters: {len(content)}")
        print()


if __name__ == "__main__":
    main()