import os
import json
import chromadb

from rag.embedding import generate_embeddings


CHUNKS_FILE = "data/processed/gtbit_chunks.json"
DB_PATH = "data/chroma_db"
COLLECTION_NAME = "gtbit_knowledge"

BATCH_SIZE = 64


def prepare_metadata(chunk):
    """
    Extract nested metadata and flatten it
    into individual ChromaDB metadata fields.
    """

    metadata = chunk.get("metadata", {})

    clean_metadata = {}

    for key, value in metadata.items():

        if value is None:
            clean_metadata[key] = ""

        elif isinstance(value, (str, int, float, bool)):
            clean_metadata[key] = value

        else:
            clean_metadata[key] = json.dumps(
                value,
                ensure_ascii=False
            )

    # Preserve the unique chunk ID
    clean_metadata["chunk_id"] = chunk.get(
        "chunk_id", ""
    )

    return clean_metadata


def build_vector_store():

    print("Loading chunks...")

    with open(
        CHUNKS_FILE,
        "r",
        encoding="utf-8"
    ) as file:
        data = json.load(file)

    chunks = data.get("chunks", [])

    print("Total chunks:", len(chunks))

    if not chunks:
        raise ValueError("No chunks found.")

    # Initialize ChromaDB
    os.makedirs(DB_PATH, exist_ok=True)

    client = chromadb.PersistentClient(
        path=DB_PATH
    )

    # Delete previous collection
    try:
        client.delete_collection(
            name=COLLECTION_NAME
        )
        print("Previous collection deleted.")

    except Exception:
        print("No previous collection found.")

    # Create fresh collection
    collection = client.create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"}
    )

    print("New collection created.")
    print("Generating embeddings and indexing...")

    total_indexed = 0

    for start in range(0, len(chunks), BATCH_SIZE):

        batch = chunks[start:start + BATCH_SIZE]

        texts = [
            chunk.get("text", "")
            for chunk in batch
        ]

        ids = [
            chunk.get(
                "chunk_id",
                f"chunk_{start + index}"
            )
            for index, chunk in enumerate(batch)
        ]

        metadatas = [
            prepare_metadata(chunk)
            for chunk in batch
        ]

        embeddings = generate_embeddings(texts)

        collection.add(
            ids=ids,
            documents=texts,
            embeddings=embeddings.tolist(),
            metadatas=metadatas
        )

        total_indexed += len(batch)

        print(
            f"Indexed {total_indexed}/{len(chunks)} chunks"
        )

    print("\n" + "=" * 55)
    print("VECTOR STORE BUILD COMPLETED")
    print("=" * 55)

    print("Total chunks indexed:", total_indexed)
    print("Collection:", COLLECTION_NAME)
    print("Database:", DB_PATH)
    print("Stored records:", collection.count())


if __name__ == "__main__":
    build_vector_store()
