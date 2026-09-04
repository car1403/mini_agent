def search(query: str, limit: int = 3) -> list[dict]:
    from app.repositories.store import store

    return store.search_documents(query, limit)
