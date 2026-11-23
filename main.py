#!/usr/bin/env python3
"""The World in One Day — Monday 23 November 2026.

A pure-stdlib Python program that draws one 1024x1024 front page
summing up the day's world news and writes it to entry.png.

No network, no clock, no randomness: two runs write identical bytes.

Stories (Monday 23 November 2026):
  LEAD    Ukraine — Russian drone hits a flat block near Kyiv, 14 missing.
  SUMMIT  Shenzhen — Trump, Xi and Putin hold first-ever trilateral talks.
  GULF    Strait of Hormuz — tanker attacks at highest level since Sept.
  CLIMATE COP31 — final draft omits the words "fossil fuels"; no deal.
  JUSTICE The Hague — ICJ rules Myanmar committed genocide on Rohingya.
  STRIP   Lisbon marches; Indonesia factory fire; Iran hits Bahrain;
          US stocks fall; Nvidia chip row; S Korea minister quits.
"""

import binascii
import math
import os
import struct
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- palette
PAPER = (247, 241, 222)
INK = (27, 27, 27)
NAVY = (20, 38, 74)
RED = (179, 39, 30)
GOLD = (201, 162, 39)
CREAM = (250, 246, 232)
GREY = (120, 120, 112)
SLATE = (91, 107, 140)
SLATE_LT = (128, 145, 178)
NIGHT = (22, 35, 63)
SEA = (31, 58, 95)
SKY = (176, 205, 228)
SAND = (232, 217, 168)
SEA_GULF = (46, 111, 142)
GREEN = (46, 125, 70)
ORANGE = (232, 116, 30)
FLAME = (245, 176, 46)
LIT = (255, 209, 102)
SKIN = (232, 188, 150)
SUIT_US = (30, 58, 110)
SUIT_CN = (168, 32, 32)
SUIT_RU = (70, 70, 78)

# ---------------------------------------------------------------- canvas
PIX = bytearray(W * H * 3)


def px(x, y, c):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        PIX[i], PIX[i + 1], PIX[i + 2] = c


def rect(x, y, w, h, c):
    x0, y0 = max(0, x), max(0, y)
    x1, y1 = min(W, x + w), min(H, y + h)
    for yy in range(y0, y1):
        base = (yy * W + x0) * 3
        for xx in range(x0, x1):
            i = base + (xx - x0) * 3
            PIX[i], PIX[i + 1], PIX[i + 2] = c


def hline(x0, x1, y, c):
    for x in range(max(0, x0), min(W, x1 + 1)):
        px(x, y, c)


def vline(x, y0, y1, c):
    for y in range(max(0, y0), min(H, y1 + 1)):
        px(x, y, c)


def line(x0, y0, x1, y1, c):
    dx = abs(x1 - x0)
    dy = -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    while True:
        px(x0, y0, c)
        if x0 == x1 and y0 == y1:
            return
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy


def disc(cx, cy, r, c):
    for yy in range(cy - r, cy + r + 1):
        for xx in range(cx - r, cx + r + 1):
            if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                px(xx, yy, c)


def ring(cx, cy, r, c):
    for a in range(360):
        px(int(cx + r * math.cos(math.radians(a))),
           int(cy + r * math.sin(math.radians(a))), c)


def triangle(x0, y0, x1, y1, x2, y2, c):
    ys = sorted([(y0, x0), (y1, x1), (y2, x2)])
    (ya, xa), (yb, xb), (yc, xc) = ys

    def interp(y, y_a, x_a, y_b, x_b):
        if y_b == y_a:
            return x_a
        return x_a + (x_b - x_a) * (y - y_a) / (y_b - y_a)

    for y in range(ya, yc + 1):
        if y < yb:
            xa_y = interp(y, ya, xa, yb, xb)
        else:
            xa_y = interp(y, yb, xb, yc, xc)
        xb_y = interp(y, ya, xa, yc, xc)
        lo, hi = sorted((int(xa_y), int(xb_y)))
        hline(lo, hi, y, c)


