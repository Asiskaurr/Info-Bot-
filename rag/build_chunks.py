import os
import json
import hashlib

from rag.chunking import chunk_pages


INPUT_FILE = "data/processed/gtbit_unified_dataset.json"

OUTPUT_FOLDER = "data/processed"
OUTPUT_FILE = os.path.join(
    OUTPUT_FOLDER,
    "gtbit_chunks.json"
)

MAX_TOKENS = 220


def get_unique_filename(document):

    if document.get("filename"):
        return document["filename"]

    source = (
        document.get("source_url")
        or document.get("document_id")
        or document.get("title", "")
    )

    unique_hash = hashlib.md5(
        source.encode("utf-8")
    ).hexdigest()[:12]

    return f"website_{unique_hash}.html"


def main():

    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    print("Loading unified dataset...")

    with open(
        INPUT_FILE,
        "r",
        encoding="utf-8"
    ) as file:
        dataset = json.load(file)

    documents = dataset.get("documents", [])

    print("Total documents:", len(documents))
    print("Chunk token limit:", MAX_TOKENS)

    all_chunks = []

    successful = 0
    failed = 0
    empty_documents = 0

    for index, document in enumerate(
        documents,
        start=1
    ):

        title = document.get("title", "Untitled")

        print(
            f"\n[{index}/{len(documents)}] "
            f"Processing: {title[:70]}"
        )

        try:

            pages = document.get("pages", [])

            if not pages:
                empty_documents += 1
                continue

            filename = get_unique_filename(document)

            # Metadata passed to the chunker
            metadata = {
                "document_id": document.get(
                    "document_id", ""
                ),
                "source_type": document.get(
                    "source_type", ""
                ),
                "title": title,
                "filename": filename,
                "source_url": document.get(
                    "source_url", ""
                ),
                "source_page": document.get(
                    "source_page", ""
                ),
                "link_text": document.get(
                    "link_text", ""
                )
            }

            # Generate chunks
            chunks = chunk_pages(
                pages,
                metadata,
                max_tokens=MAX_TOKENS
            )

            all_chunks.extend(chunks)

            successful += 1

            print("Chunks generated:", len(chunks))

        except Exception as error:

            failed += 1

            print("Processing failed:", error)

    # Save all chunks
    output_data = {
        "total_documents": len(documents),
        "successfully_processed": successful,
        "failed_documents": failed,
        "empty_documents": empty_documents,
        "max_tokens": MAX_TOKENS,
        "total_chunks": len(all_chunks),
        "chunks": all_chunks
    }

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            output_data,
            file,
            ensure_ascii=False,
            indent=2
        )

    print("\n" + "=" * 55)
    print("CHUNKING COMPLETED")
    print("=" * 55)

    print("Total documents:", len(documents))
    print("Successfully processed:", successful)
    print("Failed documents:", failed)
    print("Empty documents:", empty_documents)
    print("Total chunks generated:", len(all_chunks))
    print("Output file:", OUTPUT_FILE)


if __name__ == "__main__":
    main()
