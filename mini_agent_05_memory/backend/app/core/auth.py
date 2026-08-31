"""교육용 Header를 Backend가 확인한 사용자 범위로 변환합니다."""

from typing import Annotated

from fastapi import Header, HTTPException


async def get_authenticated_user_id(
    x_demo_user_id: Annotated[
        str | None,
        Header(alias="X-Demo-User-ID", min_length=1, max_length=100, pattern=r"^[A-Za-z0-9._-]+$"),
    ] = None,
) -> str:
    """운영 환경의 JWT/Session 검증을 대신하는 수업용 Dependency입니다."""
    if x_demo_user_id is None:
        raise HTTPException(
            status_code=401,
            detail="X-Demo-User-ID Header가 필요합니다.",
        )
    return x_demo_user_id
