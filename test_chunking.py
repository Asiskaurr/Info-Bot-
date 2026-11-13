import re
from pathlib import Path

from rag.chunking import chunk_pages
from rag.embedding import get_token_count


# Read the processed academic calendar
file_path = Path(
    "data/processed/academic_calendar_25_26_cleaned.txt"
)

content = file_path.read_text(encoding="utf-8")


# Extract the source URL
source_url = re.search(
    r"^Source:\s*(.+)$",
    content,
    re.MULTILINE
).group(1)


# Separate individual pages
parts = re.split(
    r"(?m)^PAGE (\d+)\s*$",
    content
)

pages = []

for index in range(1, len(parts), 2):

    page_number = int(parts[index])
    page_text = parts[index + 1]

    page_text = re.sub(
        r"(?m)^={5,}\s*$",
        "",
        page_text
    ).strip()

    pages.append({
        "page_number": page_number,
        "text": page_text
    })


# Document metadata
metadata = {
    "filename": "academic-calender-25-26.pdf",
    "source_url": source_url,
    "host_website": "GTBIT",
    "issuing_institution": "Guru Gobind Singh Indraprastha University",
    "document_type": "academic_calendar",
    "academic_session": "2025-26"
}


# Generate chunks
chunks = chunk_pages(
    pages,
    metadata,
    max_tokens=220
)


# Display results
print("Total pages:", len(pages))
print("Total chunks:", len(chunks))

for chunk in chunks:

    print("\n" + "=" * 60)
    print("Chunk ID:", chunk["chunk_id"])
    print("Page:", chunk["metadata"]["page_number"])
    print("Word count:", len(chunk["text"].split()))
    print("Token count:", get_token_count(chunk["text"]))
    print("Full text:\n", chunk["text"])