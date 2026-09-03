from typing import Any, Literal


Risk = Literal["read", "change", "forbidden"]

def action_risk(annotations: dict[str, Any] | None) -> Risk:
    """신뢰된 MCP Server의 Tool annotation을 보수적으로 판정합니다."""
    if not annotations or "readOnlyHint" not in annotations:
        return "forbidden"
    return "read" if annotations["readOnlyHint"] is True else "change"
