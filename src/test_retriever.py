from rag.retriever import PlaybookRetriever


def print_results(query, results):
    print()
    print(f"QUERY: {query}")
    print("-" * 80)

    for result in results:
        print(
            f"{result['rule_id']} | "
            f"{result['title']} | "
            f"similarity={result['similarity']:.4f}"
        )


def main():
    print("=" * 80)
    print("SUPPLYGUARD AI - PLAYBOOK RETRIEVAL TEST")
    print("=" * 80)

    retriever = PlaybookRetriever()
    retriever.load()

    queries = [
        "Can another warehouse provide inventory to cover the shortage?",
        "Can we move some inventory from another warehouse?",
        "Should we expedite an incoming shipment?",
        "Can we ship part of the customer's order now?",
        "Does every recommendation require human approval?",
        "What should happen when the disruption cannot be mapped to our data?",
        "What information must be included as evidence?",
    ]

    for query in queries:
        results = retriever.retrieve(
            query,
            top_k=3
        )

        print_results(query, results)

        assert len(results) == 3

        for result in results:
            assert result["rule_id"].startswith("R")
            assert result["title"]
            assert result["content"]
            assert result["source"]
            assert "similarity" in result

    print()
    print("=" * 80)
    print("PLAYBOOK RETRIEVAL TEST PASSED")
    print("=" * 80)


if __name__ == "__main__":
    main()