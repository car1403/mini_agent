from datetime import date

from app.tools.travel import functions


class Response:
    def __init__(self, payload):
        self.payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self.payload


def test_weather_uses_open_meteo(monkeypatch) -> None:
    calls = []

    def get(url, **kwargs):
        calls.append(url)
        if "geocoding" in url:
            return Response({"results": [{"name": "부산", "latitude": 35.18, "longitude": 129.07}]})
        return Response(
            {
                "daily": {
                    "time": ["2026-09-01"],
                    "weather_code": [1],
                    "temperature_2m_max": [27],
                    "temperature_2m_min": [21],
                    "precipitation_probability_max": [20],
                }
            }
        )

    monkeypatch.setattr(functions.httpx, "get", get)
    result = functions.get_weather({"city": "부산", "target_date": date(2026, 9, 1)})
    assert result["source"] == "Open-Meteo"
    assert result["temperature_max_c"] == 27
    assert any("geocoding-api.open-meteo.com" in url for url in calls)
    assert any("api.open-meteo.com" in url for url in calls)


def test_place_tools_use_openstreetmap(monkeypatch) -> None:
    monkeypatch.setattr(
        functions.httpx,
        "get",
        lambda *args, **kwargs: Response(
            [{"name": "부산 박물관", "display_name": "부산 박물관, 대한민국", "lat": "35.1", "lon": "129.0"}]
        ),
    )
    hotels = functions.search_hotels(
        {"city": "부산", "check_in": "2026-09-01", "check_out": "2026-09-03", "guests": 2}
    )
    attractions = functions.search_attractions({"city": "부산", "category": "culture"})
    assert hotels["source"] == "OpenStreetMap Nominatim"
    assert attractions["source"] == "OpenStreetMap Nominatim"
