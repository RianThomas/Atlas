import pygame
import controller as c
import tile_utils as u

import stocks_tile
import sports_tile
import weather_tile
import date_tile
import gmail_tile
import news_tile
import tasks_tile
import ai_tile
import claude_tile
import vscode_tile
import spotify_tile

pygame.init()

screen = pygame.display.set_mode((1024, 600), pygame.FULLSCREEN | pygame.SCALED)
pygame.mouse.set_visible(False)
clock = pygame.time.Clock()
running = True
BG = "gray25"

# TILES
stocks = pygame.Rect(20, 5, 190, 190)
sports = pygame.Rect(230, 5, 360, 190)
weather = pygame.Rect(610, 5, 180, 190)
date = pygame.Rect(810, 5, 190, 190)
gmail_auto = pygame.Rect(20, 205, 190, 190)
news = pygame.Rect(230, 205, 360, 190)
tasks = pygame.Rect(610, 205, 390, 190)
ai_auto = pygame.Rect(20, 405, 190, 190)
claude_auto = pygame.Rect(230, 405, 170, 190)
vscode_auto = pygame.Rect(420, 405, 170, 190)
spotify = pygame.Rect(610, 405, 390, 190)

# Each tile: its rectangle and the file that draws it
tiles = {
    "stocks": (stocks, stocks_tile),
    "sports": (sports, sports_tile),
    "weather": (weather, weather_tile),
    "date": (date, date_tile),
    "gmail_auto": (gmail_auto, gmail_tile),
    "news": (news, news_tile),
    "tasks": (tasks, tasks_tile),
    "ai_auto": (ai_auto, ai_tile),
    "claude_auto": (claude_auto, claude_tile),
    "vscode_auto": (vscode_auto, vscode_tile),
    "spotify": (spotify, spotify_tile),
}

# NAVIGATION
neighbors = {
    "stocks":      {"right": "sports",      "down": "gmail_auto"},
    "sports":      {"left": "stocks",       "right": "weather",     "down": "news"},
    "weather":     {"left": "sports",       "right": "date",        "down": "tasks"},
    "date":        {"left": "weather",      "down": "tasks"},
    "gmail_auto":  {"right": "news",        "up": "stocks",         "down": "ai_auto"},
    "news":        {"left": "gmail_auto",   "right": "tasks",       "up": "sports",   "down": "claude_auto"},
    "tasks":       {"left": "news",         "up": "weather",        "down": "spotify"},
    "ai_auto":     {"right": "claude_auto", "up": "gmail_auto"},
    "claude_auto": {"left": "ai_auto",      "right": "vscode_auto", "up": "news"},
    "vscode_auto": {"left": "claude_auto",  "right": "spotify",     "up": "news"},
    "spotify":     {"left": "vscode_auto",  "up": "tasks"},
}

c.start("/dev/cu.usbmodem1133301")

# Start the background data fetchers for tiles that have one
for rect, tile in tiles.values():
    if hasattr(tile, "start"):
        tile.start()

KEYMAP = {pygame.K_UP: "UP",
          pygame.K_DOWN: "DOWN",
          pygame.K_LEFT: "LEFT",
          pygame.K_RIGHT: "RIGHT",
          pygame.K_RETURN: "SELECT",
          pygame.K_ESCAPE: "BACK"}

focused = "stocks"

def handle(cmd):
    global focused
    direction = cmd.lower()
    if direction in ("up", "down", "left", "right"):
        focused = neighbors[focused].get(direction, focused)
    elif cmd == "SELECT":
        rect, tile = tiles[focused]
        tile.select()
    elif cmd == "BACK":
        print("Back")

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_q:
            running = False
        if event.type == pygame.KEYDOWN and event.key in KEYMAP:
            handle(KEYMAP[event.key])
    for cmd in c.get_events():
        handle(cmd)

    screen.fill(BG)
    for name, (rect, tile) in tiles.items():
        u.draw_box(screen, rect)
        tile.draw(screen, rect)
        if name == focused:
            u.draw_focus(screen, rect)

    # flip() the display to put your work on screen
    pygame.display.flip()

    clock.tick(30)  # 30 FPS is plenty for a dashboard

pygame.quit()