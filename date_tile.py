import math
from datetime import datetime
import pygame
import tile_utils as u


def hand_end(cx, cy, length, degrees):
    # 0 degrees points straight up, like a real clock
    angle = math.radians(degrees)
    return (cx + length * math.sin(angle), cy - length * math.cos(angle))


def draw_clock(screen, cx, cy, radius, now):
    pygame.draw.circle(screen, u.INNER_BG, (cx, cy), radius)
    pygame.draw.circle(screen, u.TEXT, (cx, cy), radius, 3)

    for hour in range(12):
        outer = hand_end(cx, cy, radius - 5, hour * 30)
        inner = hand_end(cx, cy, radius - 11, hour * 30)
        pygame.draw.line(screen, u.MUTED, inner, outer, 2)

    hour_angle = (now.hour % 12 + now.minute / 60) * 30
    minute_angle = (now.minute + now.second / 60) * 6
    second_angle = now.second * 6

    pygame.draw.line(screen, u.TEXT, (cx, cy), hand_end(cx, cy, radius * 0.5, hour_angle), 5)
    pygame.draw.line(screen, u.TEXT, (cx, cy), hand_end(cx, cy, radius * 0.75, minute_angle), 3)
    pygame.draw.line(screen, u.DOWN_COLOR, (cx, cy), hand_end(cx, cy, radius * 0.85, second_angle), 1)
    pygame.draw.circle(screen, u.TEXT, (cx, cy), 4)


def draw(screen, rect):
    now = datetime.now()
    u.text(screen, now.strftime("%A"), 30, u.TEXT, (rect.x + u.PAD, rect.y + 14), bold=True)
    u.text(screen, now.strftime("%b %d"), 26, u.MUTED, (rect.x + u.PAD, rect.y + 40))
    draw_clock(screen, rect.centerx, rect.y + 126, 52, now)


def select():
    print("Date selected")