import subprocess
import pygame
import tile_utils as u

# Drop a PNG with this name next to this file to use it as the icon
ICON_FILE = "vscode.png"


def draw(screen, rect):
    icon = u.load_icon(ICON_FILE, 72)
    if icon:
        screen.blit(icon, icon.get_rect(center=(rect.centerx, rect.y + 72)))
    else:
        u.text(screen, "</>", 64, u.TEXT, (rect.centerx, rect.y + 48), bold=True, align="center")
    u.text(screen, "VS Code", 26, u.TEXT, (rect.centerx, rect.bottom - 56), bold=True, align="center")
    u.text(screen, "Open app", 20, u.MUTED, (rect.centerx, rect.bottom - 32), align="center")


def select():
    result = subprocess.run(["open", "-a", "Visual Studio Code"], capture_output=True)
    if result.returncode != 0:
        print("Couldn't find VS Code in Applications")