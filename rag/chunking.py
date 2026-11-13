from rag.embedding import get_token_count


def split_into_blocks(text):
    """
    Split text into logical blocks.
    Preserve table rows and repeat table headers for retrieval.
    """

    lines = text.splitlines()

    blocks = []
    current_block = []
    index = 0

    while index < len(lines):

        line = lines[index]

        if line.strip().startswith("|"):

            if current_block:
                blocks.append("\n".join(current_block).strip())
                current_block = []

            table_lines = []

            while (
                index < len(lines)
                and lines[index].strip().startswith("|")
            ):
                table_lines.append(lines[index])
                index += 1

            if len(table_lines) >= 2:

                header = "\n".join(table_lines[:2])

                for row in table_lines[2:]:

                    blocks.append(
                        header + "\n" + row
                    )

            else:
                blocks.append("\n".join(table_lines))

            continue

        if line.strip():
            current_block.append(line)

        elif current_block:
            blocks.append("\n".join(current_block).strip())
            current_block = []

        index += 1

    if current_block:
        blocks.append("\n".join(current_block).strip())

    return blocks


def split_long_block(text, max_tokens):
    """
    Split an oversized block into token-safe pieces.
    """

    words = text.split()

    pieces = []
    start = 0

    while start < len(words):

        end = start
        current_text = ""

        while end < len(words):

            candidate = " ".join(words[start:end + 1])

            if get_token_count(candidate) > max_tokens:
                break

            current_text = candidate
            end += 1

        if not current_text:
            raise ValueError(
                "A word exceeds the maximum token limit."
            )

        pieces.append(current_text)
        start = end

    return pieces


def chunk_pages(pages, document_metadata, max_tokens=220):

    if max_tokens <= 0 or max_tokens > 256:
        raise ValueError(
            "max_tokens must be between 1 and 256."
        )

    chunks = []

    for page in pages:

        page_number = page["page_number"]
        text = page["text"]

        if not text.strip():
            continue

        blocks = split_into_blocks(text)

        current_parts = []

        for block in blocks:

            candidate = "\n\n".join(
                current_parts + [block]
            )

            if get_token_count(candidate) <= max_tokens:

                current_parts.append(block)
                continue

            if current_parts:

                chunk_text = "\n\n".join(current_parts)

                chunks.append({
                    "chunk_id": (
                        f"{document_metadata['filename']}"
                        f"_page_{page_number}_chunk_{len(chunks) + 1}"
                    ),
                    "text": chunk_text,
                    "metadata": {
                        **document_metadata,
                        "page_number": page_number
                    }
                })

                current_parts = []

            if get_token_count(block) <= max_tokens:

                current_parts.append(block)

            else:

                pieces = split_long_block(block, max_tokens)

                for piece in pieces[:-1]:

                    chunks.append({
                        "chunk_id": (
                            f"{document_metadata['filename']}"
                            f"_page_{page_number}_chunk_{len(chunks) + 1}"
                        ),
                        "text": piece,
                        "metadata": {
                            **document_metadata,
                            "page_number": page_number
                        }
                    })

                current_parts.append(pieces[-1])

        if current_parts:

            chunk_text = "\n\n".join(current_parts)

            chunks.append({
                "chunk_id": (
                    f"{document_metadata['filename']}"
                    f"_page_{page_number}_chunk_{len(chunks) + 1}"
                ),
                "text": chunk_text,
                "metadata": {
                    **document_metadata,
                    "page_number": page_number
                }
            })

    return chunks