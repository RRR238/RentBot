"""
Migration script: adds BM42 sparse vectors to the Qdrant collection.

Because Qdrant does not allow adding sparse vectors to an existing collection
via update_collection, this script:
  1. Scrolls all existing points (dense vector + payload).
  2. Fetches title + description from Postgres for each point.
  3. Generates BM42 sparse vectors via fastembed.
  4. Deletes the old collection.
  5. Recreates it with the same dense config + sparse vector config.
  6. Re-inserts all points with both dense and sparse vectors.
"""

import os
import time
from dotenv import load_dotenv
from fastembed import SparseTextEmbedding
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance, VectorParams,
    SparseVector, SparseVectorParams, SparseIndexParams,
    PointStruct,
)
from Scrapping.Rent_offers_repository import Rent_offers_repository

load_dotenv()

QDRANT_ENDPOINT    = os.getenv("QDRANT_ENDPOINT")
QDRANT_API_KEY     = os.getenv("QDRANT_API_KEY")
CONN_STRING        = os.getenv("connection_string")
COLLECTION_NAME    = "rent-bot-index"
SPARSE_VECTOR_NAME = "text-sparse"
DENSE_VECTOR_DIM   = 3072   # text-embedding-3-large
BATCH_SIZE         = 50


def scroll_all_points_with_vectors(client: QdrantClient) -> list[dict]:
    """Return list of {qdrant_id, dense_vector, payload} for every point."""
    all_points = []
    offset = None
    while True:
        response = client.scroll(
            collection_name=COLLECTION_NAME,
            limit=BATCH_SIZE,
            with_payload=True,
            with_vectors=True,
            offset=offset,
        )
        points, offset = response
        if not points:
            break
        for p in points:
            # Dense vector stored unnamed → comes back as a plain list
            vec = p.vector
            if isinstance(vec, dict):
                vec = vec.get("") or next(iter(vec.values()), None)
            all_points.append({
                "qdrant_id": p.id,
                "dense_vector": vec,
                "payload": p.payload or {},
            })
        if offset is None:
            break
    return all_points


def build_text(title: str | None, description: str | None) -> str:
    parts = []
    if title:
        parts.append(title)
    if description:
        parts.append(description)
    return " ".join(parts)


def main():
    client = QdrantClient(url=QDRANT_ENDPOINT, api_key=QDRANT_API_KEY)
    db = Rent_offers_repository(CONN_STRING)

    # ------------------------------------------------------------------ #
    # 1. Load all existing points (dense vectors + payloads)
    # ------------------------------------------------------------------ #
    print("Scrolling all Qdrant points (including dense vectors)...")
    points = scroll_all_points_with_vectors(client)
    print(f"Found {len(points)} points.")

    if not points:
        print("Nothing to migrate.")
        return

    # ------------------------------------------------------------------ #
    # 2. Generate sparse vectors
    # ------------------------------------------------------------------ #
    print("Loading BM42 model...")
    sparse_model = SparseTextEmbedding(
        model_name="Qdrant/bm42-all-minilm-l6-v2-attentions"
    )

    print("Generating sparse vectors...")
    enriched = []
    skipped = 0
    for i, point in enumerate(points):
        postgres_id = point["payload"].get("id")
        offer = db.get_offer_by_id_or_url(int(postgres_id)) if postgres_id else None
        if offer is None:
            print(f"  [WARN] No Postgres record for id={postgres_id} — skipping.")
            skipped += 1
            continue

        text = build_text(offer.title, offer.description)
        if not text.strip():
            print(f"  [WARN] Empty text for id={postgres_id} — skipping.")
            skipped += 1
            continue

        sparse_result = list(sparse_model.embed([text]))[0]
        enriched.append({
            "qdrant_id": point["qdrant_id"],
            "dense_vector": point["dense_vector"],
            "sparse_vector": SparseVector(
                indices=sparse_result.indices.tolist(),
                values=sparse_result.values.tolist(),
            ),
            "payload": point["payload"],
        })

        if (i + 1) % 100 == 0:
            print(f"  {i + 1}/{len(points)} sparse vectors generated...")

    print(f"Generated {len(enriched)} sparse vectors ({skipped} skipped).")

    # ------------------------------------------------------------------ #
    # 3. Recreate collection with sparse vector config
    # ------------------------------------------------------------------ #
    print(f"\nDeleting collection '{COLLECTION_NAME}'...")
    client.delete_collection(COLLECTION_NAME)

    print(f"Recreating collection with dense + sparse vector config...")
    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=DENSE_VECTOR_DIM, distance=Distance.COSINE),
        sparse_vectors_config={
            SPARSE_VECTOR_NAME: SparseVectorParams(
                index=SparseIndexParams(on_disk=False)
            )
        },
    )
    print("Collection recreated.")

    # ------------------------------------------------------------------ #
    # 4. Re-insert all points
    # ------------------------------------------------------------------ #
    print(f"\nRe-inserting {len(enriched)} points...")
    total_inserted = 0

    for batch_start in range(0, len(enriched), BATCH_SIZE):
        batch = enriched[batch_start: batch_start + BATCH_SIZE]
        new_points = []
        for item in batch:
            new_points.append(
                PointStruct(
                    id=item["qdrant_id"],
                    vector={
                        "": item["dense_vector"],           # unnamed dense vector
                        SPARSE_VECTOR_NAME: item["sparse_vector"],
                    },
                    payload=item["payload"],
                )
            )

        client.upsert(collection_name=COLLECTION_NAME, points=new_points)
        total_inserted += len(new_points)
        print(f"  Inserted {total_inserted}/{len(enriched)}...")

    print(f"\nDone. Migrated {total_inserted} points.")


if __name__ == "__main__":
    t0 = time.time()
    main()
    print(f"Total time: {time.time() - t0:.1f}s")
