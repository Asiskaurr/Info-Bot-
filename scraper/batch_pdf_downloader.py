import os
import json
import time
import hashlib
import requests

from urllib.parse import urlparse, unquote


INPUT_FILE = "data/raw/gtbit_website_data.json"
OUTPUT_DIR = "data/raw/pdfs"
MANIFEST_FILE = "data/raw/pdf_download_results.json"

REQUEST_DELAY = 1
MAX_RETRIES = 3

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/142.0.0.0 Safari/537.36"
    )
}


def get_filename(url, used_filenames):
    """Generate a safe, unique filename from a PDF URL."""

    path = unquote(urlparse(url).path)
    filename = os.path.basename(path)

    if not filename.lower().endswith(".pdf"):
        return None

    if filename not in used_filenames:
        used_filenames.add(filename)
        return filename

    # Avoid overwriting files with the same name
    url_hash = hashlib.md5(
        url.encode("utf-8")
    ).hexdigest()[:8]

    name, extension = os.path.splitext(filename)
    unique_filename = f"{name}_{url_hash}{extension}"

    used_filenames.add(unique_filename)

    return unique_filename


def is_valid_pdf(file_path):
    """Check whether an existing file is a valid PDF."""

    try:
        with open(file_path, "rb") as file:
            return file.read(5) == b"%PDF-"
    except OSError:
        return False


def download_pdf(session, url, file_path):
    """Download one PDF with retries."""

    for attempt in range(1, MAX_RETRIES + 1):

        temp_path = file_path + ".part"

        try:

            with session.get(
                url,
                stream=True,
                timeout=(15, 90)
            ) as response:

                response.raise_for_status()

                content_type = response.headers.get(
                    "Content-Type", ""
                ).lower()

                if (
                    "text/html" in content_type
                    or "application/json" in content_type
                ):
                    raise ValueError(
                        f"URL returned non-PDF content: {content_type}"
                    )

                first_chunk = b""

                with open(temp_path, "wb") as file:

                    for chunk in response.iter_content(
                        chunk_size=1024 * 64
                    ):

                        if not chunk:
                            continue

                        if not first_chunk:
                            first_chunk = chunk

                            if not first_chunk.startswith(b"%PDF-"):
                                raise ValueError(
                                    "Downloaded file is not a valid PDF."
                                )

                        file.write(chunk)

            if not is_valid_pdf(temp_path):
                raise ValueError("PDF validation failed.")

            os.replace(temp_path, file_path)

            return True, "Downloaded successfully"

        except Exception as error:

            if os.path.exists(temp_path):
                os.remove(temp_path)

            if attempt == MAX_RETRIES:
                return False, str(error)

            print(
                f"Retry {attempt}/{MAX_RETRIES} failed: {error}"
            )

            time.sleep(attempt * 3)

    return False, "Download failed"


def main():

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    if not os.path.exists(INPUT_FILE):
        print("Website data JSON not found:", INPUT_FILE)
        return

    with open(
        INPUT_FILE,
        "r",
        encoding="utf-8"
    ) as file:
        website_data = json.load(file)

    pdf_records = website_data.get("pdfs", [])

    # Remove duplicate URLs
    unique_pdfs = {}

    for pdf in pdf_records:

        url = pdf.get("url")

        if url:
            unique_pdfs[url] = pdf

    pdf_records = list(unique_pdfs.values())

    print("=" * 55)
    print("GTBIT BULK PDF DOWNLOADER")
    print("=" * 55)
    print("PDF links found:", len(pdf_records))
    print("Download folder:", OUTPUT_DIR)

    session = requests.Session()
    session.headers.update(HEADERS)

    used_filenames = set()

    results = []

    downloaded = 0
    skipped = 0
    failed = 0

    for index, pdf in enumerate(pdf_records, start=1):

        url = pdf["url"]

        filename = get_filename(
            url,
            used_filenames
        )

        if not filename:
            failed += 1
            results.append({
                **pdf,
                "status": "failed",
                "error": "Invalid PDF filename"
            })
            continue

        file_path = os.path.join(
            OUTPUT_DIR,
            filename
        )

        print(
            f"\n[{index}/{len(pdf_records)}] {filename}"
        )

        # Skip files that are already downloaded and valid
        if os.path.exists(file_path):

            if is_valid_pdf(file_path):

                print("Already downloaded. Skipping.")

                skipped += 1

                results.append({
                    **pdf,
                    "filename": filename,
                    "local_path": file_path,
                    "status": "skipped"
                })

                continue

            else:
                os.remove(file_path)

        success, message = download_pdf(
            session,
            url,
            file_path
        )

        if success:

            print("Success:", message)
            downloaded += 1

            results.append({
                **pdf,
                "filename": filename,
                "local_path": file_path,
                "status": "downloaded"
            })

        else:

            print("Failed:", message)
            failed += 1

            results.append({
                **pdf,
                "filename": filename,
                "status": "failed",
                "error": message
            })

        time.sleep(REQUEST_DELAY)

    # Save download results
    manifest = {
        "total_pdf_links": len(pdf_records),
        "downloaded": downloaded,
        "skipped": skipped,
        "failed": failed,
        "results": results
    }

    with open(
        MANIFEST_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            manifest,
            file,
            ensure_ascii=False,
            indent=2
        )

    session.close()

    print("\n" + "=" * 55)
    print("DOWNLOAD COMPLETED")
    print("=" * 55)
    print("Total PDF links:", len(pdf_records))
    print("Downloaded:", downloaded)
    print("Skipped:", skipped)
    print("Failed:", failed)
    print("PDF folder:", OUTPUT_DIR)
    print("Results saved:", MANIFEST_FILE)


if __name__ == "__main__":
    main()