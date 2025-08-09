import os
from app.services.vector_store import get_vector_store

def test_vector_store_insert_and_query(tmp_path):
    db_path = tmp_path / "test_db"
    store = get_vector_store(str(db_path))

    # Insert a doc
    store.add_texts(["This is a test document"])
    results = store.similarity_search("test", k=1)

    assert len(results) == 1
    assert "test document" in results[0].page_content
