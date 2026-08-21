"""Allowlist Tool을 찾아 입력 검증과 오류 표준화를 거쳐 안전하게 실행합니다.

`agents.runtime`과 `/api/tools/run` Endpoint가 모든 Tool 실행에 사용합니다.
"""

from pydantic import ValidationError

from app.schemas.stage_03 import ToolRunResult
from app.tools.registry import TOOL_REGISTRY


def execute_tool_safely(name: str, arguments: dict) -> ToolRunResult:
    tool = TOOL_REGISTRY.get(name)
    if tool is None:
        return ToolRunResult(success=False, tool_name=name, error={"code": "TOOL_NOT_ALLOWED", "message": "허용되지 않은 Tool입니다."})
    try:
        return ToolRunResult(success=True, tool_name=name, data=tool.execute(arguments))
    except ValidationError as error:
        details = [{"field": ".".join(map(str, item["loc"])), "message": item["msg"], "type": item["type"]} for item in error.errors()]
        return ToolRunResult(success=False, tool_name=name, error={"code": "TOOL_VALIDATION_ERROR", "details": details})
    except Exception as error:
        return ToolRunResult(success=False, tool_name=name, error={"code": "TOOL_EXECUTION_ERROR", "message": str(error)})
