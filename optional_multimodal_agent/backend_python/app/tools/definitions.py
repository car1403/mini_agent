from app.schemas.models import HotelArgs, WeatherArgs


TRAVEL_TOOL_DEFINITIONS = [
    {
        "name": "get_weather",
        "description": "특정 도시와 날짜의 교육용 날씨 정보를 조회합니다.",
        "input_schema": WeatherArgs.model_json_schema(),
    },
    {
        "name": "search_hotels",
        "description": "도시, 체크인·체크아웃 날짜와 인원에 맞는 교육용 숙소를 조회합니다.",
        "input_schema": HotelArgs.model_json_schema(),
    },
]
