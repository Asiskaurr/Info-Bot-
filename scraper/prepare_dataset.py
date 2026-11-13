import os
import json
import hashlib


WEBSITE_FILE = "data/raw/gtbit_website_data.json"
PDF_FOLDER = "data/cleaned/pdf_text"

OUTPUT_FOLDER = "data/processed"
OUTPUT_FILE = os.path.join(
    OUTPUT_FOLDER,
    "gtbit_unified_dataset.json"
)


def create_document_id(source_type, source):
    unique_value = f"{source_type}_{source}"
    return hashlib.md5(
        unique_value.encode("utf-8")
    ).hexdigest()


def process_website_pages():

    print("\nLoading website data...")

    with open(
        WEBSITE_FILE,
        "r",
        encoding="utf-8"
    ) as file:
        website_data = json.load(file)

    documents = []

    for page in website_data.get("pages", []):

        url = page.get("url", "")

        document = {
            "document_id": create_document_id(
                "website",
                url
            ),
            "source_type": "website",
            "title": page.get("title", ""),
            "source_url": url,
            "source_page": url,
            "filename": "",
            "link_text": "",
            "headings": page.get("headings", []),
            "total_pages": 1,
            "scanned_pages": [],
            "pages": [
                {
                    "page_number": 1,
                    "text": page.get("content", "")
                }
            ]
        }

        documents.append(document)

    print("Website pages processed:", len(documents))

    return documents


def process_pdf_documents():

    print("\nLoading processed PDFs...")

    documents = []

    if not os.path.exists(PDF_FOLDER):
        raise FileNotFoundError(
            f"PDF folder not found: {PDF_FOLDER}"
        )

    json_files = [
        filename
        for filename in os.listdir(PDF_FOLDER)
        if filename.lower().endswith(".json")
    ]

    for index, filename in enumerate(
        sorted(json_files),
        start=1
    ):

        filepath = os.path.join(
            PDF_FOLDER,
            filename
        )

        try:

            with open(
                filepath,
                "r",
                encoding="utf-8"
            ) as file:
                pdf_data = json.load(file)

            original_filename = pdf_data.get(
                "filename",
                filename.replace(".json", ".pdf")
            )

            document = {
                "document_id": create_document_id(
                    "pdf",
                    original_filename
                ),
                "source_type": "pdf",
                "title": original_filename,
                "source_url": pdf_data.get(
                    "source_url",
                    ""
                ),
                "source_page": pdf_data.get(
                    "source_page",
                    ""
                ),
                "filename": original_filename,
                "link_text": pdf_data.get(
                    "link_text",
                    ""
                ),
                "headings": [],
                "total_pages": pdf_data.get(
                    "total_pages",
                    len(pdf_data.get("pages", []))
                ),
                "scanned_pages": pdf_data.get(
                    "scanned_pages",
                    []
                ),
                "pages": pdf_data.get("pages", [])
            }

            documents.append(document)

        except Exception as error:

            print(
                f"Could not load {filename}: {error}"
            )

    print("PDF documents processed:", len(documents))

    return documents


def main():

    os.makedirs(
        OUTPUT_FOLDER,
        exist_ok=True
    )

    website_documents = process_website_pages()

    pdf_documents = process_pdf_documents()

    all_documents = (
        website_documents + pdf_documents
    )

    dataset = {
        "website": "https://www.gtbit.ac.in/",
        "total_documents": len(all_documents),
        "website_documents": len(website_documents),
        "pdf_documents": len(pdf_documents),
        "documents": all_documents
    }

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            dataset,
            file,
            ensure_ascii=False,
            indent=2
        )

    print("\n" + "=" * 55)
    print("DATASET PREPARATION COMPLETED")
    print("=" * 55)

    print("Website documents:", len(website_documents))
    print("PDF documents:", len(pdf_documents))
    print("Total documents:", len(all_documents))
    print("Output:", OUTPUT_FILE)


if __name__ == "__main__":
    main()