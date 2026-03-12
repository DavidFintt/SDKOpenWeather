from unittest.mock import patch, MagicMock
from datetime import date

import pytest

from openweather_sdk.client import OpenWeatherClient
from openweather_sdk.models import CurrentWeather


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


def _mock_geocoding_and_weather(mock_get):
    """Helper para mockar respostas de geocoding e clima."""
    geocoding_response = MagicMock()
    geocoding_response.status_code = 200
    geocoding_response.json.return_value = GEOCODING_RESPONSE

    weather_response = MagicMock()
    weather_response.status_code = 200
    weather_response.json.return_value = WEATHER_RESPONSE

    mock_get.side_effect = [geocoding_response, weather_response]

class TestCurrentWeather:
    """ Testes relacionados à validação dos dados retornados para construção do CurrentWeather. """

    @patch("openweather_sdk.client.requests.get")
    def test_get_current_weather_returns_correct_data(self, mock_get):
        """get_current_weather('London') retorna CurrentWeather com dados corretos."""
        _mock_geocoding_and_weather(mock_get)

        client = OpenWeatherClient(api_key="valid-key")
        result = client.get_current_weather(city="London")

        assert isinstance(result, CurrentWeather)
        assert result.temp == 10
        assert result.description == "algumas nuvens"
        assert result.city == "Londres"
        assert result.date == date.today().strftime("%d/%m")

    @patch("openweather_sdk.client.requests.get")
    def test_get_current_weather_by_coords(self, mock_get):
        """get_current_weather por coordenadas retorna CurrentWeather. Geocoding NÃO é chamado."""
        weather_response = MagicMock()
        weather_response.status_code = 200
        weather_response.json.return_value = WEATHER_RESPONSE
        mock_get.return_value = weather_response

        client = OpenWeatherClient(api_key="valid-key")
        result = client.get_current_weather(lat=51.5073, lon=-0.1276)

        assert isinstance(result, CurrentWeather)
        assert result.temp == 10
        assert result.description == "algumas nuvens"
