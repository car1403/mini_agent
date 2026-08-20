from app.schemas import AttractionArgs, CurrentWeatherArgs, HotelArgs, WeatherForecastArgs


TRAVEL_TOOL_DEFINITIONS = [
    {"name": "get_current_weather", "description": "특정 도시의 현재 기온, 체감 온도, 강수량과 바람을 조회합니다. 미래 날짜 예보에는 사용하지 않습니다.", "input_schema": CurrentWeatherArgs.model_json_schema()},
    {"name": "get_weather_forecast", "description": "특정 도시의 내일, 주말 또는 미래 날짜 날씨 예보를 조회합니다. 현재 날씨 질문에는 사용하지 않습니다.", "input_schema": WeatherForecastArgs.model_json_schema()},
    {"name": "search_hotels", "description": "도시, 날짜, 인원에 맞는 교육용 숙소를 조회합니다.", "input_schema": HotelArgs.model_json_schema()},
    {"name": "search_attractions", "description": "도시와 분류에 맞는 교육용 관광지를 조회합니다.", "input_schema": AttractionArgs.model_json_schema()},
]

def get_tool_definitions() -> list[dict]:
    """운영과 학습에 공통으로 사용하는 명확한 Tool 계약을 반환합니다."""
    return TRAVEL_TOOL_DEFINITIONS
