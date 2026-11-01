import os
import threading
import time
import pygame

# COLORS
TILE_BG = "gray37"
INNER_BG = "gray30"
HIGHLIGHT = "green1"
TEXT = "white"
MUTED = "gray70"
UP_COLOR = "springgreen3"
DOWN_COLOR = "tomato"
ACCENT = "green1"

BORDER_RADIUS = 16
PAD = 16

_fonts = {}
_icons = {}


def font(size, bold=False):
    # Fonts are made the first time they're used, after pygame.init() has run
    key = (size, bold)
    if key not in _fonts:
        f = pygame.font.Font(None, size)
        f.set_bold(bold)
        _fonts[key] = f
    return _fonts[key]


def text(screen, words, size, color, pos, bold=False, align="left"):
    surf = font(size, bold).render(words, True, color)
    r = surf.get_rect()
    if align == "center":
        r.midtop = pos
    elif align == "right":
        r.topright = pos
    else:
        r.topleft = pos
    screen.blit(surf, r)
    return r


def title(screen, rect, words):
    return text(screen, words, 30, TEXT, (rect.x + PAD, rect.y + PAD), bold=True)


def fit(words, size, max_width, bold=False):
    # Cut text with "..." so it never runs past the tile
    if font(size, bold).size(words)[0] <= max_width:
        return words
    while words and font(size, bold).size(words + "...")[0] > max_width:
        words = words[:-1]
    return words + "..."


def wrap(words, size, max_width, bold=False):
    # Split text into lines that fit inside max_width
    lines = []
    line = ""
    for word in words.split():
        test = word if line == "" else line + " " + word
        if font(size, bold).size(test)[0] <= max_width:
            line = test
        else:
            lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines


def load_icon(filename, size):
    # Loads a PNG that sits next to this file. Returns None if it isn't there.
    key = (filename, size)
    if key not in _icons:
        path = os.path.join(os.path.dirname(__file__), filename)
        if os.path.exists(path):
            image = pygame.image.load(path).convert_alpha()
            _icons[key] = pygame.transform.smoothscale(image, (size, size))
        else:
            _icons[key] = None
    return _icons[key]


def run_every(seconds, job, name):
    # Runs job() over and over in a background thread so the screen never freezes.
    # seconds can be a number, or a function that returns a number.
    def loop():
        while True:
            try:
                job()
            except Exception as e:
                print(f"[{name}] error:", e)
            time.sleep(seconds() if callable(seconds) else seconds)
    threading.Thread(target=loop, daemon=True).start()


def message(screen, rect, words, y=56):
    # A gray note inside a tile, e.g. "Loading..." or a setup reminder
    for line in wrap(words, 22, rect.width - PAD * 2)[:4]:
        text(screen, line, 22, MUTED, (rect.x + PAD, rect.y + y))
        y += 22


def draw_box(screen, rect):
    pygame.draw.rect(screen, TILE_BG, rect, border_radius=BORDER_RADIUS)


def draw_focus(screen, rect):
    pygame.draw.rect(screen, HIGHLIGHT, rect, 4, border_radius=BORDER_RADIUS)