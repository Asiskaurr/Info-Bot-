from rag.embedding import (
    embedding_model,
    generate_embeddings,
    get_token_count
)

sample_text = "GTBIT academic calendar for the session 2025-26."

print("Model loaded successfully!")
print("Model:", embedding_model)
print("Maximum sequence length:", embedding_model.max_seq_length)
print(
    "Embedding dimensions:",
    embedding_model.get_sentence_embedding_dimension()
)

print("\nTesting token count...")
print("Token count:", get_token_count(sample_text))

print("\nTesting embedding generation...")
embeddings = generate_embeddings([sample_text])

print("Embedding shape:", embeddings.shape)
print("Embedding generated successfully!")
