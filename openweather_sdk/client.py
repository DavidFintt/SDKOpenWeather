import requests
from collections import defaultdict
from datetime import date

from openweather_sdk.constants import GEOCODING_ENDPOINT, WEATHER_ENDPOINT, FORECAST_ENDPOINT
from openweather_sdk.exceptions import (
    APIKeyInvalidError,
    CityNotFoundError,
    InvalidCoordinatesError,
    InvalidInputError,
    NoWeatherDataError,
    OpenWeatherAPIError,
    RateLimitExceededError,
    RequestTimeoutError,
)
from openweather_sdk.models import CompleteForecast, CurrentWeather, DayForecast


class OpenWeatherClient:
    """Cliente principal para a API do OpenWeatherMap."""

    def __init__(self, api_key):
        """Inicializa o cliente com a chave de API.

        Args:
            api_key: Chave de API do OpenWeatherMap.

        Raises:
            APIKeyInvalidError: Se a chave for vazia ou None.
        """
        if not api_key:
            raise APIKeyInvalidError()
        self.api_key = api_key

    def _validate_input(self, city=None, lat=None, lon=None):
        """Valida os parametros de entrada antes de chamar a API."""
        if city is not None:
            if isinstance(city, list):
                raise InvalidInputError()
            if city == "":
                raise InvalidInputError()

        if lat is not None or lon is not None:
            if isinstance(lat, list) or isinstance(lon, list):
                raise InvalidInputError()
            if not isinstance(lat, (int, float)) or not isinstance(lon, (int, float)):
                raise InvalidCoordinatesError()
            if lat < -90 or lat > 90:
                raise InvalidCoordinatesError()
            if lon < -180 or lon > 180:
                raise InvalidCoordinatesError()

    def _check_response(self, response):
        """Verifica o status code da resposta e lanca excecoes especificas."""
        if response.status_code == 401:
            raise APIKeyInvalidError()
        if response.status_code == 429:
            raise RateLimitExceededError()
        if response.status_code >= 500:
            raise OpenWeatherAPIError()

    def _request(self, url, params, method="get"):
        """Executa a requisicao HTTP com timeout e tratamento de erros."""
        try:
            response = getattr(requests, method)(url, params=params, timeout=10)
        except requests.exceptions.Timeout:
            raise RequestTimeoutError()
        self._check_response(response)
        return response

    def _geocode(self, city):
        """Converte nome de cidade em coordenadas via Geocoding API."""
        params = {"q": city, "limit": 1, "appid": self.api_key}
        response = self._request(GEOCODING_ENDPOINT, params)
        data = response.json()
        if not data:
            raise CityNotFoundError()
        return data[0]

    def _get_current_weather(self, lat=None, lon=None):
        """Busca o clima atual para as coordenadas informadas."""
        params = {
            "lat": lat, "lon": lon,
            "lang": "pt_br", "units": "metric",
            "appid": self.api_key,
        }
        response = self._request(WEATHER_ENDPOINT, params)
        data = response.json()
        if "main" not in data:
            raise NoWeatherDataError()
        return CurrentWeather(
            temp=round(data["main"]["temp"]),
            description=data["weather"][0]["description"],
            city=data["name"],
            date=date.today().strftime("%d/%m"),
        )

    def _get_forecast(self, lat=None, lon=None):
        """Busca a previsao dos proximos 5 dias para as coordenadas informadas."""
        params = {
            "lat": lat, "lon": lon,
            "units": "metric",
            "appid": self.api_key,
        }
        response = self._request(FORECAST_ENDPOINT, params)
        data = response.json()

        today_str = date.today().strftime("%Y-%m-%d")
        days = defaultdict(list)
        for entry in data["list"]:
            day_str = entry["dt_txt"].split(" ")[0]
            if day_str == today_str:
                continue
            days[day_str].append(entry["main"]["temp"])

        forecast = []
        for day_str in sorted(days)[:5]:
            temps = days[day_str]
            avg = round(sum(temps) / len(temps))
            month, day = day_str.split("-")[1], day_str.split("-")[2]
            forecast.append(DayForecast(date=f"{day}/{month}", temp=avg))
        return forecast

    def get_complete_weather(self, city=None, lat=None, lon=None):
        """Retorna clima atual e previsao de 5 dias para uma cidade ou coordenadas."""
        self._validate_input(city=city, lat=lat, lon=lon)

        city_name = None
        if city:
            geo = self._geocode(city)
            lat = geo["lat"]
            lon = geo["lon"]
            local_names = geo.get("local_names", {})
            city_name = local_names.get("pt")

        current = self._get_current_weather(lat=lat, lon=lon)
        if city_name:
            current.city = city_name

        forecast = self._get_forecast(lat=lat, lon=lon)
        return CompleteForecast(current=current, forecast=forecast)
