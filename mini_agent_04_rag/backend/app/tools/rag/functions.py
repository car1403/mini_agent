"""검증된 검색 인자를 RAG Service에 전달하는 읽기 전용 Tool입니다."""

from app.rag.service import search
from app.schemas import SearchKnowledgeArgs, TopicSearchArgs


def search_knowledge_base(arguments: SearchKnowledgeArgs) -> dict:
    results = search(
        arguments.query,
        arguments.mode,
        arguments.top_k,
        arguments.score_threshold,
        arguments.metadata_filter,
    )
    return {"results": [item.model_dump(mode="json") for item in results]}


def _search_topic(arguments: TopicSearchArgs, topic: str) -> dict:
    results = search(
        arguments.query,
        "hybrid",
        arguments.top_k,
        None,
        {"dataset": "multi_tool", "topic": topic, "status": "active"},
    )
    return {"results": [item.model_dump(mode="json") for item in results]}


def search_hotel_knowledge(arguments: TopicSearchArgs) -> dict:
    return _search_topic(arguments, "hotel")


def search_flight_knowledge(arguments: TopicSearchArgs) -> dict:
    return _search_topic(arguments, "flight")


def search_attraction_knowledge(arguments: TopicSearchArgs) -> dict:
    return _search_topic(arguments, "attraction")
