"""TODO 3: 고객 문의 분류를 위한 SupportTicket Schema를 완성하세요."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class SupportTicket(BaseModel):
    model_config = ConfigDict(extra="forbid")

    # TODO: 각 Literal에 선언된 값만 허용되는지 확인하세요.
    category: Literal["billing", "technical", "account", "other"]
    priority: Literal["low", "medium", "high"]
    summary: str = Field(min_length=1, max_length=300)
    requires_human: bool = Field(strict=True)
    missing_information: list[str] = Field(default_factory=list, max_length=10)


# TODO: 정상 입력과 잘못된 Literal 입력을 각각 검증하세요.
