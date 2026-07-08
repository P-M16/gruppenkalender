import os
import requests
from dotenv import load_dotenv

load_dotenv()

WEATHER_CITY = os.getenv("WEATHER_CITY", "Innsbruck")

# WMO Wettercode -> (Emoji, Kurzbeschreibung)
WEATHER_CODES = {
    0: ("☀️", "Klar"),
    1: ("🌤️", "Überwiegend klar"),
    2: ("⛅", "Teilweise bewölkt"),
    3: ("☁️", "Bedeckt"),
    45: ("🌫️", "Nebel"),
    48: ("🌫️", "Nebel mit Reifbildung"),
    51: ("🌦️", "Leichter Nieselregen"),
    53: ("🌦️", "Nieselregen"),
    55: ("🌦️", "Starker Nieselregen"),
    61: ("🌧️", "Leichter Regen"),
    63: ("🌧️", "Regen"),
    65: ("🌧️", "Starker Regen"),
    71: ("❄️", "Leichter Schneefall"),
    73: ("❄️", "Schneefall"),
    75: ("❄️", "Starker Schneefall"),
    80: ("🌦️", "Regenschauer"),
    81: ("🌦️", "Regenschauer"),
    82: ("🌦️", "Heftige Regenschauer"),
    95: ("⛈️", "Gewitter"),
    96: ("⛈️", "Gewitter mit Hagel"),
    99: ("⛈️", "Gewitter mit Hagel"),
}


def weather_icon(code: int) -> str:
    return WEATHER_CODES.get(code, ("🌡️", "Unbekannt"))[0]


def weather_description(code: int) -> str:
    return WEATHER_CODES.get(code, ("🌡️", "Unbekannt"))[1]


def get_coordinates(city: str = WEATHER_CITY):
    """Wandelt einen Stadtnamen in Koordinaten um (Geocoding, ohne API-Key)."""
    response = requests.get(
        "https://geocoding-api.open-meteo.com/v1/search",
        params={"name": city, "count": 1, "language": "de", "format": "json"},
        timeout=10,
    )
    response.raise_for_status()
    results = response.json().get("results")
    if not results:
        raise ValueError(f"Ort '{city}' wurde nicht gefunden.")
    return results[0]["latitude"], results[0]["longitude"]


def get_daily_forecast(city: str = WEATHER_CITY):
    """Holt die Tagesvorhersage (ca. 16 Tage) für eine Stadt.
    Gibt ein Dict zurück: {"YYYY-MM-DD": {"code": int, "tmax": float, "tmin": float}}."""
    lat, lon = get_coordinates(city)
    response = requests.get(
        "https://api.open-meteo.com/v1/forecast",
        params={
            "latitude": lat,
            "longitude": lon,
            "daily": "weathercode,temperature_2m_max,temperature_2m_min",
            "timezone": "auto",
            "forecast_days": 16,
        },
        timeout=10,
    )
    response.raise_for_status()
    daily = response.json().get("daily", {})

    forecast = {}
    for date_str, code, tmax, tmin in zip(
        daily.get("time", []),
        daily.get("weathercode", []),
        daily.get("temperature_2m_max", []),
        daily.get("temperature_2m_min", []),
    ):
        forecast[date_str] = {"code": code, "tmax": tmax, "tmin": tmin}
    return forecast
