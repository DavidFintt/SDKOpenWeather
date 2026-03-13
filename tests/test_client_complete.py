from unittest.mock import patch, MagicMock
from datetime import date

import pytest

from openweather_sdk.client import OpenWeatherClient
from openweather_sdk.models import CompleteForecast, CurrentWeather, DayForecast


GEOCODING_RESPONSE = [
    {
        "name": "London",
        "local_names": {"pt": "Londres"},
        "lat": 51.5073219,
        "lon": -0.1276474,
        "country": "GB",
        "state": "England",
    }
]

WEATHER_RESPONSE = {
    "coord": {"lon": -0.1257, "lat": 51.5085},
    "weather": [{"id": 801, "main": "Clouds", "description": "algumas nuvens", "icon": "02n"}],
    "main": {"temp": 9.68, "feels_like": 8.63, "temp_min": 8.36, "temp_max": 10.56, "pressure": 1016, "humidity": 65},
    "name": "London",
    "cod": 200,
}

TODAY_STR = date.today().strftime("%Y-%m-%d")

FORECAST_RESPONSE = {
    "cod": "200",
    "list": [
        {"main": {"temp": 8.0}, "weather": [{"description": "clear sky"}], "dt_txt": f"{TODAY_STR} 15:00:00"},
        {"main": {"temp": 9.0}, "weather": [{"description": "clear sky"}], "dt_txt": f"{TODAY_STR} 18:00:00"},

        {"main": {"temp": 10.0}, "weather": [{"description": "clear sky"}], "dt_txt": "2026-03-20 00:00:00"},
        {"main": {"temp": 12.0}, "weather": [{"description": "clear sky"}], "dt_txt": "2026-03-20 03:00:00"},

        {"main": {"temp": 20.0}, "weather": [{"description": "clear sky"}], "dt_txt": "2026-03-21 00:00:00"},
        {"main": {"temp": 22.0}, "weather": [{"description": "clear sky"}], "dt_txt": "2026-03-21 03:00:00"},
        {"main": {"temp": 24.0}, "weather": [{"description": "clear sky"}], "dt_txt": "2026-03-21 06:00:00"},

        {"main": {"temp": 15.0}, "weather": [{"description": "clear sky"}], "dt_txt": "2026-03-22 00:00:00"},
        {"main": {"temp": 17.0}, "weather": [{"description": "clear sky"}], "dt_txt": "2026-03-22 03:00:00"},

        {"main": {"temp": 30.0}, "weather": [{"description": "clear sky"}], "dt_txt": "2026-03-23 00:00:00"},
        {"main": {"temp": 32.0}, "weather": [{"description": "clear sky"}], "dt_txt": "2026-03-23 03:00:00"},

        {"main": {"temp": 25.0}, "weather": [{"description": "clear sky"}], "dt_txt": "2026-03-24 00:00:00"},
        {"main": {"temp": 27.0}, "weather": [{"description": "clear sky"}], "dt_txt": "2026-03-24 03:00:00"},
    ],
}


def _mock_geocoding_weather_forecast(mock_get):
    """Helper para mockar respostas de geocoding, weather e forecast."""
    geocoding_response = MagicMock()
    geocoding_response.status_code = 200
    geocoding_response.json.return_value = GEOCODING_RESPONSE

    weather_response = MagicMock()
    weather_response.status_code = 200
    weather_response.json.return_value = WEATHER_RESPONSE

    forecast_response = MagicMock()
    forecast_response.status_code = 200
    forecast_response.json.return_value = FORECAST_RESPONSE

    mock_get.side_effect = [geocoding_response, weather_response, forecast_response]


def _mock_weather_forecast(mock_get):
    """Helper para mockar respostas de weather e forecast (sem geocoding)."""
    weather_response = MagicMock()
    weather_response.status_code = 200
    weather_response.json.return_value = WEATHER_RESPONSE

    forecast_response = MagicMock()
    forecast_response.status_code = 200
    forecast_response.json.return_value = FORECAST_RESPONSE

    mock_get.side_effect = [weather_response, forecast_response]


class TestCompleteWeather:
    """Testes para get_complete_weather()."""

    @patch("openweather_sdk.client.requests.get")
    def test_returns_complete_forecast(self, mock_get):
        """Por cidade retorna CompleteForecast com current e forecast."""
        _mock_geocoding_weather_forecast(mock_get)

        client = OpenWeatherClient(api_key="valid-key")
        result = client.get_complete_weather(city="London")

        assert isinstance(result, CompleteForecast)
        assert isinstance(result.current, CurrentWeather)
        assert isinstance(result.forecast, list)
        assert all(isinstance(day, DayForecast) for day in result.forecast)

    @patch("openweather_sdk.client.requests.get")
    def test_by_coords(self, mock_get):
        """Por coords retorna CompleteForecast sem geocoding."""
        _mock_weather_forecast(mock_get)

        client = OpenWeatherClient(api_key="valid-key")
        result = client.get_complete_weather(lat=51.5073, lon=-0.1276)

        assert isinstance(result, CompleteForecast)
        assert isinstance(result.current, CurrentWeather)
        assert isinstance(result.forecast, list)
        assert all(isinstance(day, DayForecast) for day in result.forecast)

    @patch("openweather_sdk.client.requests.get")
    def test_fields_are_correct(self, mock_get):
        """current e forecast têm os campos corretos."""
        _mock_geocoding_weather_forecast(mock_get)

        client = OpenWeatherClient(api_key="valid-key")
        result = client.get_complete_weather(city="London")

        assert result.current.temp == 10
        assert result.current.description == "algumas nuvens"
        assert result.current.city == "Londres"
        assert result.current.date == date.today().strftime("%d/%m")

        assert len(result.forecast) == 5
        assert result.forecast[0] == DayForecast(date="20/03", temp=11)
        assert result.forecast[1] == DayForecast(date="21/03", temp=22)
        assert result.forecast[2] == DayForecast(date="22/03", temp=16)
        assert result.forecast[3] == DayForecast(date="23/03", temp=31)
        assert result.forecast[4] == DayForecast(date="24/03", temp=26)
