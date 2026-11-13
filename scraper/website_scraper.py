import json
import os
import time
import requests

from collections import deque
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, urldefrag


BASE_URL = "https://www.gtbit.ac.in/"

OUTPUT_DIR = "data/raw"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "gtbit_website_data.json")

MAX_PAGES = 300
REQUEST_DELAY = 1

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/142.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9"
}


def normalize_url(url):
    url, _ = urldefrag(url)

    parsed = urlparse(url)

    if parsed.scheme not in ("http", "https"):
        return None

    if parsed.netloc.lower() not in (
        "www.gtbit.ac.in",
        "gtbit.ac.in"
    ):
        return None

    return parsed._replace(
        scheme="https",
        netloc="www.gtbit.ac.in",
        query="",
        fragment=""
    ).geturl().rstrip("/")


def extract_page_data(soup, url):

    # Collect links BEFORE removing navigation elements
    links = [
        {
            "href": link["href"],
            "text": link.get_text(" ", strip=True)
        }
        for link in soup.find_all("a", href=True)
    ]

    # Extract page title
    title = (
        soup.title.get_text(" ", strip=True)
        if soup.title else ""
    )

    # Extract headings
    headings = [
        heading.get_text(" ", strip=True)
        for heading in soup.find_all(
            ["h1", "h2", "h3", "h4"]
        )
    ]

    # Remove unnecessary elements for text extraction
    for element in soup([
        "script",
        "style",
        "noscript",
        "nav",
        "footer"
    ]):
        element.decompose()

    # Extract page content
    content = soup.get_text(
        separator="\n",
        strip=True
    )

    content = "\n".join(
        line for line in content.splitlines()
        if line.strip()
    )

    return {
        "url": url,
        "title": title,
        "headings": headings,
        "content": content,
        "links": links
    }


def crawl_website():

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    session = requests.Session()
    session.headers.update(HEADERS)

    start_url = normalize_url(BASE_URL)

    visited = set()
    queued = {start_url}
    to_visit = deque([start_url])

    page_records = []
    pdf_records = {}

    print("Starting GTBIT website crawler...")
    print("Starting URL:", BASE_URL)

    while to_visit and len(visited) < MAX_PAGES:

        url = to_visit.popleft()

        if url in visited:
            continue

        visited.add(url)

        print(
            f"\nCrawling {len(visited)}/{MAX_PAGES}: {url}"
        )

        try:

            response = session.get(
                url,
                timeout=30
            )

            response.raise_for_status()

            content_type = response.headers.get(
                "Content-Type", ""
            ).lower()

            if "text/html" not in content_type:
                print("Skipping non-HTML page.")
                continue

            soup = BeautifulSoup(
                response.content,
                "lxml"
            )

            page_data = extract_page_data(
                soup,
                url
            )

            page_records.append(page_data)

            print(
                "Page saved:",
                page_data["title"] or url
            )

            # Process all links collected from this page
            for link in page_data["links"]:

                absolute_url = urljoin(
                    url,
                    link["href"]
                )

                parsed = urlparse(absolute_url)

                # Collect PDF links
                if parsed.path.lower().endswith(".pdf"):

                    pdf_url = normalize_url(absolute_url)

                    if pdf_url and pdf_url not in pdf_records:

                        pdf_records[pdf_url] = {
                            "url": pdf_url,
                            "source_page": url,
                            "link_text": link["text"]
                        }

                    continue

                # Add internal website pages to the queue
                normalized = normalize_url(
                    absolute_url
                )

                if (
                    normalized
                    and normalized not in visited
                    and normalized not in queued
                ):
                    queued.add(normalized)
                    to_visit.append(normalized)

            time.sleep(REQUEST_DELAY)

        except requests.RequestException as error:

            print("Request failed:", error)

    # Prepare final output
    output = {
        "website": BASE_URL,
        "total_pages": len(page_records),
        "total_pdfs": len(pdf_records),
        "pages": page_records,
        "pdfs": list(pdf_records.values())
    }

    # Save collected website data
    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            output,
            file,
            ensure_ascii=False,
            indent=2
        )

    print("\n" + "=" * 50)
    print("CRAWLING COMPLETED")
    print("=" * 50)

    print("Pages collected:", len(page_records))
    print("Unique PDFs found:", len(pdf_records))
    print("Output:", OUTPUT_FILE)


if __name__ == "__main__":
    crawl_website()