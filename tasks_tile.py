import webbrowser
from googleapiclient.discovery import build
import pygame
import tile_utils as u
import google_auth

REFRESH_SECONDS = 120  # 2 minutes

tasks = None   # list of task titles once loaded
status = "Loading..."


def fetch():
    global tasks, status
    creds = google_auth.get_creds()
    if creds is None:
        status = "Not signed in. Run google_auth.py once."
        return
    service = build("tasks", "v1", credentials=creds, cache_discovery=False)
    result = service.tasks().list(tasklist="@default", showCompleted=False, maxResults=20).execute()
    items = result.get("items", [])
    items.sort(key=lambda item: item.get("position", ""))  # same order as the Google Tasks app
    tasks = [item["title"] for item in items if item.get("title")]


def start():
    u.run_every(REFRESH_SECONDS, fetch, "tasks")


def draw(screen, rect):
    u.title(screen, rect, "Tasks")
    if tasks is None:
        u.message(screen, rect, status)
        return
    if not tasks:
        u.message(screen, rect, "All caught up!")
        return

    if len(tasks) > 3:
        u.text(screen, f"+{len(tasks) - 3} more", 18, u.MUTED, (rect.right - u.PAD, rect.y + 22), align="right")

    y = rect.y + 52
    for title in tasks[:3]:
        row = pygame.Rect(rect.x + u.PAD, y, rect.width - u.PAD * 2, 36)
        pygame.draw.rect(screen, u.INNER_BG, row, border_radius=18)
        pygame.draw.circle(screen, u.TEXT, (row.x + 20, row.centery), 8, 2)
        words = u.fit(title, 24, row.width - 52)
        u.text(screen, words, 24, u.TEXT, (row.x + 38, row.y + 10))
        y += 44


def select():
    webbrowser.open("https://tasks.google.com")