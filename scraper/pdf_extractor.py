import os

import pdfplumber


def extract_pdf_text(pdf_path):
    """Extract page-level text with pdfplumber and flag likely scanned pages."""
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    extracted_pages = []
    scanned_pages = []

    with pdfplumber.open(pdf_path) as document:
        total_pages = len(document.pages)
        print(f"Processing: {os.path.basename(pdf_path)}")
        print(f"Total pages: {total_pages}")

        for page_number, page in enumerate(document.pages, start=1):
            text = (page.extract_text() or "").strip()
            if len(text) < 30:
                scanned_pages.append(page_number)

            extracted_pages.append({
                "page_number": page_number,
                "text": text,
            })
            print(f"Page {page_number}: {len(text)} characters extracted")

    metadata = {
        "filename": os.path.basename(pdf_path),
        "total_pages": total_pages,
        "scanned_pages": scanned_pages,
    }
    return extracted_pages, metadata
