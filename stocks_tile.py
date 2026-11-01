from datetime import datetime
from zoneinfo import ZoneInfo
import yfinance as yf
import pygame
import tile_utils as u

# (name shown on screen, Yahoo Finance symbol)
SYMBOLS = [
    ("AAPL", "AAPL"),
    ("NASDAQ", "^IXIC"),
    ("S&P 500", "^GSPC"),
    ("NVDA", "NVDA"),
]

stocks = None


def market_open():
    now = datetime.now(ZoneInfo("America/New_York"))
    if now.weekday() >= 5:  # Saturday or Sunday
        return False
    minutes = now.hour * 60 + now.minute
    return 9 * 60 + 30 <= minutes <= 16 * 60


def refresh_seconds():
    # Every 5 minutes while the market is open, otherwise once an hour
    return 300 if market_open() else 3600


def fetch():
    global stocks
    results = []
    for name, symbol in SYMBOLS:
        ticker = yf.Ticker(symbol)
        daily = ticker.history(period="5d", interval="1d")
        intraday = ticker.history(period="5d", interval="15m")

        closes = daily["Close"].tolist()
        last = closes[-1]
        previous = closes[-2]

        # Sparkline: only the most recent trading day
        last_day = intraday.index[-1].date()
        history = intraday[intraday.index.date == last_day]["Close"].tolist()

        results.append({
            "name": name,
            "price": last,
            "change": (last - previous) / previous * 100,
            "history": history,
        })
    stocks = results


def start():
    u.run_every(refresh_seconds, fetch, "stocks")


def draw_sparkline(screen, box, history, color):
    if len(history) < 2:
        return
    low = min(history)
    high = max(history)
    spread = (high - low) or 1
    step = box.width / (len(history) - 1)
    points = []
    for i, value in enumerate(history):
        x = box.x + i * step
        y = box.bottom - (value - low) / spread * box.height
        points.append((x, y))
    pygame.draw.lines(screen, color, False, points, 2)


def draw(screen, rect):
    u.title(screen, rect, "Stocks")
    if stocks is None:
        u.message(screen, rect, "Loading...")
        return

    y = rect.y + 56
    for stock in stocks:
        color = u.UP_COLOR if stock["change"] >= 0 else u.DOWN_COLOR
        draw_sparkline(screen, pygame.Rect(rect.x + u.PAD, y + 2, 36, 18), stock["history"], color)
        u.text(screen, stock["name"], 24, u.TEXT, (rect.x + 62, y + 2))
        u.text(screen, f"{stock['change']:+.1f}%", 20, color, (rect.right - u.PAD, y + 4), align="right")
        y += 32

    if not market_open():
        u.text(screen, "Closed", 18, u.MUTED, (rect.right - u.PAD, rect.y + 22), align="right")


def select():
    print("Stocks selected")