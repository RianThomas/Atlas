import math
import pygame
import tile_utils as u


def draw_mic(screen, cx, cy):
    pygame.draw.rect(screen, u.TEXT, pygame.Rect(cx - 13, cy - 38, 26, 48), border_radius=13)
    pygame.draw.arc(screen, u.TEXT, pygame.Rect(cx - 23, cy - 26, 46, 46), math.pi, 2 * math.pi, 3)
    pygame.draw.line(screen, u.TEXT, (cx, cy + 20), (cx, cy + 32), 3)
    pygame.draw.line(screen, u.TEXT, (cx - 14, cy + 32), (cx + 14, cy + 32), 3)


def draw(screen, rect):
    draw_mic(screen, rect.centerx, rect.y + 72)
    u.text(screen, "AI Assistant", 26, u.TEXT, (rect.centerx, rect.bottom - 56), bold=True, align="center")
    u.text(screen, "Press to talk", 20, u.MUTED, (rect.centerx, rect.bottom - 32), align="center")


def select():
    print("AI Assistant selected")