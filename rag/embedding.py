from sentence_transformers import SentenceTransformer


MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


# Load the embedding model
embedding_model = SentenceTransformer(MODEL_NAME)


def generate_embeddings(texts):

    if not texts:
        return []

    embeddings = embedding_model.encode(
        texts,
        convert_to_numpy=True,
        normalize_embeddings=True
    )

    return embeddings


def get_token_count(text):

    tokens = embedding_model.tokenizer(
        text,
        truncation=False,
        verbose=False
    )

    return len(tokens["input_ids"])