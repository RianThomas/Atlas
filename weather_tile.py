import requests
import pygame
import tile_utils as u

# Livingston, NJ
LATITUDE = 40.7959
LONGITUDE = -74.3149
REFRESH_SECONDS = 600  # 10 minutes

weather = None

CONDITIONS = {
    0: "Clear", 1: "Mostly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Fog", 48: "Fog",
    51: "Light drizzle", 53: "Drizzle", 55: "Heavy drizzle",
    56: "Freezing drizzle", 57: "Freezing drizzle",
    61: "Light rain", 63: "Rain", 65: "Heavy rain",
    66: "Freezing rain", 67: "Freezing rain",
    71: "Light snow", 73: "Snow", 75: "Heavy snow", 77: "Snow grains",
    80: "Showers", 81: "Showers", 82: "Heavy showers",
    85: "Snow showers", 86: "Snow showers",
    95: "Thunderstorm", 96: "Thunderstorm", 99: "Thunderstorm",
}


def fetch():
    global weather
    params = {
        "latitude": LATITUDE,
        "longitude": LONGITUDE,
        "current": "temperature_2m,weather_code,wind_speed_10m,is_day",
        "hourly": "precipitation_probability",
        "temperature_unit": "fahrenheit",
        "wind_speed_unit": "mph",
        "timezone": "America/New_York",
        "forecast_days": 1,
    }
    response = requests.get("https://api.open-meteo.com/v1/forecast", params=params, timeout=10)
    response.raise_for_status()
    data = response.json()

    current = data["current"]
    this_hour = current["time"][:13]  # "2026-10-31T12"
    rain = 0
    for hour, chance in zip(data["hourly"]["time"], data["hourly"]["precipitation_probability"]):
        if hour[:13] == this_hour:
            rain = chance or 0

    weather = {
        "temp": round(current["temperature_2m"]),
        "code": current["weather_code"],
        "is_day": current["is_day"] == 1,
        "rain": rain,
        "wind": round(current["wind_speed_10m"]),
    }


def start():
    u.run_every(REFRESH_SECONDS, fetch, "weather")


def icon_kind(code):
    if code in (0, 1):
        return "clear"
    if code == 2:
        return "partly"
    if code in (45, 48):
        return "fog"
    if code >= 95:
        return "storm"
    if code in (71, 73, 75, 77, 85, 86):
        return "snow"
    if code >= 51:
        return "rain"
    return "cloud"


def draw_sun_or_moon(screen, center, radius, is_day):
    if is_day:
        pygame.draw.circle(screen, "gold", center, radius)
    else:
        pygame.draw.circle(screen, "lightyellow", center, radius)
        pygame.draw.circle(screen, u.TILE_BG, (center[0] + 7, center[1] - 5), radius - 2)


def draw_cloud(screen, cx, cy, color="gray90"):
    pygame.draw.circle(screen, color, (cx - 8, cy + 4), 11)
    pygame.draw.circle(screen, color, (cx + 6, cy), 13)
    pygame.draw.circle(screen, color, (cx + 18, cy + 6), 9)
    pygame.draw.rect(screen, color, pygame.Rect(cx - 8, cy + 4, 26, 11))


def draw_icon(screen, cx, cy, kind, is_day):
    if kind == "clear":
        draw_sun_or_moon(screen, (cx + 4, cy + 2), 17, is_day)
        return
    if kind == "partly":
        draw_sun_or_moon(screen, (cx + 10, cy - 8), 15, is_day)
        draw_cloud(screen, cx, cy)
        return

    draw_cloud(screen, cx, cy - 6, "gray80" if kind == "storm" else "gray90")
    if kind == "rain":
        for dx in (-6, 4, 14):
            pygame.draw.line(screen, "deepskyblue", (cx + dx, cy + 14), (cx + dx - 4, cy + 24), 2)
    elif kind == "snow":
        for dx in (-6, 4, 14):
            pygame.draw.circle(screen, u.TEXT, (cx + dx, cy + 20), 3)
    elif kind == "storm":
        pygame.draw.polygon(screen, "gold", [(cx + 6, cy + 10), (cx - 2, cy + 22), (cx + 4, cy + 22), (cx, cy + 32), (cx + 12, cy + 18), (cx + 5, cy + 18)])
    elif kind == "fog":
        for dy in (14, 20):
            pygame.draw.line(screen, u.MUTED, (cx - 12, cy + dy), (cx + 24, cy + dy), 2)


def draw_drop(screen, cx, cy):
    pygame.draw.circle(screen, "deepskyblue", (cx, cy + 3), 6)
    pygame.draw.polygon(screen, "deepskyblue", [(cx - 6, cy + 2), (cx + 6, cy + 2), (cx, cy - 9)])


def draw_wind(screen, x, y):
    pygame.draw.line(screen, u.MUTED, (x, y - 5), (x + 14, y - 5), 2)
    pygame.draw.line(screen, u.MUTED, (x, y), (x + 18, y), 2)
    pygame.draw.line(screen, u.MUTED, (x, y + 5), (x + 10, y + 5), 2)


def draw(screen, rect):
    if weather is None:
        u.title(screen, rect, "Weather")
        u.message(screen, rect, "Loading...")
        return

    u.text(screen, f"{weather['temp']}°", 60, u.TEXT, (rect.x + u.PAD, rect.y + 16), bold=True)
    draw_icon(screen, rect.right - 42, rect.y + 40, icon_kind(weather["code"]), weather["is_day"])
    condition = CONDITIONS.get(weather["code"], "")
    u.text(screen, u.fit(condition, 22, rect.width - u.PAD * 2), 22, u.MUTED, (rect.x + u.PAD, rect.y + 72))

    draw_drop(screen, rect.x + u.PAD + 7, rect.y + 120)
    u.text(screen, f"{weather['rain']}%", 26, u.TEXT, (rect.x + 44, rect.y + 112))

    draw_wind(screen, rect.x + u.PAD, rect.y + 158)
    u.text(screen, f"{weather['wind']} mph", 26, u.TEXT, (rect.x + 44, rect.y + 150))


def select():
    print("Weather selected")