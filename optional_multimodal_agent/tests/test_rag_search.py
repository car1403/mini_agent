import json
from shared.config import ROOT
from scripts.ingest_knowledge import chunks, discover_documents
from mcp_server.database import knowledge_queries

def test_documents_and_samples_match():
    documents = discover_documents()
    assert len(documents)==13
    for path, target_type, target_id in documents:
        text = path.read_text(encoding="utf-8")
        assert target_id in text
        assert target_type in {"product","program","facility"}
        assert all(len(content)<=1000 for _,content in chunks(text))
    scenario_file = json.loads((ROOT/"data/samples/scenarios.json").read_text(encoding="utf-8"))
    assert scenario_file["_comment"]
    assert scenario_file["_field_guide"]["checks"]
    for scenario in scenario_file["scenarios"]:
        assert (ROOT/"data/samples"/scenario["image"]).is_file()

def test_query_scopes_target_and_embedding_model(monkeypatch):
    observed = {}
    def query(sql,params):
        observed.update(sql=sql,params=params)
        return []
    monkeypatch.setattr(knowledge_queries,"query",query)
    knowledge_queries.search("[0]","program","PG-YOGA","model")
    assert "program_documents" in observed["sql"]
    assert "facility_documents" in observed["sql"]
    assert "embedding_model=%s" in observed["sql"]
    assert "embedding_dimensions=768" in observed["sql"]
    assert "PG-YOGA" not in observed["sql"]
    assert "PG-YOGA" in observed["params"]

def test_embeddinggemma_batch_request(monkeypatch):
    from mcp_server.rag import embeddings

    observed = {}

    class Response:
        def raise_for_status(self):
            return None
        def json(self):
            return {"embeddings": [[0.0] * 768, [1.0] * 768]}

    class Client:
        async def __aenter__(self):
            return self
        async def __aexit__(self, *args):
            return None
        async def post(self, url, json):
            observed.update(url=url, json=json)
            return Response()

    monkeypatch.setattr(embeddings.httpx, "AsyncClient", lambda **kwargs: Client())
    import asyncio
    result = asyncio.run(embeddings.embed(["문서", "질문"]))
    assert len(result) == 2
    assert observed["url"].endswith("/api/embed")
    assert observed["json"] == {"model": "embeddinggemma", "input": ["문서", "질문"]}
