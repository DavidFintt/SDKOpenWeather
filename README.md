# OpenWeather SDK

SDK Python para consulta de dados meteorologicos via API do OpenWeatherMap.

## Instalacao

```bash
pip install git+https://github.com/DavidFintt/SDKOpenWeather
```

## Configuracao

Obtenha uma API key em (https://openweathermap.org/) e passe ao client:

```python
from openweather_sdk import OpenWeatherClient

client = OpenWeatherClient(api_key="sua_api_key")
```

## Metodos

### get_complete_weather

Retorna clima atual e previsao dos proximos 5 dias. Aceita busca por cidade ou por coordenadas.

```python
# Por cidade
result = client.get_complete_weather(city="London")

# Por coordenadas
result = client.get_complete_weather(lat=-23.55, lon=-46.63)
```

**Retorno:** `CompleteForecast`

```python
result.current   # CurrentWeather (clima atual)
result.forecast  # list[DayForecast] (previsao dos proximos dias)
```

### Campos de retorno

**CurrentWeather:**

| Campo         | Tipo  | Descricao                            |
|---------------|-------|--------------------------------------|
| `temp`        | int   | Temperatura em Celsius (arredondada) |
| `description` | str   | Descricao do clima em portugues      |
| `city`        | str   | Nome da cidade                       |
| `date`        | str   | Data no formato DD/MM                |

**DayForecast:**

| Campo  | Tipo | Descricao                                  |
|--------|------|--------------------------------------------|
| `date` | str  | Data no formato DD/MM                      |
| `temp` | int  | Temperatura media em Celsius (arredondada) |

## Exceptions

Todas as excecoes herdam de `OpenWeatherError`, permitindo captura generica:

```python
from openweather_sdk import OpenWeatherError

try:
    resultado = client.get_complete_weather(city="London")
except OpenWeatherError as e:
    print(e)
```

Para tratamento especifico:

| Excecao                  | Quando ocorre                                      |
|--------------------------|-----------------------------------------------------|
| `APIKeyInvalidError`     | API key vazia, nula ou rejeitada pela API (HTTP 401) |
| `CityNotFoundError`      | Cidade nao encontrada no geocoding                  |
| `InvalidCoordinatesError`| Latitude/longitude fora do intervalo ou nao numerica |
| `InvalidInputError`      | Entrada invalida (cidade vazia, listas, etc.)       |
| `NoWeatherDataError`     | Coordenadas validas mas sem dados meteorologicos    |
| `OpenWeatherAPIError`    | Erro no servidor da API (HTTP 5xx)                  |
| `RateLimitExceededError` | Limite de requisicoes atingido (HTTP 429)           |
| `RequestTimeoutError`    | Requisicao excedeu o tempo limite                   |

## Testes

Os testes usam `pytest` e nao fazem chamadas reais a API (todas as requisicoes sao mockadas).

```bash
pip install -e ".[dev]"
pytest
```

## Estrutura do projeto

```
openweather_sdk/
    __init__.py       # Exportacoes publicas
    client.py         # OpenWeatherClient (facade principal)
    models.py         # Dataclasses de retorno
    exceptions.py     # Hierarquia de excecoes
    constants.py      # URLs base e endpoints
tests/
    test_client_complete.py
    test_client_errors.py
    test_client_forecast.py
    test_client_geocoding.py
    test_client_weather.py
setup.py
```
