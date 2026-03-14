from unittest.mock import patch, MagicMock
from datetime import date

import pytest

from openweather_sdk.client import OpenWeatherClient
from openweather_sdk.models import CurrentWeather


WEATHER_RESPONSE = {
    "coord": {"lon": -0.1257, "lat": 51.5085},
    "weather": [{"id": 801, "main": "Clouds", "description": "algumas nuvens", "icon": "02n"}],
    "main": {"temp": 9.68, "feels_like": 8.63, "temp_min": 8.36, "temp_max": 10.56, "pressure": 1016, "humidity": 65},
    "name": "London",
    "cod": 200,
}


class TestCurrentWeather:
    """ Testes relacionados à validação dos dados retornados para construção do CurrentWeather. """

    @patch("openweather_sdk.client.requests.get")
    def test_get_current_weather_by_coords(self, mock_get):
        """get_current_weather por coordenadas retorna CurrentWeather com dados corretos."""
        weather_response = MagicMock()
        weather_response.status_code = 200
        weather_response.json.return_value = WEATHER_RESPONSE
        mock_get.return_value = weather_response

        client = OpenWeatherClient(api_key="valid-key")
        result = client._get_current_weather(lat=51.5073, lon=-0.1276)

        assert isinstance(result, CurrentWeather)
        assert result.temp == 10
        assert result.description == "algumas nuvens"
        assert result.city == "London"
        assert result.date == date.today().strftime("%d/%m")
