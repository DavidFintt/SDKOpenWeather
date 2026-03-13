from unittest.mock import patch, MagicMock

import pytest

from openweather_sdk.client import OpenWeatherClient
from openweather_sdk.exceptions import CityNotFoundError


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
    def test_geocoding_empty_list_raises_city_not_found(self, mock_get):
        """Geocoding retorna lista vazia (cidade não encontrada)."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = []
        mock_get.return_value = mock_response

        client = OpenWeatherClient(api_key="valid-key")
        with pytest.raises(CityNotFoundError):
            client.get_complete_weather(city="cidadeinexistente")
