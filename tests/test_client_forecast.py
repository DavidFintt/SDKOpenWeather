from unittest.mock import patch, MagicMock
from datetime import date

import pytest

from openweather_sdk.client import OpenWeatherClient
from openweather_sdk.models import DayForecast


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


def _mock_forecast(mock_get):
    """Helper para mockar resposta de forecast."""
    forecast_response = MagicMock()
    forecast_response.status_code = 200
    forecast_response.json.return_value = FORECAST_RESPONSE
    mock_get.return_value = forecast_response


class TestForecast:
    """Testes relacionados ao método get_forecast e à construção dos DayForecast."""

    @patch("openweather_sdk.client.requests.get")
    def test_get_forecast_returns_list_of_day_forecast(self, mock_get):
        """get_forecast retorna lista de DayForecast."""
        _mock_forecast(mock_get)

        client = OpenWeatherClient(api_key="valid-key")
        result = client.get_forecast(lat=51.5073, lon=-0.1276)

        assert isinstance(result, list)
        assert len(result) > 0
        assert all(isinstance(day, DayForecast) for day in result)

    @patch("openweather_sdk.client.requests.get")
    def test_get_forecast_excludes_today(self, mock_get):
        """Entries de hoje são excluídas do resultado do forecast."""
        _mock_forecast(mock_get)

        client = OpenWeatherClient(api_key="valid-key")
        result = client.get_forecast(lat=51.5073, lon=-0.1276)

        today_str = date.today().strftime("%d/%m")
        dates = [day.date for day in result]
        assert today_str not in dates

    @patch("openweather_sdk.client.requests.get")
    def test_get_forecast_calculates_average_temp(self, mock_get):
        """Temperatura de cada dia é a média arredondada das entries."""
        _mock_forecast(mock_get)

        client = OpenWeatherClient(api_key="valid-key")
        result = client.get_forecast(lat=51.5073, lon=-0.1276)

        temps = {day.date: day.temp for day in result}
        assert temps["20/03"] == 11
        assert temps["21/03"] == 22
        assert temps["22/03"] == 16
        assert temps["23/03"] == 31
        assert temps["24/03"] == 26

    @patch("openweather_sdk.client.requests.get")
    def test_get_forecast_days_in_order(self, mock_get):
        """Dias retornados em ordem crescente de data."""
        _mock_forecast(mock_get)

        client = OpenWeatherClient(api_key="valid-key")
        result = client.get_forecast(lat=51.5073, lon=-0.1276)

        dates = [day.date for day in result]
        assert dates == ["20/03", "21/03", "22/03", "23/03", "24/03"]

    @patch("openweather_sdk.client.requests.get")
    def test_get_forecast_max_5_days(self, mock_get):
        """No máximo 5 dias retornados, mesmo que a API retorne mais."""
        response = {
            "cod": "200",
            "list": [
                {"main": {"temp": 20.0}, "weather": [{"description": "clear sky"}], "dt_txt": f"2026-04-0{i} 12:00:00"}
                for i in range(1, 8) 
            ],
        }

        forecast_response = MagicMock()
        forecast_response.status_code = 200
        forecast_response.json.return_value = response
        mock_get.return_value = forecast_response

        client = OpenWeatherClient(api_key="valid-key")
        result = client.get_forecast(lat=51.5073, lon=-0.1276)

        assert len(result) <= 5

