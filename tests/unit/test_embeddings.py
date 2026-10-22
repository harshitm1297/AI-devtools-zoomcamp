from backend.app.embeddings import cosine_similarity, hash_embedding, purchase_text


def test_hash_embedding_is_deterministic_and_normalized() -> None:
    first = hash_embedding("Northstar Market groceries EUR")
    second = hash_embedding("Northstar Market groceries EUR")
    assert first == second
    assert round(cosine_similarity(first, first), 6) == 1.0


def test_similar_purchase_text_scores_higher() -> None:
    query = hash_embedding(purchase_text("Northstar Market", "groceries", "EUR"))
    similar = hash_embedding(purchase_text("Green Market", "groceries", "EUR"))
    different = hash_embedding(purchase_text("Cinema Square", "entertainment", "EUR"))
    assert cosine_similarity(query, similar) > cosine_similarity(query, different)

