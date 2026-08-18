from app.schemas import AttractionArgs, HotelArgs, WeatherArgs


TRAVEL_TOOL_DEFINITIONS = [
    {"name": "get_weather", "description": "특정 도시와 날짜의 교육용 날씨를 조회합니다.", "input_schema": WeatherArgs.model_json_schema()},
    {"name": "search_hotels", "description": "도시, 날짜, 인원에 맞는 교육용 숙소를 조회합니다.", "input_schema": HotelArgs.model_json_schema()},
    {"name": "search_attractions", "description": "도시와 분류에 맞는 교육용 관광지를 조회합니다.", "input_schema": AttractionArgs.model_json_schema()},
]
