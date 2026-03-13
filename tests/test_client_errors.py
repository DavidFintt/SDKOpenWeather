from unittest.mock import patch, MagicMock

import pytest
import requests

from openweather_sdk.client import OpenWeatherClient
from openweather_sdk.exceptions import (
    APIKeyInvalidError,
    OpenWeatherAPIError,
    RateLimitExceededError,
    RequestTimeoutError,
)


METHODS = ["get_current_weather", "get_forecast"]


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

    @pytest.mark.parametrize("method", METHODS)
    @patch("openweather_sdk.client.requests.get")
    def test_http_401_raises_api_key_invalid(self, mock_get, method):
        """Chamar API com token invalido e receber HTTP 401."""
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.json.return_value = {"cod": 401, "message": "Invalid API key"}
        mock_get.return_value = mock_response

        client = OpenWeatherClient(api_key="invalid-key")
        with pytest.raises(APIKeyInvalidError):
            getattr(client, method)(lat=51.5, lon=-0.1)

class TestAPIErrors:
    """ Testes relacionados a erros da API do OpenWeather. """

    @pytest.mark.parametrize("method", METHODS)
    @patch("openweather_sdk.client.requests.get")
    def test_http_500_raises_api_error(self, mock_get, method):
        """API retorna HTTP 500."""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.json.return_value = {}
        mock_get.return_value = mock_response

        client = OpenWeatherClient(api_key="valid-key")
        with pytest.raises(OpenWeatherAPIError):
            getattr(client, method)(lat=51.5, lon=-0.1)

    @pytest.mark.parametrize("method", METHODS)
    @patch("openweather_sdk.client.requests.get")
    def test_http_429_raises_rate_limit(self, mock_get, method):
        """API retorna HTTP 429."""
        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_response.json.return_value = {}
        mock_get.return_value = mock_response

        client = OpenWeatherClient(api_key="valid-key")
        with pytest.raises(RateLimitExceededError):
            getattr(client, method)(lat=51.5, lon=-0.1)

    @pytest.mark.parametrize("method", METHODS)
    @patch("openweather_sdk.client.requests.get")
    def test_timeout_raises_request_timeout_error(self, mock_get, method):
        """Timeout na requisição."""
        mock_get.side_effect = requests.exceptions.Timeout("Connection timed out")

        client = OpenWeatherClient(api_key="valid-key")
        with pytest.raises(RequestTimeoutError):
            getattr(client, method)(lat=51.5, lon=-0.1)
