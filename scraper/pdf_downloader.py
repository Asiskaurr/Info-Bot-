import os
import requests
from urllib.parse import urlparse, unquote


def download_pdf(url, output_dir="data/raw"):

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 Chrome/142.0.0.0 Safari/537.36"
        )
    }

    os.makedirs(output_dir, exist_ok=True)

    # Extract filename from URL
    parsed_url = urlparse(url)
    filename = os.path.basename(unquote(parsed_url.path))

    if not filename.lower().endswith(".pdf"):
        raise ValueError("The provided URL does not point to a PDF.")

    file_path = os.path.join(output_dir, filename)

    # Avoid downloading an existing file again
    if os.path.exists(file_path):
        print(f"PDF already exists: {file_path}")
        return file_path

    print(f"Downloading: {filename}")

    response = requests.get(
        url,
        headers=headers,
        timeout=60
    )

    response.raise_for_status()

    # Verify that the response is actually a PDF
    if not response.content.startswith(b"%PDF"):
        raise ValueError("Downloaded content is not a valid PDF.")

    with open(file_path, "wb") as file:
        file.write(response.content)

    print(f"PDF saved successfully: {file_path}")

    return file_path