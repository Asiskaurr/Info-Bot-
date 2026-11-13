import os
import re
import time
import requests
import pymupdf as fitz
from scraper.pdf_downloader import download_pdf

from dotenv import load_dotenv
from google import genai
from google.genai import types


# Load environment variables
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("Gemini API key not found in .env")


client = genai.Client(
    api_key=api_key,
    http_options=types.HttpOptions(timeout=120000)
)


MODEL = "gemini-3.8-flash"

PDF_URL = (
    "https://www.gtbit.ac.in/assets/pdf/"
    "academic-calender-25-26.pdf"
)

OUTPUT_PATH = "data/cleaned/academic_calendar_25_26_ocr.txt"

def get_completed_pages():

    if not os.path.exists(OUTPUT_PATH):
        return set()

    with open(OUTPUT_PATH, "r", encoding="utf-8") as file:
        content = file.read()

    if not content.startswith(f"Source: {PDF_URL}"):
        return set()

    completed = re.findall(
        r"PAGE (\d+)",
        content
    )

    return {int(number) for number in completed}


def extract_with_gemini(pdf_bytes):

    document = fitz.open(
        stream=pdf_bytes,
        filetype="pdf"
    )

    os.makedirs("data/cleaned", exist_ok=True)

    completed_pages = get_completed_pages()

    # Create the output file only if it doesn't exist
    if not os.path.exists(OUTPUT_PATH):

        with open(OUTPUT_PATH, "w", encoding="utf-8") as file:
            file.write(f"Source: {PDF_URL}\n")

    print(f"Total pages: {len(document)}")
    print(f"Already completed pages: {sorted(completed_pages)}")

    prompt = """
    Extract all readable information from this document page.

    1. Transcribe all readable text accurately.
    2. Preserve headings, dates and important details.
    3. Preserve tables using readable rows and columns.
    4. Do not invent missing information.
    5. Mark unreadable portions as [UNREADABLE].
    6. Do not summarise or omit information.

    Return only the extracted content.
    """

    try:

        for page_number, page in enumerate(document, start=1):

            if page_number in completed_pages:

                print(f"\nPage {page_number} already saved. Skipping.")
                continue

            print(f"\nProcessing page {page_number}...")

            # Render at a slightly lower resolution
            pixmap = page.get_pixmap(
                matrix=fitz.Matrix(1.2, 1.2),
                alpha=False
            )

            # JPEG reduces image size
            image_bytes = pixmap.tobytes(
                "jpeg",
                jpg_quality=85
            )

            image_part = types.Part.from_bytes(
                data=image_bytes,
                mime_type="image/jpeg"
            )

            response = None

            for attempt in range(3):

                try:

                    print(
                        f"Sending page to Gemini "
                        f"(attempt {attempt + 1}/3)..."
                    )

                    response = client.models.generate_content(
                        model=MODEL,
                        contents=[prompt, image_part]
                    )

                    if not response.text:
                        raise RuntimeError(
                            "Gemini returned an empty response."
                        )

                    break

                except Exception as e:

                    error_message = str(e).lower()

                    temporary_error = any(
                        term in error_message
                        for term in [
                            "503",
                            "504",
                            "429",
                            "timeout",
                            "timed out",
                            "deadline_exceeded",
                            "unavailable"
                        ]
                    )

                    print(f"Gemini error: {e}")

                    if temporary_error and attempt < 2:

                        wait_time = 10 * (2 ** attempt)

                        print(
                            f"Temporary error. "
                            f"Retrying in {wait_time} seconds..."
                        )

                        time.sleep(wait_time)

                    else:
                        raise

            if response is None:
                raise RuntimeError(
                    f"Page {page_number} could not be processed."
                )

            page_text = response.text

            page_content = (
                f"\n{'=' * 60}\n"
                f"PAGE {page_number}\n"
                f"{'=' * 60}\n\n"
                f"{page_text}\n"
            )

            # Save immediately after successful extraction
            with open(
                OUTPUT_PATH,
                "a",
                encoding="utf-8"
            ) as file:

                file.write(page_content)
                file.flush()

            print(
                f"Page {page_number} extracted and saved!"
            )

    finally:
        document.close()


def main():

    print("Downloading GTBIT academic calendar...")

    pdf_path = download_pdf(PDF_URL)

    print(f"PDF available at: {pdf_path}")

    with open(pdf_path, "rb") as file:
        pdf_bytes = file.read()

    print("PDF loaded successfully.")

    extract_with_gemini(pdf_bytes)

    print("\nOCR processing completed!")
    print(f"Output file: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()