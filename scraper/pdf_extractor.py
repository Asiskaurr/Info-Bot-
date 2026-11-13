import os
import pymupdf


def extract_pdf_text(pdf_path):

    if not os.path.exists(pdf_path):
        raise FileNotFoundError(
            f"PDF not found: {pdf_path}"
        )

    document = pymupdf.open(pdf_path)

    extracted_pages = []
    scanned_pages = []

    print(f"Processing: {os.path.basename(pdf_path)}")
    print(f"Total pages: {len(document)}")

    for page_number, page in enumerate(document, start=1):

        text = page.get_text("text").strip()

        if len(text) < 30:
            scanned_pages.append(page_number)

        extracted_pages.append({
            "page_number": page_number,
            "text": text
        })

        print(
            f"Page {page_number}: "
            f"{len(text)} characters extracted"
        )

    metadata = {
        "filename": os.path.basename(pdf_path),
        "total_pages": len(document),
        "scanned_pages": scanned_pages
    }

    document.close()

    return extracted_pages, metadata