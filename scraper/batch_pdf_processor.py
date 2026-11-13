import os
import json
from dotenv import load_dotenv

from scraper.pdf_extractor import extract_pdf_text
from rag.data_cleaning import clean_pages


load_dotenv()
INPUT_FILE = "data/raw/pdf_download_results.json"
OUTPUT_DIR = "data/cleaned/pdf_text"
REPORT_FILE = "data/cleaned/pdf_processing_report.json"
ENABLE_SCANNED_PDF_OCR = os.getenv(
    "ENABLE_SCANNED_PDF_OCR", "false"
).lower() in {"1", "true", "yes", "on"}


def main():

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    with open(INPUT_FILE, "r", encoding="utf-8") as file:
        manifest = json.load(file)

    pdf_records = manifest.get("results", [])

    downloaded = [
        pdf for pdf in pdf_records
        if pdf.get("status") in ("downloaded", "skipped")
    ]

    print("=" * 55)
    print("GTBIT BULK PDF PROCESSOR")
    print("=" * 55)
    print("PDFs to process:", len(downloaded))

    successful = 0
    failed = 0
    scanned_documents = 0
    total_pages = 0

    results = []

    for index, pdf in enumerate(downloaded, start=1):

        filename = pdf.get("filename", "")

        pdf_path = pdf.get(
            "local_path",
            os.path.join("data/raw/pdfs", filename)
        )

        print(f"\n[{index}/{len(downloaded)}] Processing: {filename}")

        try:

            if not os.path.exists(pdf_path):
                raise FileNotFoundError(pdf_path)

            # Extract text page by page. OCR is an explicit opt-in because it
            # sends scanned page images to the configured Gemini API.
            pages, metadata = extract_pdf_text(pdf_path)
            scanned_pages = metadata.get("scanned_pages", [])
            ocr_pages = []

            if scanned_pages and ENABLE_SCANNED_PDF_OCR:
                try:
                    from scraper.scanned_pdf_ocr import extract_scanned_pages

                    ocr_text = extract_scanned_pages(pdf_path, scanned_pages)
                    for page in pages:
                        replacement = ocr_text.get(page["page_number"])
                        if replacement:
                            page["text"] = replacement
                            ocr_pages.append(page["page_number"])
                except Exception as error:
                    print(f"OCR could not complete for {filename}: {error}")

            # Clean extracted and OCR text before dataset preparation.
            cleaned_pages = clean_pages(pages)

            if scanned_pages:
                scanned_documents += 1

            total_pages += metadata.get("total_pages", len(pages))

            # Prepare document metadata
            document = {
                "filename": filename,
                "source_url": pdf.get("url", ""),
                "source_page": pdf.get("source_page", ""),
                "link_text": pdf.get("link_text", ""),
                "total_pages": metadata.get("total_pages", len(pages)),
                "scanned_pages": scanned_pages,
                "ocr_pages": ocr_pages,
                "pages": cleaned_pages
            }

            # Save extracted and cleaned document
            output_filename = os.path.splitext(filename)[0] + ".json"

            output_path = os.path.join(
                OUTPUT_DIR,
                output_filename
            )

            with open(
                output_path,
                "w",
                encoding="utf-8"
            ) as file:

                json.dump(
                    document,
                    file,
                    ensure_ascii=False,
                    indent=2
                )

            successful += 1

            print(
                f"Success | Pages: {len(cleaned_pages)} "
                f"| Scanned: {len(scanned_pages)}"
            )

            results.append({
                "filename": filename,
                "status": "processed",
                "output_path": output_path,
                "total_pages": document["total_pages"],
                "scanned_pages": scanned_pages
            })

        except Exception as error:

            failed += 1

            print("Processing failed:", error)

            results.append({
                "filename": filename,
                "status": "failed",
                "error": str(error)
            })

    # Save processing report
    report = {
        "total_pdfs": len(downloaded),
        "successful": successful,
        "failed": failed,
        "scanned_documents": scanned_documents,
        "total_pages": total_pages,
        "results": results
    }

    with open(
        REPORT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            report,
            file,
            ensure_ascii=False,
            indent=2
        )

    print("\n" + "=" * 55)
    print("PROCESSING COMPLETED")
    print("=" * 55)
    print("Total PDFs:", len(downloaded))
    print("Successfully processed:", successful)
    print("Failed:", failed)
    print("Documents containing scanned pages:", scanned_documents)
    print("Total pages:", total_pages)
    print("Output folder:", OUTPUT_DIR)
    print("Report:", REPORT_FILE)


if __name__ == "__main__":
    main()
