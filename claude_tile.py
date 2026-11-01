import subprocess
import webbrowser
import pygame
import tile_utils as u

# Drop a PNG with this name next to this file to use it as the icon
ICON_FILE = "claude.png"


def draw_chat_bubble(screen, cx, cy):
    bubble = pygame.Rect(cx - 34, cy - 26, 68, 46)
    pygame.draw.rect(screen, u.TEXT, bubble, border_radius=14)
    pygame.draw.polygon(screen, u.TEXT, [(cx - 18, cy + 18), (cx - 4, cy + 18), (cx - 22, cy + 32)])
    for dx in (-16, 0, 16):
        pygame.draw.circle(screen, u.TILE_BG, (cx + dx, cy - 3), 5)


def draw(screen, rect):
    icon = u.load_icon(ICON_FILE, 72)
    if icon:
        screen.blit(icon, icon.get_rect(center=(rect.centerx, rect.y + 72)))
    else:
        draw_chat_bubble(screen, rect.centerx, rect.y + 72)
    u.text(screen, "Claude", 26, u.TEXT, (rect.centerx, rect.bottom - 56), bold=True, align="center")
    u.text(screen, "Open app", 20, u.MUTED, (rect.centerx, rect.bottom - 32), align="center")


def select():
    # Opens the Claude desktop app; falls back to claude.ai if it isn't installed
    result = subprocess.run(["open", "-a", "Claude"], capture_output=True)
    if result.returncode != 0:
        webbrowser.open("https://claude.ai")