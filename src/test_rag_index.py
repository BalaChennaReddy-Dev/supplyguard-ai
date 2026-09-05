import numpy as np

from rag.chunker import PlaybookChunker
from rag.index import LocalRAGIndex


def main():
    print("=" * 80)
    print("SUPPLYGUARD AI - LOCAL RAG INDEX TEST")
    print("=" * 80)

    chunker = PlaybookChunker()
    chunks = chunker.chunk()

    assert len(chunks) == 12

    # Fake embeddings for the offline structural test.
    # Gemini is NOT called by this test.
    embeddings = []

    for index, _ in enumerate(chunks):
        vector = np.zeros(8, dtype="float32")
        vector[index % 8] = 1.0
        embeddings.append(vector.tolist())

    metadata = []

    for chunk in chunks:
        metadata.append({
            "chunk_id": chunk["chunk_id"],
            "rule_id": chunk["rule_id"],
            "title": chunk["title"],
            "content": chunk["content"],
            "source": chunk["source"],
        })

    rag_index = LocalRAGIndex()

    rag_index.build(
        embeddings,
        metadata
    )

    assert rag_index.index is not None
    assert rag_index.index.ntotal == 12

    # Test persistence using temporary files.
    import tempfile
    from pathlib import Path

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        test_index = LocalRAGIndex(
            index_path=temp_path / "test.index",
            metadata_path=temp_path / "metadata.json"
        )

        test_index.build(
            embeddings,
            metadata
        )

        test_index.save()

        loaded_index = LocalRAGIndex(
            index_path=temp_path / "test.index",
            metadata_path=temp_path / "metadata.json"
        )

        loaded_index.load()

        assert loaded_index.index.ntotal == 12
        assert len(loaded_index.metadata) == 12

        results = loaded_index.search(
            embeddings[0],
            top_k=3
        )

        assert len(results) == 3

        expected_rules = {
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
        }

        returned_rule_ids = {
            result["rule_id"]
            for result in results
        }

        assert returned_rule_ids.issubset(
            expected_rules
        )

        for result in results:
            assert "chunk_id" in result
            assert "rule_id" in result
            assert "title" in result
            assert "content" in result
            assert "source" in result
            assert "similarity" in result

    print()
    print("Chunks indexed: 12")
    print("FAISS vectors: 12")
    print("Persistence: PASSED")
    print("Search: PASSED")
    print()
    print("=" * 80)
    print("LOCAL RAG INDEX TEST PASSED")
    print("=" * 80)


if __name__ == "__main__":
    main()