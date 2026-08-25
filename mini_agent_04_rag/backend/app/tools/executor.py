"""Allowlist Tool의 입력을 검증하고 오류를 공통 계약으로 변환합니다."""

from pydantic import ValidationError

from app.schemas import ToolRunResult
from app.tools.registry import TOOL_REGISTRY


def execute_tool_safely(name: str, arguments: dict) -> ToolRunResult:
    spec = TOOL_REGISTRY.get(name)
    if spec is None:
        return ToolRunResult(
            success=False,
            tool_name=name,
            error={"code": "TOOL_NOT_ALLOWED", "message": "허용되지 않은 Tool입니다."},
        )
    try:
        return ToolRunResult(success=True, tool_name=name, data=spec.execute(arguments))
    except ValidationError as error:
        details = [
            {
                "field": ".".join(map(str, item["loc"])),
                "message": item["msg"],
                "type": item["type"],
            }
            for item in error.errors()
        ]
        return ToolRunResult(
            success=False,
            tool_name=name,
            error={"code": "TOOL_VALIDATION_ERROR", "details": details},
        )
    except Exception as error:
        return ToolRunResult(
            success=False,
            tool_name=name,
            error={"code": "TOOL_EXECUTION_ERROR", "message": str(error)},
        )


def run_tool(name: str, arguments: dict) -> dict:
    """기존 내부 호출자를 위한 호환 함수입니다.

    새 Agent와 Router는 구조화된 오류를 보존하는 execute_tool_safely를 사용합니다.
    """
    result = execute_tool_safely(name, arguments)
    if not result.success:
        raise ValueError(result.error)
    return result.data
