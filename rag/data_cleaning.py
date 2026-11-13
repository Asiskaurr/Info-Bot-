import re
import unicodedata


def clean_text(text):

    if not text:
        return ""

    # Normalize Unicode characters
    text = unicodedata.normalize("NFKC", text)

    # Normalize line endings
    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    # Repair incorrectly decoded text, line by line
    text = "\n".join(
    repair_mojibake(line)
    for line in text.split("\n")
)

    # Remove null bytes and unwanted control characters
    text = "".join(
        char for char in text
        if char in "\n\t" or unicodedata.category(char)[0] != "C"
    )

    # Remove unnecessary spaces and tabs
    text = re.sub(r"[ \t]+", " ", text)

    # Remove spaces at the beginning and end of lines
    lines = [
        line.strip()
        for line in text.split("\n")
    ]

    text = "\n".join(lines)

    # Replace excessive consecutive blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()

def repair_mojibake(text):

    if not text:
        return text

    # Common signs of incorrectly decoded UTF-8
    error_markers = [
    "â€“",
    "â€™",
    "â€œ",
    "Ã",
    "Â",
    "à¤"
    ]

    original_errors = sum(
        text.count(marker)
        for marker in error_markers
    )

    if original_errors == 0:
        return text

    try:
        repaired = text.encode("cp1252").decode("utf-8")

        repaired_errors = sum(
            repaired.count(marker)
            for marker in error_markers
        )

        # Accept the repair only if suspicious patterns decrease
        if repaired_errors < original_errors:
            return repaired

    except (UnicodeEncodeError, UnicodeDecodeError):
        pass

    return text

def clean_pages(pages):

    cleaned_pages = []

    for page in pages:

        cleaned_pages.append({
            "page_number": page["page_number"],
            "text": clean_text(page["text"])
        })

    return cleaned_pages