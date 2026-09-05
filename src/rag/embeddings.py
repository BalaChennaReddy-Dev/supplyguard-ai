import os
from typing import Any

from dotenv import load_dotenv
from google import genai


load_dotenv()


class GeminiEmbeddingClient:
    """Generate embeddings using Google's gemini-embedding-001 model."""

    MODEL_NAME = "gemini-embedding-001"

    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise RuntimeError(
                "GEMINI_API_KEY is not configured."
            )

        self.client = genai.Client(api_key=api_key)

    def embed(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []

        response = self.client.models.embed_content(
            model=self.MODEL_NAME,
            contents=texts,
        )

        embeddings = []

        for embedding in response.embeddings:
            embeddings.append(embedding.values)

        return embeddings