# ---------------------------------------------------------------- 5x7 font
# Each glyph: 7 rows of 5 cells, "1" = on.
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "+": ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
}


def text_width(s, scale):
    return len(s) * 6 * scale - scale


def draw_text(x, y, s, scale, c):
    s = s.upper()
    cx = x
    for ch in s:
        glyph = FONT.get(ch, FONT[" "])
        for row in range(7):
            bits = glyph[row]
            for col in range(5):
                if bits[col] == "1":
                    rect(cx + col * scale, y + row * scale, scale, scale, c)
        cx += 6 * scale
    return cx


def draw_text_centered(x0, x1, y, s, scale, c):
    w = text_width(s, scale)
    draw_text(x0 + (x1 - x0 - w) // 2, y, s, scale, c)


def wrap(s, max_chars):
    words = s.split()
    lines, cur = [], ""
    for w in words:
        nxt = (cur + " " + w).strip()
        if len(nxt) <= max_chars:
            cur = nxt
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_para(x, y, s, scale, c, max_chars, line_h=None):
    lines = wrap(s, max_chars)
    lh = line_h or (7 * scale + 4)
    for i, ln in enumerate(lines):
        draw_text(x, y + i * lh, ln, scale, c)
    return y + len(lines) * lh


# ---------------------------------------------------------------- scenes
def scene_lead(x, y, w, h):
    """Night over Kyiv: pale-lit skyline, drone streaks, burning ship."""
    rect(x, y, w, h, NIGHT)
    for sx, sy in [(30, 18), (90, 42), (150, 14), (230, 30), (300, 12),
                   (360, 44), (420, 20), (60, 70), (200, 62), (330, 66)]:
        px(x + sx, y + sy, CREAM)
        px(x + sx + 1, y + sy, CREAM)
    disc(x + 415, y + 30, 16, CREAM)
    disc(x + 408, y + 26, 14, NIGHT)
    # skyline: LIGHT silhouettes so they read against the night sky
    base = y + h - 58
    buildings = [(0, 70, 120), (70, 96, 150), (150, 60, 100), (215, 110, 168),
                 (300, 78, 130), (360, 96, 150), (420, 58, 96)]
    for bx, bw, bh in buildings:
        rect(x + bx, base - bh + 58, bw, bh, SLATE_LT)
        rect(x + bx, base - bh + 58, bw, 3, SLATE)
    # many lit windows
    for wx in range(8, w - 8, 16):
        for wy in range(base - 140, base, 18):
            if (wx * 7 + wy * 3) % 5 < 2:
                rect(x + wx, wy, 5, 6, LIT)
    # drone streaks
    line(x + 40, y + 96, x + 130, y + 60, CREAM)
    line(x + 130, y + 60, x + 150, y + 52, CREAM)
    disc(x + 152, y + 51, 3, CREAM)
    line(x + 250, y + 108, x + 330, y + 74, CREAM)
    line(x + 330, y + 74, x + 348, y + 66, CREAM)
    disc(x + 350, y + 65, 3, CREAM)
    # sea
    rect(x, y + h - 58, w, 58, SEA)
    for wx in range(6, w - 6, 26):
        hline(x + wx, x + wx + 12, y + h - 40, SLATE)
        hline(x + wx + 6, x + wx + 18, y + h - 22, SLATE)
    # cargo ship, burning
    sx, sy = x + 150, y + h - 58
    rect(sx, sy - 26, 220, 26, (90, 40, 36))
    rect(sx + 20, sy - 44, 60, 18, (70, 32, 30))
    rect(sx + 110, sy - 40, 70, 14, (70, 32, 30))
    rect(sx, sy - 26, 220, 4, RED)
    for fx, fr in [(180, 16), (205, 22), (235, 18), (265, 24), (300, 15)]:
        disc(sx + fx, sy - 34, fr, ORANGE)
        disc(sx + fx, sy - 30, fr - 6, FLAME)
    for sx2, sy2, sr in [(185, 78, 9), (210, 66, 11), (240, 72, 9),
                         (270, 64, 10), (300, 78, 8)]:
        disc(x + sx2, y + sy2, sr, GREY)


def figure(cx, top, suit):
    """A seated leader: big head + broad shoulders so the person reads."""
    r = 17
    disc(cx, top + r, r, SKIN)
    for yy in range(top + 2 * r - 4, top + 2 * r + 18):
        half = int(((yy - (top + 2 * r - 4)) ** 0.5) * 8)
        hline(cx - half, cx + half, yy, suit)
    rect(cx - 2, top + 2 * r + 2, 4, 12, CREAM)


def scene_summit(x, y, w, h):
    """Three flags, three leaders around a round table.

    Scene area is only ~96px tall: short flags up top, big figures
    below, table near the bottom so heads and shoulders stay visible.
    """
    rect(x, y, w, h, SKY)
    # US flag banner (short)
    rect(x + 28, y + 4, 64, 30, CREAM)
    for i in range(5):
        rect(x + 28, y + 4 + i * 6, 64, 3, RED)
    rect(x + 28, y + 4, 26, 14, NAVY)
    # China flag banner
    rect(x + w // 2 - 32, y + 4, 64, 30, RED)
    disc(x + w // 2 - 18, y + 16, 5, GOLD)
    for sx, sy in [(8, -6), (13, -1), (13, 5), (8, 9)]:
        disc(x + w // 2 + sx, y + 16 + sy, 2, GOLD)
    # Russia flag banner
    rect(x + w - 92, y + 4, 64, 30, CREAM)
    rect(x + w - 92, y + 14, 64, 10, (30, 90, 180))
    rect(x + w - 92, y + 24, 64, 10, RED)
    # leaders, large and low so the table does not hide them
    table_y = y + h - 22
    figure(x + 80, y + 36, SUIT_US)
    figure(x + w // 2, y + 36, SUIT_CN)
    figure(x + w - 80, y + 36, SUIT_RU)
    # round table
    rect(x + 20, table_y, w - 40, 8, (122, 82, 42))
    for cx, tag in [(80, "USA"), (w // 2, "CHN"), (w - 80, "RUS")]:
        draw_text_centered(x + cx - 20, x + cx + 20, table_y + 10, tag, 1, INK)


def scene_hormuz(x, y, w, h):
    """A tall-hulled tanker on the strait, missile arc, big burst.

    Scene area is only ~96px tall: keep every element inside it —
    sky 0..44, sea 44..96, hull 30 tall with a burst above the bow.
    """
    rect(x, y, w, h, SAND)
    rect(x, y + 44, w, h - 44, SEA_GULF)
    for wx in range(6, w - 6, 30):
        hline(x + wx, x + wx + 14, y + 62, CREAM)
        hline(x + wx + 8, x + wx + 22, y + 80, CREAM)
    # missile arc (dotted), peaks inside the sky band
    for t in range(0, 101, 4):
        mx = x + 30 + int(t * (w - 90) / 100)
        my = y + 40 - int(30 * (1 - ((t - 50) / 50) ** 2))
        disc(mx, my, 2, INK)
    # tanker: TALL hull, unmistakable, fully inside the scene
    tx, ty = x + 60, y + 88
    rect(tx, ty - 30, 300, 30, (38, 38, 44))
    rect(tx, ty - 30, 300, 5, RED)
    rect(tx + 10, ty - 44, 80, 14, (120, 40, 36))
    rect(tx + 120, ty - 40, 56, 10, (200, 200, 200))
    rect(tx + 200, ty - 44, 64, 14, (120, 40, 36))
    for i in range(5):
        rect(tx + 12 + i * 52, ty - 28, 44, 10,
             (201, 162, 39) if i % 2 else (232, 116, 30))
    # BIG burst above the bow, inside the sky band
    bx, by = tx + 320, ty - 48
    for r, c in [(22, ORANGE), (16, FLAME), (9, LIT)]:
        disc(bx, by, r, c)
    for dx, dy in [(-26, -6), (26, -10), (-6, -26), (10, 22), (-20, 16)]:
        triangle(bx + dx, by + dy, bx + dx + 8, by + dy + 5,
                 bx + dx + 2, by + dy + 9, ORANGE)


def scene_cop31(x, y, w, h):
    """Cracked globe, thermometer, FOSSIL FUELS crossed out.

    Scene area is only ~96px tall: small globe top-left, thermometer
    top-right, crossed-out words along the bottom clear of the globe.
    """
    rect(x, y, w, h, CREAM)
    gx, gy, gr = x + 64, y + 38, 26
    disc(gx, gy, gr, (52, 120, 190))
    disc(gx - 8, gy - 7, 9, GREEN)
    disc(gx + 9, gy + 9, 7, GREEN)
    disc(gx + 7, gy - 11, 5, GREEN)
    ring(gx, gy, gr, NAVY)
    line(gx - 5, gy - 25, gx + 1, gy - 6, INK)
    line(gx + 1, gy - 6, gx - 7, gy + 5, INK)
    line(gx - 7, gy + 5, gx + 4, gy + 17, INK)
    line(gx + 4, gy + 17, gx - 2, gy + 25, INK)
    # thermometer
    tx = x + w - 84
    rect(tx, y + 10, 14, 46, CREAM)
    rect(tx + 2, y + 12, 10, 44, RED)
    disc(tx + 7, y + 62, 12, RED)
    for i in range(4):
        hline(tx - 7, tx - 2, y + 16 + i * 11, INK)
    # crossed-out words along the bottom, clear of the globe
    ty = y + h - 26
    draw_text(x + 16, ty, "FOSSIL FUELS", 2, RED)
    line(x + 12, ty + 3, x + 12 + text_width("FOSSIL FUELS", 2), ty + 10, RED)
    line(x + 12, ty + 10, x + 12 + text_width("FOSSIL FUELS", 2), ty + 3, RED)
    draw_text(x + 180, ty, "NOT IN DRAFT", 1, INK)


def scene_icj(x, y, w, h):
    """Courthouse columns and the scales of justice.

    Scene area is only ~96px tall: shallow pediment, short columns,
    scales compact in the centre, all clear of the caption below.
    """
    rect(x, y, w, h, (226, 220, 200))
    triangle(x + 30, y + 6, x + w - 30, y + 6, x + w // 2, y + 28, NAVY)
    disc(x + w // 2, y + 17, 5, GOLD)
    for cx in [x + 60, x + 150, x + w - 170, x + w - 80]:
        rect(cx, y + 30, 14, 40, CREAM)
        rect(cx - 3, y + 28, 20, 4, NAVY)
        rect(cx - 3, y + 68, 20, 4, NAVY)
    sx, sy = x + w // 2, y + 52
    vline(sx, sy - 16, sy + 18, INK)
    hline(sx - 34, sx + 34, sy - 16, INK)
    disc(sx, sy - 19, 4, GOLD)
    line(sx - 34, sy - 16, sx - 24, sy + 4, INK)
    line(sx - 34, sy - 16, sx - 44, sy + 4, INK)
    triangle(sx - 46, sy + 4, sx - 22, sy + 4, sx - 34, sy + 13, GOLD)
    line(sx + 34, sy - 16, sx + 24, sy + 4, INK)
    line(sx + 34, sy - 16, sx + 44, sy + 4, INK)
    triangle(sx + 22, sy + 4, sx + 46, sy + 4, sx + 34, sy + 13, GOLD)
    rect(sx - 20, sy + 18, 40, 4, INK)


# ---------------------------------------------------------------- page
def panel(x, y, w, h, tag, title, caption, scene):
    rect(x, y, w, h, INK)
    rect(x + 2, y + 2, w - 4, h - 4, CREAM)
    rect(x + 2, y + 2, w - 4, 34, NAVY)
    draw_text(x + 12, y + 10, tag, 2, GOLD)
    draw_text(x + 12 + text_width(tag + "  ", 2), y + 10, title, 2, CREAM)
    scene(x + 8, y + 42, w - 16, h - 42 - 52)
    draw_para(x + 12, y + h - 48, caption, 2, INK, 40, line_h=18)


def main():
    rect(0, 0, W, H, PAPER)

    # ---- masthead
    rect(0, 0, W, 104, NAVY)
    draw_text_centered(0, W, 16, "THE WORLD IN ONE DAY", 5, CREAM)
    draw_text_centered(0, W, 62, "MONDAY 23 NOVEMBER 2026", 2, GOLD)
    rect(0, 104, W, 4, GOLD)

    # ---- lead story
    rect(12, 116, 1000, 282, INK)
    rect(14, 118, 996, 278, CREAM)
    draw_text(28, 128, "DRONE HITS KYIV FLATS", 4, RED)
    draw_text(28, 162, "14 MISSING IN RUBBLE", 4, INK)
    scene_lead(24, 200, 470, 188)
    draw_para(514, 206, "A RUSSIAN DRONE STRUCK A FIVE-STOREY BLOCK IN "
              "DYMER, NORTH OF KYIV. TWO KILLED, AT LEAST 14 MISSING "
              "UNDER THE RUBBLE, ZELENSKIY SAYS. A RUSSIAN CARGO SHIP "
              "STILL BURNS OFF FINLAND AFTER AN ATTACK.", 2, INK, 38)

    # ---- 2x2 grid
    panel(12, 408, 490, 190, "SUMMIT", "SHENZHEN",
          "TRUMP, XI AND PUTIN MEET FOR THE FIRST TIME - "
          "'A NUCLEAR WAR CANNOT BE WON'", scene_summit)
    panel(522, 408, 490, 190, "GULF", "TANKERS UNDER FIRE",
          "ATTACKS IN THE STRAIT AT THE HIGHEST LEVEL "
          "SINCE SEPTEMBER", scene_hormuz)
    panel(12, 606, 490, 190, "CLIMATE", "COP31 ENDS IN DISARRAY",
          "FINAL DRAFT OMITS THE WORDS 'FOSSIL FUELS' "
          "ENTIRELY - NO DEAL", scene_cop31)
    panel(522, 606, 490, 190, "JUSTICE", "GENOCIDE VERDICT",
          "ICJ RULES MYANMAR COMMITTED GENOCIDE AGAINST "
          "THE ROHINGYA", scene_icj)

    # ---- also-today strip
    rect(12, 806, 1000, 142, NAVY)
    draw_text(28, 818, "ALSO TODAY", 2, GOLD)
    strip = [
        "LISBON MARCHES OVER LIVING COSTS",
        "INDONESIA FACTORY FIRE: 7 DEAD",
        "IRAN STRIKES BAHRAIN SITE",
        "US STOCKS FALL INTO CORRECTION",
        "NVIDIA CHIP-DIVERSION ROW",
        "S KOREA MINISTER QUITS IN AI SCANDAL",
    ]
    for i, item in enumerate(strip):
        col = i % 2
        row = i // 2
        sx = 28 + col * 500
        sy = 846 + row * 32
        draw_text(sx, sy, ">", 2, GOLD)
        draw_para(sx + 22, sy, item, 2, CREAM, 36, line_h=18)

    # ---- footer
    draw_text_centered(0, W, 966, "THE WORLD IN ONE DAY - MONDAY 23 NOVEMBER 2026", 2, INK)
    draw_text_centered(0, W, 992, "ONE IMAGE. THE WHOLE DAY.", 1, GREY)

    # ---- write PNG
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    for name in os.listdir(out_dir):
        p = os.path.join(out_dir, name)
        if os.path.isfile(p):
            os.remove(p)
    raw = bytearray()
    for yy in range(H):
        raw.append(0)
        raw.extend(PIX[yy * W * 3:(yy + 1) * W * 3])
    comp = zlib.compress(bytes(raw), 9)

    def chunk(kind, data):
        c = struct.pack(">I", len(data)) + kind + data
        return c + struct.pack(">I", binascii.crc32(kind + data) & 0xFFFFFFFF)

    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", comp)
    png += chunk(b"IEND", b"")
    with open(os.path.join(out_dir, "entry.png"), "wb") as f:
        f.write(png)


if __name__ == "__main__":
    main()
