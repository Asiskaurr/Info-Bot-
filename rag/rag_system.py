import os
import time

import chromadb
from dotenv import load_dotenv
from google import genai

from rag.embedding import generate_embeddings


# Configuration
DB_PATH = "data/chroma_db"
COLLECTION_NAME = "gtbit_knowledge"

GEMINI_MODEL = "gemini-3.5-flash"

TOP_K = 5
MAX_RETRIES = 3


# Load environment variables
load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("GEMINI_API_KEY not found in .env file.")

gemini_client = genai.Client(api_key=API_KEY)


# Connect to existing vector database
chroma_client = chromadb.PersistentClient(path=DB_PATH)

collection = chroma_client.get_collection(
    name=COLLECTION_NAME
)


def retrieve_documents(question, top_k=TOP_K):

    query_embedding = generate_embeddings([question])

    results = collection.query(
        query_embeddings=query_embedding.tolist(),
        n_results=top_k,
        include=[
            "documents",
            "metadatas",
            "distances"
        ]
    )

    retrieved = []

    for index in range(len(results["documents"][0])):

        retrieved.append({
            "text": results["documents"][0][index],
            "metadata": results["metadatas"][0][index],
            "distance": results["distances"][0][index]
        })

    return retrieved


def generate_answer(question, retrieved_documents):

    if not retrieved_documents:
        return (
            "I couldn't find relevant information about this "
            "in the available GTBIT resources."
        )

    context = ""
    sources = []

    for index, document in enumerate(retrieved_documents, start=1):

        metadata = document["metadata"]

        title = metadata.get("title", "Unknown")
        source_type = metadata.get("source_type", "Unknown")
        source_url = metadata.get("source_url", "")
        page_number = metadata.get("page_number", "")

        context += f"""
[Source {index}]
Title: {title}
Type: {source_type}
URL: {source_url}
Page: {page_number}

Content:
{document["text"]}

"""

        sources.append({
            "source_number": index,
            "title": title,
            "source_type": source_type,
            "source_url": source_url,
            "page_number": page_number,
            "distance": document["distance"]
        })

    prompt = f"""
You are an intelligent information assistant for
Guru Tegh Bahadur Institute of Technology (GTBIT).

Answer the user's question using ONLY the information
provided in the context below.

INSTRUCTIONS:

1. Give accurate, clear and helpful answers.
2. Do not invent information.
3. If the context does not contain the answer, clearly
   say that the information could not be found.
4. Maintain the language used by the user.
5. Support factual claims with source references
   such as [Source 1] or [Source 2].
6. Use bullet points when they improve readability.
7. If multiple sources contain relevant information,
   combine them without repeating content.

CONTEXT:

{context}

USER QUESTION:

{question}

ANSWER:
"""

    for attempt in range(MAX_RETRIES):

        try:

            response = gemini_client.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt
            )

            return response.text, sources

        except Exception as error:

            print(
                f"Gemini attempt {attempt + 1} failed: {error}"
            )

            if attempt < MAX_RETRIES - 1:
                time.sleep(2 ** (attempt + 1))

    raise RuntimeError(
        "Unable to generate an answer after multiple attempts."
    )


def answer_question(question):

    if not question or not question.strip():
        raise ValueError("Question cannot be empty.")

    print("\nRetrieving relevant information...")

    retrieved_documents = retrieve_documents(question)

    print(
        f"Retrieved {len(retrieved_documents)} relevant chunks."
    )

    answer, sources = generate_answer(
        question,
        retrieved_documents
    )

    return {
        "question": question,
        "answer": answer,
        "sources": sources
    }


if __name__ == "__main__":

    print("=" * 55)
    print("GTBIT INFORMATION CHATBOT")
    print("=" * 55)

    print("Type 'exit' to quit.")

    while True:

        question = input("\nAsk your question: ").strip()

        if question.lower() in ["exit", "quit"]:
            print("Goodbye!")
            break

        if not question:
            continue

        try:

            result = answer_question(question)

            print("\n" + "=" * 55)
            print("ANSWER")
            print("=" * 55)

            print(result["answer"])

            print("\n" + "=" * 55)
            print("SOURCES")
            print("=" * 55)

            for source in result["sources"]:

                print(f"\n[Source {source['source_number']}]")
                print("Title:", source["title"])
                print("Type:", source["source_type"])
                print("URL:", source["source_url"])
                print("Page:", source["page_number"])

        except Exception as error:

            print("\nError:", error)