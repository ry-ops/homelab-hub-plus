"""
Qdrant-backed semantic search service.

Each inventory entity is embedded as a single document combining its
most descriptive fields. Vectors are upserted on create/update and
deleted on entity deletion.

Embedding model: all-MiniLM-L6-v2 (384-dim, ~80MB, runs on CPU fine)

Usage:
    from app.services.search import SearchService

    SearchService.upsert(entity_type="hardware", entity_id=1, entity_dict={...})
    SearchService.delete(entity_type="hardware", entity_id=1)
    results = SearchService.query("old nas box in basement", limit=10)
"""
import logging
import os

from flask import current_app

logger = logging.getLogger(__name__)

# Lazily loaded singletons
_embedder = None
_qdrant = None


def _get_embedder():
    global _embedder
    if _embedder is None:
        from sentence_transformers import SentenceTransformer
        _embedder = SentenceTransformer("all-MiniLM-L6-v2")
    return _embedder


def _get_qdrant():
    global _qdrant
    if _qdrant is None:
        from qdrant_client import QdrantClient
        url = current_app.config.get("QDRANT_URL", "http://localhost:6333")
        _qdrant = QdrantClient(url=url)
        _ensure_collection(_qdrant)
    return _qdrant


def _ensure_collection(client):
    from qdrant_client.models import Distance, VectorParams
    collection = current_app.config.get("QDRANT_COLLECTION", "homelab")
    existing = [c.name for c in client.get_collections().collections]
    if collection not in existing:
        client.create_collection(
            collection_name=collection,
            vectors_config=VectorParams(size=384, distance=Distance.COSINE),
        )
        logger.info("Created Qdrant collection: %s", collection)


def _make_text(entity_type: str, data: dict) -> str:
    """Flatten an entity dict into a searchable text blob."""
    # Fields to skip — noisy or binary
    skip = {"id", "created_at", "updated_at", "icon"}
    parts = [entity_type.replace("_", " ")]
    for key, val in data.items():
        if key in skip or val is None or val == "":
            continue
        label = key.replace("_", " ")
        parts.append(f"{label}: {val}")
    return " | ".join(parts)


def _point_id(entity_type: str, entity_id: int) -> int:
    """
    Map (entity_type, entity_id) to a stable uint64 Qdrant point ID.
    Uses a simple namespace prefix to avoid collisions across types.
    """
    NAMESPACE = {
        "hardware": 1,
        "vms": 2,
        "apps": 3,
        "storage": 4,
        "networks": 5,
        "misc": 6,
        "shares": 7,
        "documents": 8,
    }
    ns = NAMESPACE.get(entity_type, 9)
    return ns * 10_000_000 + entity_id


class SearchService:
    @staticmethod
    def upsert(entity_type: str, entity_id: int, entity_dict: dict):
        try:
            from qdrant_client.models import PointStruct
            client = _get_qdrant()
            embedder = _get_embedder()
            collection = current_app.config.get("QDRANT_COLLECTION", "homelab")

            text = _make_text(entity_type, entity_dict)
            vector = embedder.encode(text).tolist()

            client.upsert(
                collection_name=collection,
                points=[
                    PointStruct(
                        id=_point_id(entity_type, entity_id),
                        vector=vector,
                        payload={
                            "entity_type": entity_type,
                            "entity_id": entity_id,
                            "name": entity_dict.get("name", ""),
                            "text": text,
                        },
                    )
                ],
            )
        except Exception:
            logger.exception("Qdrant upsert failed for %s/%s", entity_type, entity_id)

    @staticmethod
    def delete(entity_type: str, entity_id: int):
        try:
            from qdrant_client.models import PointIdsList
            client = _get_qdrant()
            collection = current_app.config.get("QDRANT_COLLECTION", "homelab")
            client.delete(
                collection_name=collection,
                points_selector=PointIdsList(points=[_point_id(entity_type, entity_id)]),
            )
        except Exception:
            logger.exception("Qdrant delete failed for %s/%s", entity_type, entity_id)

    @staticmethod
    def query(q: str, limit: int = 20) -> list[dict]:
        try:
            client = _get_qdrant()
            embedder = _get_embedder()
            collection = current_app.config.get("QDRANT_COLLECTION", "homelab")

            vector = embedder.encode(q).tolist()
            hits = client.search(
                collection_name=collection,
                query_vector=vector,
                limit=limit,
                with_payload=True,
            )
            return [
                {
                    "entity_type": h.payload["entity_type"],
                    "entity_id": h.payload["entity_id"],
                    "name": h.payload.get("name", ""),
                    "score": round(h.score, 4),
                }
                for h in hits
            ]
        except Exception:
            logger.exception("Qdrant query failed")
            return []
