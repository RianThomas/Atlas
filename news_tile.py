import webbrowser
import requests
import feedparser
import pygame
import tile_utils as u

# AP's own Flipboard feed first, Google News (AP stories only) as a backup
FEEDS = [
    "https://flipboard.com/@associatedpress/top-stories-u7govdf1z.rss",
    "https://news.google.com/rss/search?q=when:24h+site:apnews.com&hl=en-US&gl=US&ceid=US:en",
]

REFRESH_SECONDS = 1200  # 20 minutes
SECONDS_PER_HEADLINE = 8

headlines = None


def clean(title):
    # Google News adds " - AP News" to the end of every title
    for ending in (" - AP News", " - The Associated Press"):
        if title.endswith(ending):
            title = title[: -len(ending)]
    return title.strip()


def fetch():
    global headlines
    for url in FEEDS:
        try:
            response = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
            response.raise_for_status()
        except requests.RequestException as e:
            print("[news] feed failed, trying the next one:", e)
            continue
        feed = feedparser.parse(response.content)
        found = []
        for entry in feed.entries[:10]:
            if entry.get("title"):
                found.append({"title": clean(entry.title), "link": entry.get("link", "")})
        if found:
            headlines = found
            return
    raise Exception("no headlines from any feed")


def start():
    u.run_every(REFRESH_SECONDS, fetch, "news")


def current_index():
    return (pygame.time.get_ticks() // (SECONDS_PER_HEADLINE * 1000)) % len(headlines)


def draw(screen, rect):
    u.title(screen, rect, "News")
    if not headlines:
        u.message(screen, rect, "Loading...")
        return

    index = current_index()
    lines = u.wrap(headlines[index]["title"], 28, rect.width - u.PAD * 2)
    if len(lines) > 3:
        lines = lines[:3]
        lines[2] = u.fit(lines[2] + " ...", 28, rect.width - u.PAD * 2)
    y = rect.y + 56
    for line in lines:
        u.text(screen, line, 28, u.TEXT, (rect.x + u.PAD, y))
        y += 26

    u.text(screen, "AP News", 20, u.MUTED, (rect.x + u.PAD, rect.bottom - 30))

    # One dot per headline, the current one lit up
    count = len(headlines)
    for i in range(count):
        color = u.ACCENT if i == index else u.MUTED
        x = rect.right - u.PAD - 6 - (count - 1 - i) * 14
        pygame.draw.circle(screen, color, (x, rect.bottom - 23), 4)


def select():
    # Opens the headline that's showing right now
    if headlines:
        link = headlines[current_index()]["link"]
        if link:
            webbrowser.open(link)