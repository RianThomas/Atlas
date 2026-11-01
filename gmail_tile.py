import os
import webbrowser
from datetime import date, datetime, timedelta
import requests
from dotenv import load_dotenv
from icalendar import Calendar
from googleapiclient.discovery import build
import pygame
import tile_utils as u
import google_auth

load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))
SCHOOLOGY_URL = os.getenv("SCHOOLOGY_ICAL_URL")

GMAIL_REFRESH = 180       # 3 minutes
SCHOOLOGY_REFRESH = 1800  # 30 minutes

gmail = None
schoology = None


def fetch_gmail():
    global gmail
    creds = google_auth.get_creds()
    if creds is None:
        gmail = {"count": 0, "detail": "run google_auth.py"}
        return
    service = build("gmail", "v1", credentials=creds, cache_discovery=False)
    inbox = service.users().labels().get(userId="me", id="INBOX").execute()
    gmail = {"count": inbox.get("messagesUnread", 0), "detail": "unread"}


def fetch_schoology():
    global schoology
    if not SCHOOLOGY_URL:
        schoology = {"count": 0, "detail": "add link to .env", "next": ""}
        return
    url = SCHOOLOGY_URL.replace("webcal://", "https://")
    response = requests.get(url, timeout=15)
    response.raise_for_status()
    calendar = Calendar.from_ical(response.content)

    today = date.today()
    week_from_now = today + timedelta(days=7)
    upcoming = []
    for event in calendar.walk("VEVENT"):
        start = event.get("DTSTART")
        if start is None:
            continue
        day = start.dt
        if isinstance(day, datetime):
            day = day.astimezone().date() if day.tzinfo else day.date()
        if today <= day <= week_from_now:
            upcoming.append((day, str(event.get("SUMMARY", ""))))
    upcoming.sort()

    schoology = {
        "count": len(upcoming),
        "detail": "due this week",
        "next": upcoming[0][1] if upcoming else "Nothing due this week",
    }


def start():
    u.run_every(GMAIL_REFRESH, fetch_gmail, "gmail")
    u.run_every(SCHOOLOGY_REFRESH, fetch_schoology, "schoology")


def draw_row(screen, rect, y, name, info):
    u.text(screen, name, 24, u.TEXT, (rect.x + u.PAD, y))
    detail = info["detail"] if info else "loading..."
    u.text(screen, detail, 18, u.MUTED, (rect.x + u.PAD, y + 20))
    if info and info["count"] > 0:
        count = str(info["count"]) if info["count"] < 100 else "99+"
        center = (rect.right - u.PAD - 14, y + 16)
        pygame.draw.circle(screen, u.DOWN_COLOR, center, 14)
        u.text(screen, count, 20, u.TEXT, (center[0], center[1] - 7), bold=True, align="center")


def draw(screen, rect):
    u.title(screen, rect, "Inbox")
    draw_row(screen, rect, rect.y + 54, "Gmail", gmail)
    draw_row(screen, rect, rect.y + 96, "Schoology", schoology)
    if schoology and schoology["next"]:
        u.text(screen, "Next:", 18, u.MUTED, (rect.x + u.PAD, rect.y + 142))
        words = u.fit(schoology["next"], 20, rect.width - u.PAD * 2)
        u.text(screen, words, 20, u.TEXT, (rect.x + u.PAD, rect.y + 160))


def select():
    webbrowser.open("https://mail.google.com")