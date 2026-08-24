"""7개 Tool Use Lab의 신뢰 경계에서 사용하는 Pydantic 계약입니다.

HTTP 요청뿐 아니라 Ollama Agent가 만든 arguments도 같은 Schema로 다시 검증합니다.
따라서 LLM 출력은 제안일 뿐이며 Schema와 Service 정책을 통과하기 전에는 Tool에
전달되지 않습니다.
"""

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


LabId = Literal[
    "auto", "parking", "air_conditioner", "parcel_locker",
    "cafe", "library", "inventory", "travel",
]


class LabRunRequest(BaseModel):
    """Frontend가 단일 Lab Router로 보내는 공통 요청입니다."""
    model_config = ConfigDict(extra="forbid")

    message: str = Field(min_length=1, max_length=2000)
    session_id: str = Field(default="demo-session", min_length=1, max_length=100)
    lab_id: LabId = "auto"
    arguments: dict[str, Any] = Field(default_factory=dict)
    confirmed: bool = False
    action_id: str | None = None


class ParkingInput(BaseModel):
    """주차장 입력 Agent가 채우고 Workflow가 검사하는 arguments입니다."""
    model_config = ConfigDict(extra="forbid")
    plate_number: str | None = None


class AirConditionerInput(BaseModel):
    """에어컨 Agent 출력에 물리적으로 허용할 온도 범위를 적용합니다."""
    model_config = ConfigDict(extra="forbid")
    temperature_c: float | None = Field(default=None, ge=-40, le=80)


class ParcelLockerInput(BaseModel):
    """택배함 Agent의 추출 결과이며 실제 인증 성공을 의미하지 않습니다."""
    model_config = ConfigDict(extra="forbid")
    locker_id: str | None = None
    code: str | None = None


class InventoryInput(BaseModel):
    """재고 Agent 출력이며 현재 재고·Version과의 일치는 Service가 검사합니다."""
    model_config = ConfigDict(extra="forbid")
    sku: str | None = None
    quantity: int | None = Field(default=None, ge=1)
    expected_version: int | None = Field(default=None, ge=1)


class LabRouteDecision(BaseModel):
    """Routing Agent의 제안을 confidence와 허용된 Lab ID로 제한합니다."""
    lab_id: Literal[
        "parking", "air_conditioner", "parcel_locker", "cafe",
        "library", "inventory", "travel", "unknown",
    ]
    confidence: float = Field(ge=0, le=1)
    reason: str
    provider: str = "ollama"
    model: str


class LabRunResponse(BaseModel):
    """Workflow와 Agent 실행 결과를 Frontend가 동일하게 관찰하는 공통 계약입니다."""
    lab_id: str
    execution_type: Literal["workflow", "agent"]
    status: Literal["completed", "needs_clarification", "confirmation_required", "rejected", "error"]
    final_answer: str
    state: dict[str, Any] = Field(default_factory=dict)
    tool_calls: list[dict[str, Any]] = Field(default_factory=list)
    trace: list[dict[str, Any]] = Field(default_factory=list)
    termination_reason: str
    routing: LabRouteDecision | None = None

