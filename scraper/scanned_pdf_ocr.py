import os
import time

import pymupdf
from dotenv import load_dotenv


OCR_PROMPT = """
Transcribe all readable information from this document page accurately.
Preserve headings, dates, tables and important details. Do not summarize or
invent content. Mark unreadable portions as [UNREADABLE]. Return only the
transcribed page text.
"""


def extract_scanned_pages(pdf_path, page_numbers):
    """OCR selected 1-based PDF pages with Gemini and return page text by number."""
    if not page_numbers:
        return {}

    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is required to OCR scanned PDFs.")

    from google import genai
    from google.genai import types

    client = genai.Client(api_key=api_key)
    model = os.getenv("GEMINI_OCR_MODEL", "gemini-3.8-flash")
    output = {}

    with pymupdf.open(pdf_path) as document:
        for page_number in page_numbers:
            if page_number < 1 or page_number > len(document):
                continue

            page = document[page_number - 1]
            pixmap = page.get_pixmap(
                matrix=pymupdf.Matrix(1.2, 1.2),
                alpha=False,
            )
            image_part = types.Part.from_bytes(
                data=pixmap.tobytes("jpeg", jpg_quality=85),
                mime_type="image/jpeg",
            )

            for attempt in range(3):
                try:
                    response = client.models.generate_content(
                        model=model,
                        contents=[OCR_PROMPT, image_part],
                    )
                    text = (response.text or "").strip()
                    if not text:
                        raise RuntimeError("Gemini returned empty OCR text.")
                    output[page_number] = text
                    break
                except Exception:
                    if attempt == 2:
                        raise
                    time.sleep(2 ** (attempt + 1))

    return output
