from typing import Any

from core.api_client import request


def get_health():
    return request("GET", "/health")


def get_providers():
    return request("GET", "/api/providers")


def compare_concepts(message: str):
    return request("POST", "/api/concepts/compare", json={"message": message})


def classify_travel(message: str):
    return request("POST", "/api/travel/classify", json={"message": message})


def generate_response(provider: str, system_prompt: str, message: str):
    return request("POST", "/api/generate", json={"provider": provider, "system_prompt": system_prompt, "message": message})


def compare_providers(providers: list[str], message: str):
    return request("POST", "/api/providers/compare", json={"providers": providers, "message": message})


def preview_prompt(
    role: str,
    instruction: str,
    context: str,
    constraint: str,
    output_format: str = "",
):
    return request(
        "POST",
        "/api/prompts/preview",
        json={
            "role": role,
            "instruction": instruction,
            "context": context,
            "constraint": constraint,
            "output_format": output_format,
        },
    )


def validate_structured_output(schema_type: str, payload: dict[str, Any]):
    return request(
        "POST",
        "/api/structured/validate",
        json={"schema_type": schema_type, "payload": payload},
    )


def generate_structured_output(provider: str, message: str, schema_type: str):
    return request(
        "POST",
        "/api/structured/generate",
        json={"provider": provider, "message": message, "schema_type": schema_type},
    )


def compare_structured_outputs(
    providers: list[str], message: str, schema_type: str = "travel_plan"
):
    return request(
        "POST",
        "/api/structured/compare",
        json={"providers": providers, "message": message, "schema_type": schema_type},
    )
