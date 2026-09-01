"""Allowlist에 등록된 Tool만 찾아 입력 검증 후 실행합니다."""

from app.tools.registry import TOOL_REGISTRY

def run_tool(name: str, arguments: dict) -> dict:
    spec = TOOL_REGISTRY.get(name)
    if spec is None:
        raise PermissionError("허용되지 않은 Tool입니다.")
    return spec.execute(arguments)
