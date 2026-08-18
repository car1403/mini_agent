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


def compare_providers(providers: list[str], system_prompt: str, message: str):
    return request("POST", "/api/providers/compare", json={"providers": providers, "system_prompt": system_prompt, "message": message})
