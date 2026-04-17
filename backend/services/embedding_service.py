"""Embedding and matching service — gracefully degrades without sentence-transformers."""

import logging
import re
from collections import Counter

logger = logging.getLogger(__name__)

_model = None
_available = None


def _get_model():
    global _model, _available
    if _available is None:
        try:
            from sentence_transformers import SentenceTransformer
            _model = SentenceTransformer("all-MiniLM-L6-v2")
            _available = True
            logger.info("Embedding model loaded.")
        except ImportError:
            _available = False
            logger.warning("sentence-transformers not installed. Using keyword matching fallback.")
    return _model


class EmbeddingService:
    """Embedding and matching — falls back to keyword overlap if model unavailable."""

    def embed(self, text: str) -> list[float]:
        model = _get_model()
        if model:
            return model.encode(text, normalize_embeddings=True).tolist()
        return []  # Empty embedding when model unavailable

    def cosine_similarity(self, vec1: list, vec2: list) -> float:
        if not vec1 or not vec2:
            return 0.0
        try:
            import numpy as np
            a = np.array(vec1)
            b = np.array(vec2)
            return float(np.dot(a, b))
        except Exception:
            return 0.0

    def _keyword_match(self, text1: str, text2: str) -> float:
        """Keyword overlap fallback when embeddings unavailable."""
        words1 = set(re.findall(r'\b[a-z]{3,}\b', text1.lower()))
        words2 = set(re.findall(r'\b[a-z]{3,}\b', text2.lower()))
        if not words1 or not words2:
            return 0.0
        overlap = words1 & words2
        return len(overlap) / max(len(words1), len(words2))

    def match_score(self, user_profile_text: str, job_jd_text: str) -> float:
        """Match score: uses embeddings if available, keyword overlap otherwise."""
        model = _get_model()
        if model:
            user_vec = self.embed(user_profile_text)
            job_vec = self.embed(job_jd_text)
            return self.cosine_similarity(user_vec, job_vec)
        return self._keyword_match(user_profile_text, job_jd_text)


embedder = EmbeddingService()
