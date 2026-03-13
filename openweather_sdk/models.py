from dataclasses import dataclass


@dataclass
class CurrentWeather:
    temp: int
    description: str
    city: str
    date: str


@dataclass
class DayForecast:
    date: str
    temp: int


@dataclass
class CompleteForecast:
    current: CurrentWeather
    forecast: list[DayForecast]
