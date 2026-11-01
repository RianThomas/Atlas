from datetime import datetime
import requests
import pygame
import tile_utils as u

NFL_FAVORITES = ["Chiefs", "Jets", "Giants"]
NBA_FAVORITES = ["Knicks", "Warriors"]

ESPN_URL = "https://site.api.espn.com/apis/site/v2/sports/{}/scoreboard"

nfl_games = None
nba_games = None


def parse_games(data, favorites):
    games = []
    for event in data.get("events", []):
        competition = event["competitions"][0]
        sides = {team["homeAway"]: team for team in competition["competitors"]}
        away = sides["away"]
        home = sides["home"]

        away_names = [away["team"].get("name", ""), away["team"].get("shortDisplayName", "")]
        home_names = [home["team"].get("name", ""), home["team"].get("shortDisplayName", "")]

        start_time = datetime.fromisoformat(event["date"].replace("Z", "+00:00")).astimezone()

        games.append({
            "away": away["team"]["abbreviation"],
            "home": home["team"]["abbreviation"],
            "away_score": away.get("score", ""),
            "home_score": home.get("score", ""),
            "away_favorite": any(n in favorites for n in away_names),
            "home_favorite": any(n in favorites for n in home_names),
            "state": event["status"]["type"]["state"],  # "pre", "in" or "post"
            "start": start_time,
        })

    # Favorite teams first, then live games, then upcoming, then finished
    order = {"in": 0, "pre": 1, "post": 2}
    games.sort(key=lambda g: (
        not (g["away_favorite"] or g["home_favorite"]),
        order.get(g["state"], 3),
        g["start"],
    ))
    return games[:3]


def fetch():
    global nfl_games, nba_games
    nfl = requests.get(ESPN_URL.format("football/nfl"), timeout=10)
    nfl.raise_for_status()
    nfl_games = parse_games(nfl.json(), NFL_FAVORITES)

    nba = requests.get(ESPN_URL.format("basketball/nba"), timeout=10)
    nba.raise_for_status()
    nba_games = parse_games(nba.json(), NBA_FAVORITES)


def refresh_seconds():
    # Every 30 seconds during a live game, otherwise every 10 minutes
    for games in (nfl_games or [], nba_games or []):
        for game in games:
            if game["state"] == "in":
                return 30
    return 600


def start():
    u.run_every(refresh_seconds, fetch, "sports")


def middle_label(game):
    if game["state"] == "in":
        return "LIVE"
    if game["state"] == "post":
        return "F"
    return game["start"].strftime("%a %-I:%M")


def draw_column(screen, x, y, width, league, games):
    u.text(screen, league, 24, u.TEXT, (x + width // 2, y), bold=True, align="center")
    y += 26
    if games is None:
        u.text(screen, "Loading...", 18, u.MUTED, (x + width // 2, y + 8), align="center")
        return
    if not games:
        u.text(screen, "No games", 18, u.MUTED, (x + width // 2, y + 8), align="center")
        return

    for game in games:
        pill = pygame.Rect(x, y, width, 28)
        pygame.draw.rect(screen, u.INNER_BG, pill, border_radius=14)

        away_color = u.ACCENT if game["away_favorite"] else u.TEXT
        home_color = u.ACCENT if game["home_favorite"] else u.TEXT
        if game["state"] == "pre":
            left = game["away"]
            right = game["home"]
        else:
            left = f"{game['away']} {game['away_score']}"
            right = f"{game['home_score']} {game['home']}"

        middle_color = u.DOWN_COLOR if game["state"] == "in" else u.MUTED
        u.text(screen, left, 18, away_color, (pill.x + 10, pill.y + 8))
        u.text(screen, middle_label(game), 16, middle_color, (pill.centerx, pill.y + 9), align="center")
        u.text(screen, right, 18, home_color, (pill.right - 10, pill.y + 8), align="right")
        y += 34


def draw(screen, rect):
    u.title(screen, rect, "Sports")
    line_y = rect.y + 46
    pygame.draw.line(screen, u.MUTED, (rect.x + u.PAD, line_y), (rect.right - u.PAD, line_y), 1)
    pygame.draw.line(screen, u.MUTED, (rect.centerx, line_y + 8), (rect.centerx, rect.bottom - 12), 1)

    column_width = (rect.width - u.PAD * 2 - 24) // 2
    draw_column(screen, rect.x + u.PAD, line_y + 10, column_width, "NFL", nfl_games)
    draw_column(screen, rect.centerx + 12, line_y + 10, column_width, "NBA", nba_games)


def select():
    print("Sports selected")