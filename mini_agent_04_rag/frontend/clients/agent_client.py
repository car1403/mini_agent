from typing import Any

from core.api_client import request, request_bytes, upload


def get_health():
    return request("GET", "/health")


def get_providers():
    return request("GET", "/api/providers")


def compare_concepts(message: str):
    payload = {"message": message}
    return request("POST", "/api/concepts/compare", json=payload)


def classify_travel(message: str):
    payload = {"message": message}
    return request("POST", "/api/travel/classify", json=payload)


def generate_response(provider: str, system_prompt: str, message: str):
    payload = {
        "provider": provider,
        "system_prompt": system_prompt,
        "message": message,
    }
    return request("POST", "/api/generate", json=payload)


def compare_providers(providers: list[str], message: str):
    payload = {"providers": providers, "message": message}
    return request("POST", "/api/providers/compare", json=payload)


def preview_prompt(role: str, instruction: str, context: str, constraint: str):
    payload = {
        "role": role,
        "instruction": instruction,
        "context": context,
        "constraint": constraint,
    }
    return request("POST", "/api/prompts/preview", json=payload)


def validate_travel_plan(payload: dict[str, Any]):
    return request("POST", "/api/structured/validate", json={"payload": payload})


def compare_structured_outputs(providers: list[str], message: str):
    payload = {"providers": providers, "message": message}
    return request("POST", "/api/structured/compare", json=payload)


def get_tools():
    return request("GET", "/api/tools")


def select_tool(provider: str, message: str):
    payload = {"provider": provider, "message": message}
    return request("POST", "/api/tools/select", json=payload)


def compare_tools(providers: list[str], message: str):
    payload = {"providers": providers, "message": message}
    return request("POST", "/api/tools/compare", json=payload)


def run_tool(tool_name: str, arguments: dict[str, Any]):
    payload = {"tool_name": tool_name, "arguments": arguments}
    return request("POST", "/api/tools/run", json=payload)


def complete_tool_loop(provider: str, message: str):
    payload = {"provider": provider, "message": message}
    return request("POST", "/api/tools/complete", json=payload)


def get_rag_documents():
    return request("GET", "/api/rag/documents")


def preview_chunks(
    text: str,
    source: str,
    title: str,
    sentences_per_chunk: int,
):
    payload = {
        "text": text,
        "source": source,
        "title": title,
        "sentences_per_chunk": sentences_per_chunk,
    }
    return request("POST", "/api/rag/chunks", json=payload)


def search_rag(query: str, mode: str, top_k: int):
    payload = {"query": query, "mode": mode, "top_k": top_k}
    return request("POST", "/api/rag/search", json=payload)


def answer_with_rag(query: str, mode: str, top_k: int, provider: str):
    payload = {
        "query": query,
        "mode": mode,
        "top_k": top_k,
        "provider": provider,
    }
    return request("POST", "/api/rag/answer", json=payload)


def index_rag_documents(reset_collection: bool = True):
    return request(
        "POST",
        "/api/rag/index",
        json={"reset_collection": reset_collection},
    )


def get_rag_status():
    return request("GET", "/api/rag/status")


def upload_image(filename: str, content: bytes, content_type: str, question: str):
    files = {"image": (filename, content, content_type)}
    data = {"question": question}
    return upload("/api/media/image-analysis", files, data)


def create_tts(text: str, voice: str, instructions: str) -> bytes:
    payload = {"text": text, "voice": voice, "instructions": instructions}
    return request_bytes("/api/media/tts", payload)
