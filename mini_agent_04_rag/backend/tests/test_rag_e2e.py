"""실제 Ollama·pgvector·Redis가 준비된 환경에서만 실행하는 RAG E2E Test입니다."""

import io
import os
import uuid

import pytest
from fastapi.testclient import TestClient
from pypdf import PdfWriter
from pypdf.generic import DictionaryObject, NameObject, StreamObject


if os.getenv("RUN_RAG_E2E") != "1":
    pytest.skip("RUN_RAG_E2E=1일 때만 실제 RAG 인프라 Test를 실행합니다.", allow_module_level=True)

from app.main import app  # noqa: E402


client = TestClient(app)


def _assert_ok(response):
    assert response.status_code == 200, response.text
    return response.json()


def _text_pdf(text: str) -> bytes:
    writer = PdfWriter()
    page = writer.add_blank_page(width=612, height=792)
    font = DictionaryObject({
        NameObject("/Type"): NameObject("/Font"),
        NameObject("/Subtype"): NameObject("/Type1"),
        NameObject("/BaseFont"): NameObject("/Helvetica"),
    })
    page[NameObject("/Resources")] = DictionaryObject({
        NameObject("/Font"): DictionaryObject({NameObject("/F1"): font}),
    })
    stream = StreamObject()
    safe_text = text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
    stream.set_data(f"BT /F1 12 Tf 72 720 Td ({safe_text}) Tj ET".encode("ascii"))
    page[NameObject("/Contents")] = writer._add_object(stream)
    output = io.BytesIO()
    writer.write(output)
    return output.getvalue()


def test_labs_01_to_07_with_real_infrastructure():
    status = _assert_ok(client.get("/api/rag/status"))
    assert status["ollama"]["ok"] is True
    assert status["postgres"]["ok"] is True
    assert status["redis"]["ok"] is True

    run_id = uuid.uuid4().hex
    source = "e2e-policy.md"
    first = _assert_ok(client.post("/api/rag/texts", json={
        "title": "E2E 고객 정책",
        "content": "E2E 정책의 당일 취소 수수료는 전액입니다.",
        "source": source,
        "metadata": {"dataset": "e2e", "run_id": run_id, "version": 1},
        "sentences_per_chunk": 1,
        "replace_source": True,
    }))
    assert first["indexed_count"] == 1

    answer_request = {
        "query": "E2E 정책 당일 취소 수수료는?",
        "mode": "pgvector",
        "top_k": 3,
        "provider": "mock",
        "use_cache": True,
        "metadata_filter": {"dataset": "e2e", "run_id": run_id},
    }
    first_answer = _assert_ok(client.post("/api/rag/answer", json=answer_request))
    second_answer = _assert_ok(client.post("/api/rag/answer", json=answer_request))
    assert first_answer["cache_hit"] is False
    assert second_answer["cache_hit"] is True
    assert source in second_answer["sources"]

    _assert_ok(client.post("/api/rag/texts", json={
        "title": "E2E 고객 정책",
        "content": "E2E 정책의 당일 취소 수수료는 오십 퍼센트입니다.",
        "source": source,
        "metadata": {"dataset": "e2e", "run_id": run_id, "version": 2},
        "sentences_per_chunk": 1,
        "replace_source": True,
    }))
    indexed = _assert_ok(client.get("/api/rag/indexed", params={"source": source}))
    assert indexed["count"] == 1
    assert indexed["chunks"][0]["metadata"]["version"] == 2
    replaced_answer = _assert_ok(client.post("/api/rag/answer", json=answer_request))
    assert replaced_answer["cache_hit"] is False

    _assert_ok(client.post("/api/rag/labs/products/seed"))
    products = _assert_ok(client.post("/api/rag/labs/products/search", json={
        "query": "달리기 신발", "category": "shoes", "max_price": 90000, "top_k": 3,
    }))
    assert products["results"]
    assert all(item["metadata"]["category"] == "shoes" for item in products["results"])
    assert all(item["metadata"]["price"] <= 90000 for item in products["results"])

    _assert_ok(client.post("/api/rag/labs/policies/seed"))
    employee = _assert_ok(client.post(
        "/api/rag/labs/policies/search",
        headers={"X-Demo-Role": "employee"},
        json={"query": "급여 정정 승인", "top_k": 3},
    ))
    hr = _assert_ok(client.post(
        "/api/rag/labs/policies/search",
        headers={"X-Demo-Role": "hr"},
        json={"query": "급여 정정 승인", "top_k": 3},
    ))
    assert all("employee" in item["metadata"]["allowed_roles"] for item in employee["results"])
    assert any(item["title"] == "급여 운영" for item in hr["results"])

    pdf_name = "e2e-guide.pdf"
    pdf_bytes = _text_pdf("E2E travel museum closes every Tuesday.")
    for _ in range(2):
        pdf_result = _assert_ok(client.post(
            "/api/rag/pdf",
            files={"pdf": (pdf_name, pdf_bytes, "application/pdf")},
            data={"title": "E2E Travel Guide", "replace_source": "true"},
        ))
    pdf_source = pdf_result["source"]
    assert pdf_source.startswith(f"{pdf_name}:")
    pdf_indexed = _assert_ok(client.get("/api/rag/indexed", params={"source": pdf_source}))
    assert pdf_indexed["count"] == 1
    assert pdf_indexed["chunks"][0]["metadata"]["page_number"] == 1
    assert pdf_indexed["chunks"][0]["metadata"]["source_id"] == pdf_source

    _assert_ok(client.post("/api/rag/labs/evaluation/seed"))
    evaluation = _assert_ok(client.post("/api/rag/labs/evaluation/run", json={"top_k": 3}))
    assert {report["mode"] for report in evaluation["reports"]} == {"keyword", "pgvector", "hybrid"}
    assert all(0 <= report["hit_at_k"] <= 1 for report in evaluation["reports"])
    assert all(0 <= report["mrr"] <= 1 for report in evaluation["reports"])

    _assert_ok(client.post("/api/rag/labs/multi-agent/seed"))
    session_id = f"e2e-{uuid.uuid4().hex}"
    _assert_ok(client.delete("/api/rag/labs/multi-agent/state", params={"session_id": session_id}))
    clarification = _assert_ok(client.post("/api/rag/labs/multi-agent/run", json={
        "session_id": session_id, "message": "정보를 알려 주세요", "provider": "mock",
    }))
    assert clarification["status"] == "needs_clarification"
    completed = _assert_ok(client.post("/api/rag/labs/multi-agent/run", json={
        "session_id": session_id, "message": "호텔 취소 규정", "provider": "mock",
    }))
    assert completed["status"] == "completed"
    assert completed["topics"] == ["hotel"]
    assert completed["tool_calls"][0]["name"] == "search_hotel_knowledge"
    assert completed["termination_reason"] == "grounded_answer"
