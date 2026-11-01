import io
import platform
import subprocess
import time
import requests
import pygame
import tile_utils as u

# Works with free Spotify: this talks to the Spotify desktop app on this Mac
# through AppleScript instead of using Spotify's developer API.

REFRESH_SECONDS = 2
SPLIT = "|~|"

song = None
status = "Loading..."
art_bytes = None
_art_url = None
_art_surface = None
_art_from = None

READ_SCRIPT = f'''
if application "Spotify" is running then
    tell application "Spotify"
        if player state is stopped then return "STOPPED"
        set t to current track
        return (name of t) & "{SPLIT}" & (artist of t) & "{SPLIT}" & (album of t) & "{SPLIT}" & (duration of t) & "{SPLIT}" & (player position) & "{SPLIT}" & (player state as string) & "{SPLIT}" & (artwork url of t)
    end tell
else
    return "NOT_RUNNING"
end if
'''


def osascript(script):
    result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True, timeout=5)
    return result.stdout.strip()


def fetch():
    global song, status, art_bytes, _art_url
    if platform.system() != "Darwin":
        status = "Spotify tile needs macOS"
        return

    output = osascript(READ_SCRIPT)
    if output == "NOT_RUNNING":
        song, status = None, "Open Spotify on this Mac"
        return
    if output == "STOPPED" or SPLIT not in output:
        song, status = None, "Nothing playing"
        return

    title, artist, album, duration_ms, position, state, art_url = output.split(SPLIT)
    song = {
        "title": title,
        "artist": artist,
        "album": album,
        "duration": int(float(duration_ms)) / 1000,
        "position": float(position.replace(",", ".")),
        "playing": state == "playing",
        "fetched_at": time.time(),
    }

    if art_url and art_url != _art_url:
        _art_url = art_url
        art_bytes = requests.get(art_url, timeout=10).content


def start():
    u.run_every(REFRESH_SECONDS, fetch, "spotify")


def draw_album_art(screen, box):
    global _art_surface, _art_from
    if art_bytes and art_bytes is not _art_from:
        image = pygame.image.load(io.BytesIO(art_bytes))
        _art_surface = pygame.transform.smoothscale(image, box.size)
        _art_from = art_bytes

    if song and _art_surface:
        screen.blit(_art_surface, box)
        return

    pygame.draw.rect(screen, u.INNER_BG, box, border_radius=12)
    cx, cy = box.centerx, box.centery
    pygame.draw.circle(screen, u.MUTED, (cx - 12, cy + 22), 12)
    pygame.draw.line(screen, u.MUTED, (cx - 1, cy + 22), (cx - 1, cy - 26), 4)
    pygame.draw.line(screen, u.MUTED, (cx - 1, cy - 26), (cx + 20, cy - 16), 4)


def draw_controls(screen, cx, cy, playing):
    # Previous
    pygame.draw.polygon(screen, u.TEXT, [(cx - 52, cy - 9), (cx - 52, cy + 9), (cx - 64, cy)])
    pygame.draw.polygon(screen, u.TEXT, [(cx - 64, cy - 9), (cx - 64, cy + 9), (cx - 76, cy)])
    # Play / pause
    if playing:
        pygame.draw.rect(screen, u.TEXT, pygame.Rect(cx - 9, cy - 11, 6, 22))
        pygame.draw.rect(screen, u.TEXT, pygame.Rect(cx + 3, cy - 11, 6, 22))
    else:
        pygame.draw.polygon(screen, u.TEXT, [(cx - 7, cy - 12), (cx - 7, cy + 12), (cx + 11, cy)])
    # Next
    pygame.draw.polygon(screen, u.TEXT, [(cx + 52, cy - 9), (cx + 52, cy + 9), (cx + 64, cy)])
    pygame.draw.polygon(screen, u.TEXT, [(cx + 64, cy - 9), (cx + 64, cy + 9), (cx + 76, cy)])


def time_text(seconds):
    seconds = int(seconds)
    return f"{seconds // 60}:{seconds % 60:02d}"


def draw(screen, rect):
    art = pygame.Rect(rect.x + u.PAD, rect.y + u.PAD, rect.height - u.PAD * 2, rect.height - u.PAD * 2)
    draw_album_art(screen, art)

    x = art.right + 20
    width = rect.right - u.PAD - x

    if song is None:
        u.text(screen, "Spotify", 30, u.TEXT, (x, rect.y + 22), bold=True)
        for i, line in enumerate(u.wrap(status, 22, width)[:3]):
            u.text(screen, line, 22, u.MUTED, (x, rect.y + 56 + i * 22))
        return

    u.text(screen, u.fit(song["title"], 30, width, bold=True), 30, u.TEXT, (x, rect.y + 22), bold=True)
    u.text(screen, u.fit(song["artist"], 24, width), 24, u.TEXT, (x, rect.y + 52))
    u.text(screen, u.fit(song["album"], 22, width), 22, u.MUTED, (x, rect.y + 76))

    # Between checks, keep the bar moving on our own so it looks smooth
    position = song["position"]
    if song["playing"]:
        position += time.time() - song["fetched_at"]
    position = min(position, song["duration"])

    bar_y = rect.y + 116
    filled = x + width * position / max(song["duration"], 1)
    pygame.draw.line(screen, u.INNER_BG, (x, bar_y), (x + width, bar_y), 4)
    pygame.draw.line(screen, u.ACCENT, (x, bar_y), (filled, bar_y), 4)
    pygame.draw.circle(screen, u.TEXT, (filled, bar_y), 6)
    u.text(screen, time_text(position), 18, u.MUTED, (x, bar_y + 8))
    u.text(screen, time_text(song["duration"]), 18, u.MUTED, (x + width, bar_y + 8), align="right")

    draw_controls(screen, x + width // 2, rect.bottom - 30, song["playing"])


def select():
    global song
    if song is None:
        return
    osascript('tell application "Spotify" to playpause')
    # Flip the icon right away instead of waiting for the next check
    song = dict(song, playing=not song["playing"], position=song["position"] + (time.time() - song["fetched_at"] if song["playing"] else 0), fetched_at=time.time())