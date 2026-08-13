"""Embedding providers — hackathon prompt section 10.

`EmbeddingProvider` is the interface `vector_search.py` depends on.
`DeterministicEmbeddingProvider` needs no API key/network and is what
tests and local dev use. `GoogleEmbeddingProvider` is the real one for
production (per Tech_stack.txt's "Google Embeddings (Optional)") — it's a
thin wrapper stub, since wiring a live Gemini API key isn't something this
module should do on its own.
"""

from __future__ import annotations

import hashlib
import math
from typing import Protocol


class EmbeddingProvider(Protocol):
    dimensions: int

    def embed(self, text: str) -> list[float]: ...


class DeterministicEmbeddingProvider:
    """Hash-based bag-of-words embedding. Not semantically meaningful in
    the way a real model's embeddings are, but same text -> same vector,
    and different-topic text ends up in different regions of the space
    often enough to sanity-check the retrieval pipeline without any
    external dependency. Good for tests/local dev; swap for
    `GoogleEmbeddingProvider` before relying on retrieval quality.
    """

    def __init__(self, dimensions: int = 64):
        self.dimensions = dimensions

    def embed(self, text: str) -> list[float]:
        vector = [0.0] * self.dimensions
        for word in text.lower().split():
            digest = hashlib.sha256(word.encode()).digest()
            index = int.from_bytes(digest[:4], "big") % self.dimensions
            sign = 1.0 if digest[4] % 2 == 0 else -1.0
            vector[index] += sign
        norm = math.sqrt(sum(v * v for v in vector)) or 1.0
        return [v / norm for v in vector]


class GoogleEmbeddingProvider:
    """Production provider — wraps the Google embeddings API mentioned in
    Technology_Stack.md. Not implemented here: needs an API key/network
    call this module shouldn't make on its own. Implement `embed()` when
    wiring the real `AI_API_KEY`; the rest of `vector_search.py` doesn't
    need to change since it only depends on the `EmbeddingProvider`
    protocol.
    """

    def __init__(self, dimensions: int = 768, api_key: str | None = None):
        self.dimensions = dimensions
        self._api_key = api_key

    def embed(self, text: str) -> list[float]:
        raise NotImplementedError(
            "Wire this to the Google embeddings API once AI_API_KEY is available. "
            "Until then, use DeterministicEmbeddingProvider."
        )
