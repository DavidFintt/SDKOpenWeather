from unittest.mock import patch, MagicMock, call

import pytest

from openweather_sdk.client import OpenWeatherClient


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

class TestGeocoding:
    """ Testes relacionados à API de Geocoding do OpenWeather e à função _geocode. """

    @patch("openweather_sdk.client.requests.get")
    def test_geocode_returns_correct_lat_lon(self, mock_get):
        """_geocode('London') monta e retorna lat/lon corretos."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = GEOCODING_RESPONSE
        mock_get.return_value = mock_response

        client = OpenWeatherClient(api_key="valid-key")
        result = client._geocode("London")

        assert result["lat"] == 51.5073219
        assert result["lon"] == -0.1276474

    @patch("openweather_sdk.client.requests.get")
    def test_get_current_weather_calls_geocoding_then_weather(self, mock_get):
        """Geocoding é chamado automaticamente em get_current_weather('London')."""
        geocoding_response = MagicMock()
        geocoding_response.status_code = 200
        geocoding_response.json.return_value = GEOCODING_RESPONSE

        weather_response = MagicMock()
        weather_response.status_code = 200
        weather_response.json.return_value = WEATHER_RESPONSE

        mock_get.side_effect = [geocoding_response, weather_response]

        client = OpenWeatherClient(api_key="valid-key")
        client.get_current_weather(city="London")

        assert mock_get.call_count == 2

    @patch("openweather_sdk.client.requests.get")
    def test_get_current_weather_by_coords_skips_geocoding(self, mock_get):
        """Geocoding NÃO é chamado quando lat/lon são passados diretamente."""
        weather_response = MagicMock()
        weather_response.status_code = 200
        weather_response.json.return_value = WEATHER_RESPONSE

        mock_get.return_value = weather_response

        client = OpenWeatherClient(api_key="valid-key")
        client.get_current_weather(lat=51.5073, lon=-0.1276)

        assert mock_get.call_count == 1
