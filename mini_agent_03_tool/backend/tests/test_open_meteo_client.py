from app.clients import open_meteo_client


class FakeResponse:
    def __init__(self, body: dict):
        self.body = body

    def raise_for_status(self) -> None:
        pass

    def json(self) -> dict:
        return self.body


def test_current_weather_is_normalized(monkeypatch) -> None:
    responses = iter([
        {"results": [{"name": "Pusan", "admin1": "경상북도", "feature_code": "PPL", "latitude": 36.38, "longitude": 128.36}, {"name": "부산광역시", "admin1": "부산광역시", "feature_code": "PPLA", "population": 3285147, "latitude": 35.10, "longitude": 129.03}]},
        {"current": {"time": "2026-08-19T12:00", "temperature_2m": 29.1, "apparent_temperature": 31.0, "precipitation": 0.0, "weather_code": 1, "wind_speed_10m": 8.4}},
    ])
    monkeypatch.setattr(open_meteo_client.httpx, "get", lambda *args, **kwargs: FakeResponse(next(responses)))

    result = open_meteo_client.fetch_current_weather("부산")

    assert result["city"] == "부산광역시"
    assert result["condition"] == "대체로 맑음"
    assert result["temperature_c"] == 29.1
    assert result["source"] == "open-meteo"


def test_unknown_city_is_rejected(monkeypatch) -> None:
    monkeypatch.setattr(open_meteo_client.httpx, "get", lambda *args, **kwargs: FakeResponse({"results": []}))

    try:
        open_meteo_client.geocode_city("없는도시")
    except ValueError as error:
        assert "찾을 수 없습니다" in str(error)
    else:
        raise AssertionError("도시 검색 실패가 ValueError를 발생시켜야 합니다.")
