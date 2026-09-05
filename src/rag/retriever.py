from typing import Any

from rag.embeddings import GeminiEmbeddingClient
from rag.index import LocalRAGIndex


class PlaybookRetriever:
    """Retrieve the most relevant operational rules."""

    def __init__(
        self,
        index: LocalRAGIndex | None = None,
        embedding_client: GeminiEmbeddingClient | None = None
    ):
        self.index = index or LocalRAGIndex()
        self.embedding_client = embedding_client

    def load(self) -> None:
        self.index.load()

    def retrieve(
        self,
        query: str,
        top_k: int = 3
    ) -> list[dict[str, Any]]:

        if not query.strip():
            return []

        if self.embedding_client is None:
            self.embedding_client = GeminiEmbeddingClient()

        embeddings = self.embedding_client.embed([query])

        if not embeddings:
            return []

        return self.index.search(
            embeddings[0],
            top_k=top_k
        )