from unittest.mock import patch, MagicMock

import pytest
import requests

from openweather_sdk.client import OpenWeatherClient
from openweather_sdk.exceptions import (
    APIKeyInvalidError,
    CityNotFoundError,
    InvalidCoordinatesError,
    InvalidInputError,
    NoWeatherDataError,
    OpenWeatherAPIError,
    RateLimitExceededError,
)


class TestAPIKeyValidation:
    """ Testes relacionados à validação da API key e erros de autenticação. """

    def test_empty_api_key_raises_error(self):
        """Criar client com API key vazia."""
        with pytest.raises(APIKeyInvalidError):
            OpenWeatherClient(api_key="")

    def test_none_api_key_raises_error(self):
        """Criar client com API key None."""
        with pytest.raises(APIKeyInvalidError):
            OpenWeatherClient(api_key=None)

    @patch("openweather_sdk.client.requests.get")
    def test_http_401_raises_api_key_invalid(self, mock_get):
        """Chamar API com token invalido e receber HTTP 401."""
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.json.return_value = {"cod": 401, "message": "Invalid API key"}
        mock_get.return_value = mock_response

        client = OpenWeatherClient(api_key="invalid-key")
        with pytest.raises(APIKeyInvalidError):
            client.get_current_weather(city="London")


class TestCityValidation:

    @patch("openweather_sdk.client.requests.get")
    def test_geocoding_empty_list_raises_city_not_found(self, mock_get):
        """Geocoding retorna lista vazia (cidade não encontrada)."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = []
        mock_get.return_value = mock_response

        client = OpenWeatherClient(api_key="valid-key")
        with pytest.raises(CityNotFoundError):
            client.get_current_weather(city="cidadeinexistente")

    def test_empty_city_raises_invalid_input(self):
        """Buscar cidade com string vazia."""
        client = OpenWeatherClient(api_key="valid-key")
        with pytest.raises(InvalidInputError):
            client.get_current_weather(city="")

    def test_multiple_cities_raises_invalid_input(self):
        """Buscar com múltiplas cidades (lista)."""
        client = OpenWeatherClient(api_key="valid-key")
        with pytest.raises(InvalidInputError):
            client.get_current_weather(city=["London", "Paris"])

class TestCoordinatesValidation:
    """ Testes relacionados à validação de coordenadas e erros associados. """

    def test_latitude_out_of_range_raises_error(self):
        """Latitude fora do range (-90 a 90)."""
        client = OpenWeatherClient(api_key="valid-key")
        with pytest.raises(InvalidCoordinatesError):
            client.get_current_weather(lat=91, lon=0)

    def test_longitude_out_of_range_raises_error(self):
        """Longitude fora do range (-180 a 180)."""
        client = OpenWeatherClient(api_key="valid-key")
        with pytest.raises(InvalidCoordinatesError):
            client.get_current_weather(lat=0, lon=181)

    def test_non_numeric_coordinates_raises_error(self):
        """Latitude/longitude não numérica."""
        client = OpenWeatherClient(api_key="valid-key")
        with pytest.raises(InvalidCoordinatesError):
            client.get_current_weather(lat="abc", lon="xyz")

    def test_multiple_coordinate_pairs_raises_error(self):
        """Múltiplos pares de coordenadas."""
        client = OpenWeatherClient(api_key="valid-key")
        with pytest.raises(InvalidInputError):
            client.get_current_weather(lat=[51.5, 48.8], lon=[-0.1, 2.3])


class TestAPIErrors:
    """ Testes relacionados a erros da API do OpenWeather. """

    @patch("openweather_sdk.client.requests.get")
    def test_http_500_raises_api_error(self, mock_get):
        """API retorna HTTP 500."""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.json.return_value = {}
        mock_get.return_value = mock_response

        client = OpenWeatherClient(api_key="valid-key")
        with pytest.raises(OpenWeatherAPIError):
            client.get_current_weather(city="London")

    @patch("openweather_sdk.client.requests.get")
    def test_http_429_raises_rate_limit(self, mock_get):
        """API retorna HTTP 429."""
        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_response.json.return_value = {}
        mock_get.return_value = mock_response

        client = OpenWeatherClient(api_key="valid-key")
        with pytest.raises(RateLimitExceededError):
            client.get_current_weather(city="London")

    @patch("openweather_sdk.client.requests.get")
    def test_timeout_raises_api_error(self, mock_get):
        """Timeout na requisição."""
        mock_get.side_effect = requests.exceptions.Timeout("Connection timed out")

        client = OpenWeatherClient(api_key="valid-key")
        with pytest.raises(OpenWeatherAPIError):
            client.get_current_weather(city="London")
