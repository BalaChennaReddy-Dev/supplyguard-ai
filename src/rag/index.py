import json
from pathlib import Path
from typing import Any

import faiss
import numpy as np


BASE_DIR = Path(__file__).resolve().parent.parent.parent
RAG_DIR = BASE_DIR / "data" / "rag"


class LocalRAGIndex:
    """Persistent local FAISS index with rule metadata."""

    def __init__(
        self,
        index_path: Path | None = None,
        metadata_path: Path | None = None
    ):
        self.index_path = index_path or (
            RAG_DIR / "faiss.index"
        )

        self.metadata_path = metadata_path or (
            RAG_DIR / "metadata.json"
        )

        self.index = None
        self.metadata: list[dict[str, Any]] = []

    def build(
        self,
        embeddings: list[list[float]],
        metadata: list[dict[str, Any]]
    ) -> None:

        if not embeddings:
            raise ValueError(
                "Cannot build an empty FAISS index."
            )

        if len(embeddings) != len(metadata):
            raise ValueError(
                "Embedding count must match metadata count."
            )

        vectors = np.asarray(
            embeddings,
            dtype="float32"
        )

        if vectors.ndim != 2:
            raise ValueError(
                "Embeddings must be a 2D array."
            )

        dimension = vectors.shape[1]

        self.index = faiss.IndexFlatIP(dimension)

        # Normalize vectors so inner product behaves
        # like cosine similarity.
        faiss.normalize_L2(vectors)

        self.index.add(vectors)

        self.metadata = metadata

    def save(self) -> None:
        if self.index is None:
            raise RuntimeError(
                "No FAISS index has been built."
            )

        RAG_DIR.mkdir(
            parents=True,
            exist_ok=True
        )

        faiss.write_index(
            self.index,
            str(self.index_path)
        )

        self.metadata_path.write_text(
            json.dumps(
                self.metadata,
                indent=2,
                ensure_ascii=False
            ),
            encoding="utf-8"
        )

    def load(self) -> None:
        if not self.index_path.exists():
            raise FileNotFoundError(
                f"FAISS index not found: {self.index_path}"
            )

        if not self.metadata_path.exists():
            raise FileNotFoundError(
                f"Metadata not found: {self.metadata_path}"
            )

        self.index = faiss.read_index(
            str(self.index_path)
        )

        self.metadata = json.loads(
            self.metadata_path.read_text(
                encoding="utf-8"
            )
        )

        if self.index.ntotal != len(self.metadata):
            raise ValueError(
                "FAISS index size does not match metadata."
            )

    def search(
        self,
        query_embedding: list[float],
        top_k: int = 3
    ) -> list[dict[str, Any]]:

        if self.index is None:
            raise RuntimeError(
                "FAISS index is not loaded."
            )

        if not self.metadata:
            return []

        top_k = min(
            top_k,
            len(self.metadata)
        )

        query = np.asarray(
            [query_embedding],
            dtype="float32"
        )

        if query.ndim != 2:
            raise ValueError(
                "Query embedding must be one-dimensional."
            )

        faiss.normalize_L2(query)

        scores, indices = self.index.search(
            query,
            top_k
        )

        results = []

        for score, index in zip(
            scores[0],
            indices[0]
        ):
            if index < 0:
                continue

            result = dict(
                self.metadata[index]
            )

            result["similarity"] = float(score)

            results.append(result)

        return results