class OpenWeatherError(Exception):
    """Base exception for all OpenWeather SDK errors."""


class APIKeyInvalidError(OpenWeatherError):
    def __init__(self, 
        message="API key inválida ou não autorizada."):
        super().__init__(message)


class CityNotFoundError(OpenWeatherError):
    def __init__(self,
        message = "Nenhum resultado encontrado para a cidade informada."):
        super().__init__(message)


class InvalidCoordinatesError(OpenWeatherError):
    def __init__(self,
        message = "Coordenadas inválidas."):
        super().__init__(message)


class NoWeatherDataError(OpenWeatherError):
    """Raised when coordinates are valid but no weather data is available for that location."""

    def __init__(self,
        message = "Nenhum dado meteorológico encontrado para as coordenadas informadas."):
        super().__init__(message)


class InvalidInputError(OpenWeatherError):
    def __init__(self, 
        message="Entrada inválida. Informe apenas uma cidade ou um par de coordenadas."):
        super().__init__(message)


class OpenWeatherAPIError(OpenWeatherError):
    def __init__(self, 
        message="API do OpenWeather indisponível. Tente novamente mais tarde."):
        super().__init__(message)


class RateLimitExceededError(OpenWeatherError):
    def __init__(self, 
        message="Limite de requisições atingido. Tente novamente mais tarde."):
        super().__init__(message)


class RequestTimeoutError(OpenWeatherError):
    def __init__(self, 
        message="Tempo limite da requisição excedido. Tente novamente mais tarde."):
        super().__init__(message)
