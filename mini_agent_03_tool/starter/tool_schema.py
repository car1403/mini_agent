"""TODO 1: WeatherArgs와 HotelArgs의 검증 조건을 완성하세요."""

from datetime import date
from pydantic import BaseModel, Field


class WeatherArgs(BaseModel):
    city: str = Field(min_length=1)
    target_date: date


class HotelArgs(BaseModel):
    city: str = Field(min_length=1)
    check_in: date
    check_out: date
    # TODO: 1명 이상 10명 이하로 제한하세요.
    guests: int
