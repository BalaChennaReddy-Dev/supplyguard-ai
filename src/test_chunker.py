from rag.chunker import PlaybookChunker


def main():
    print("=" * 80)
    print("SUPPLYGUARD AI - PLAYBOOK CHUNK TEST")
    print("=" * 80)

    chunker = PlaybookChunker()
    chunks = chunker.chunk()

    print()
    print(f"Total chunks: {len(chunks)}")

    for chunk in chunks:
        print()
        print(f"{chunk['chunk_id']} — {chunk['title']}")
        print("-" * 80)
        print(f"Source: {chunk['source']}")
        print(f"Characters: {len(chunk['content'])}")

    assert len(chunks) == 12

    expected_rules = [
        "R01",
        "R02",
        "R03",
        "R04",
        "R05",
        "R06",
        "R07",
        "R08",
        "R09",
        "R10",
        "R11",
        "R12",
    ]

    actual_rules = [chunk["rule_id"] for chunk in chunks]

    assert actual_rules == expected_rules

    for chunk in chunks:
        assert chunk["content"]
        assert chunk["source"] == "documents/response_playbook.md"

    print()
    print("=" * 80)
    print("PLAYBOOK CHUNK TEST PASSED")
    print("=" * 80)


if __name__ == "__main__":
    main()