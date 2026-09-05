import json
from pathlib import Path

from rag.chunker import PlaybookChunker
from rag.embeddings import GeminiEmbeddingClient
from rag.index import LocalRAGIndex


BASE_DIR = Path(__file__).resolve().parent.parent.parent
RAG_DIR = BASE_DIR / "data" / "rag"
EMBEDDINGS_PATH = RAG_DIR / "embeddings.json"


def load_cached_embeddings():
    if not EMBEDDINGS_PATH.exists():
        return None

    return json.loads(
        EMBEDDINGS_PATH.read_text(
            encoding="utf-8"
        )
    )


def save_embeddings(embeddings):
    RAG_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    EMBEDDINGS_PATH.write_text(
        json.dumps(embeddings),
        encoding="utf-8"
    )


def main():
    print("=" * 80)
    print("SUPPLYGUARD AI - BUILD LOCAL RAG INDEX")
    print("=" * 80)

    chunker = PlaybookChunker()
    chunks = chunker.chunk()

    print()
    print(f"Playbook chunks: {len(chunks)}")

    cached = load_cached_embeddings()

    if cached is not None:
        print("Using cached Gemini embeddings.")
        embeddings = cached

    else:
        print()
        print("Generating Gemini embeddings...")
        print("Model: gemini-embedding-001")

        embedding_client = GeminiEmbeddingClient()

        texts = [
            chunk["content"]
            for chunk in chunks
        ]

        embeddings = embedding_client.embed(texts)

        if len(embeddings) != len(chunks):
            raise RuntimeError(
                "Embedding count does not match chunk count."
            )

        save_embeddings(embeddings)

        print("Embeddings generated and cached.")

    metadata = [
        {
            "chunk_id": chunk["chunk_id"],
            "rule_id": chunk["rule_id"],
            "title": chunk["title"],
            "content": chunk["content"],
            "source": chunk["source"],
        }
        for chunk in chunks
    ]

    index = LocalRAGIndex()

    index.build(
        embeddings,
        metadata
    )

    index.save()

    print()
    print("RAG index created successfully.")
    print(f"Vectors: {len(embeddings)}")
    print(f"Index: {index.index_path}")
    print(f"Metadata: {index.metadata_path}")
    print(f"Embeddings: {EMBEDDINGS_PATH}")

    print()
    print("=" * 80)
    print("RAG INDEX BUILD COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()