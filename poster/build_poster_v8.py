#!/usr/bin/env python3
"""v8 poster builder for make.fun news-image-20261120.
Fresh build from the owner's replication-recipe prompt (rank-1 skeleton,
rank-2 lead order, exact recipe wording/numbers). PIL only, deterministic.
Output: poster/entry_v8.png (1024x1024, <= 1 MiB).
"""
import math
import os
import random

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
M = 14  # side margin
CW = W - 2 * M  # 996 content width
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry_v8.png")

# ---- palette (cream / navy / red, like the top entries) ----
CREAM = (247, 241, 227)
PAPER = (250, 246, 236)
INK = (26, 26, 26)
NAVY = (20, 33, 61)
NAVY2 = (27, 44, 74)
RED = (176, 30, 36)
RED_DK = (140, 22, 28)
GOLD = (201, 162, 39)
TAN = (216, 201, 163)
TAN_DK = (198, 178, 132)
TEAL = (31, 120, 110)
AMBER = (198, 124, 24)
BROWN = (122, 84, 52)
PURPLE = (104, 78, 140)
SLATE = (90, 100, 112)
WHITE = (255, 255, 255)
SKY = (126, 180, 210)
BLUE = (52, 110, 180)
GREEN = (46, 130, 80)
GREY = (120, 116, 108)
RULE = (26, 26, 26)

FONT_DIR = "/usr/share/fonts/truetype/liberation"


def font(name, size):
    path = os.path.join(FONT_DIR, name)
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.load_default()


SERIF_B = lambda s: font("LiberationSerif-Bold.ttf", s)
SERIF = lambda s: font("LiberationSerif-Regular.ttf", s)
SERIF_I = lambda s: font("LiberationSerif-Italic.ttf", s)
SANS = lambda s: font("LiberationSans-Regular.ttf", s)
SANS_B = lambda s: font("LiberationSans-Bold.ttf", s)
SANS_I = lambda s: font("LiberationSans-Italic.ttf", s)


def text_w(draw, text, fnt):
    return draw.textlength(text, font=fnt)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap; returns list of lines."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_wrapped(draw, x, y, text, fnt, color, max_w, leading, max_lines=None):
    lines = wrap(draw, text, fnt, max_w)
    if max_lines:
        lines = lines[:max_lines]
    for i, ln in enumerate(lines):
        draw.text((x, y + i * leading), ln, font=fnt, fill=color)
    return len(lines)


def draw_center(draw, cx, y, text, fnt, color):
    w = draw.textlength(text, font=fnt)
    draw.text((cx - w / 2, y), text, font=fnt, fill=color)


def hline(draw, x0, x1, y, color, width=1):
    draw.line([(x0, y), (x1, y)], fill=color, width=width)


def vline(draw, x, y0, y1, color, width=1):
    draw.line([(x, y0), (x, y1)], fill=color, width=width)


# ---- simplified coastline point lists (lon, lat) ----
NORTH_AMERICA = [(-168, 66), (-158, 58), (-152, 60), (-142, 60), (-135, 57),
                 (-130, 54), (-125, 48), (-124, 40), (-120, 34), (-114, 29),
                 (-109, 24), (-104, 20), (-97, 16), (-91, 14), (-86, 12),
                 (-82, 9), (-79, 8), (-77, 7), (-80, 9), (-83, 10), (-86, 13),
                 (-90, 14), (-93, 15), (-96, 16), (-97, 20), (-97, 25),
                 (-93, 29), (-89, 30), (-84, 30), (-81, 25), (-80, 32),
                 (-76, 35), (-74, 39), (-70, 42), (-67, 45), (-61, 46),
                 (-56, 48), (-60, 52), (-64, 56), (-60, 55), (-65, 58),
                 (-70, 60), (-76, 62), (-82, 64), (-88, 66), (-94, 68),
                 (-100, 69), (-110, 68), (-120, 69), (-130, 70), (-140, 70),
                 (-152, 71), (-162, 70), (-168, 66)]
GREENLAND = [(-44, 60), (-40, 64), (-32, 68), (-24, 70), (-20, 74), (-24, 78),
             (-34, 80), (-48, 79), (-56, 76), (-54, 71), (-52, 65), (-48, 61)]
SOUTH_AMERICA = [(-80, 9), (-77, 4), (-80, -3), (-81, -6), (-77, -11),
                 (-73, -16), (-70, -21), (-70, -28), (-72, -36), (-73, -43),
                 (-74, -49), (-70, -54), (-66, -55), (-67, -51), (-65, -44),
                 (-62, -39), (-58, -34), (-53, -32), (-48, -27), (-41, -23),
                 (-39, -17), (-35, -9), (-35, -6), (-40, -3), (-44, -2),
                 (-50, 0), (-53, 4), (-58, 6), (-62, 9), (-68, 11),
                 (-73, 12), (-77, 10), (-80, 9)]
AFRICA = [(-6, 35), (-10, 31), (-15, 27), (-17, 21), (-17, 15), (-15, 11),
          (-12, 8), (-8, 5), (-4, 5), (2, 6), (6, 4), (9, 4), (9, 0),
          (12, -4), (13, -8), (13, -12), (12, -17), (14, -22), (16, -28),
          (18, -33), (20, -35), (26, -34), (28, -32), (32, -28), (35, -24),
          (36, -20), (40, -16), (40, -11), (42, -5), (44, -1), (48, 2),
          (51, 5), (51, 11), (46, 11), (43, 12), (40, 15), (38, 18),
          (37, 22), (35, 28), (33, 31), (30, 32), (25, 32), (20, 32),
          (15, 32), (10, 34), (5, 37), (0, 36), (-6, 35)]
EURASIA = [(-10, 36), (-9, 43), (-2, 44), (-2, 48), (0, 50), (3, 52), (7, 54),
           (8, 57), (11, 58), (15, 56), (19, 55), (23, 58), (27, 60),
           (30, 63), (30, 67), (35, 69), (42, 68), (48, 69), (55, 68),
           (62, 69), (69, 71), (76, 72), (83, 73), (90, 75), (97, 76),
           (104, 77), (111, 74), (118, 73), (125, 72), (132, 71), (139, 72),
           (146, 72), (153, 70), (159, 69), (162, 64), (159, 59), (156, 53),
           (152, 47), (147, 43), (142, 44), (140, 39), (136, 35), (132, 33),
           (129, 34), (126, 37), (124, 39), (122, 37), (120, 34), (117, 30),
           (114, 24), (110, 20), (107, 17), (104, 13), (101, 9), (99, 6),
           (102, 2), (104, 1), (101, 5), (98, 9), (95, 13), (92, 17),
           (90, 21), (87, 21), (84, 18), (81, 14), (78, 9), (76, 9),
           (74, 14), (72, 19), (69, 22), (66, 24), (62, 25), (58, 25),
           (54, 26), (50, 28), (46, 29), (42, 29), (38, 27), (36, 23),
           (35, 19), (36, 15), (39, 12), (42, 12), (45, 14), (48, 16),
           (52, 18), (56, 20), (59, 23), (57, 25), (54, 27), (51, 28),
           (48, 29), (45, 30), (42, 30), (39, 30), (36, 31), (33, 32),
           (30, 32), (27, 32), (24, 33), (21, 34), (18, 35), (15, 36),
           (12, 37), (9, 37), (6, 37), (3, 36), (0, 36), (-3, 36),
           (-6, 35), (-10, 36)]
AUSTRALIA = [(113, -22), (114, -30), (115, -35), (118, -35), (124, -33),
             (129, -32), (132, -32), (135, -35), (138, -35), (140, -38),
             (145, -38), (150, -37), (153, -32), (153, -27), (150, -23),
             (146, -19), (142, -15), (142, -11), (140, -17), (136, -15),
             (135, -12), (132, -12), (130, -13), (126, -14), (122, -17),
             (118, -20), (114, -21), (113, -22)]
UK = [(-5, 50), (-3, 53), (-5, 56), (-3, 58), (-1, 57), (0, 53), (1, 51),
      (-2, 50), (-5, 50)]
JAPAN = [(130, 31), (132, 33), (135, 34), (137, 35), (139, 36), (140, 38),
         (141, 40), (142, 42), (143, 44), (141, 45), (140, 42), (139, 39),
         (137, 37), (135, 35), (133, 34), (131, 32), (130, 31)]
NEW_ZEALAND = [(167, -45), (170, -42), (173, -40), (175, -38), (177, -38),
               (175, -40), (172, -43), (168, -46), (167, -45)]
MADAGASCAR = [(44, -16), (47, -15), (50, -16), (49, -20), (47, -24),
              (44, -25), (43, -21), (44, -16)]
SUMATRA = [(95, 5), (98, 2), (101, -2), (104, -4), (106, -6), (103, -5),
           (100, -1), (97, 3), (95, 5)]
BORNEO = [(109, 1), (111, 3), (114, 4), (117, 2), (118, -1), (116, -3),
          (113, -3), (110, 0), (109, 1)]
JAVA = [(105, -6), (108, -7), (111, -7), (114, -8), (114, -9), (110, -8),
        (106, -7), (105, -6)]
NEW_GUINEA = [(131, -1), (135, -2), (138, -4), (141, -5), (141, -8),
              (138, -8), (134, -7), (131, -4), (131, -1)]
ICELAND = [(-22, 64), (-18, 63), (-14, 64), (-16, 66), (-20, 66), (-22, 64)]
CONTINENTS = [NORTH_AMERICA, GREENLAND, SOUTH_AMERICA, AFRICA, EURASIA,
              AUSTRALIA, UK, JAPAN, NEW_ZEALAND, MADAGASCAR, SUMATRA,
              BORNEO, JAVA, NEW_GUINEA, ICELAND]

# pins: (number, lon, lat, is_lead) — Mercury (5) is the top-right SPACE badge
PINS = [(1, 30.5, 50.4, True), (2, 84.9, 19.3, True), (3, 139.7, 35.7, True),
        (4, 30.7, 36.9, False), (6, 4.4, 50.9, False), (7, 147.0, 28.0, False),
        (8, 116.4, 39.9, False), (9, 171.0, -41.3, False),
        (10, -89.2, 13.7, False), (11, -17.4, 14.7, False),
        (12, 12.5, 41.9, False), (13, 0.8, 40.5, False)]


# ---- art panels ----
def art_kyiv(draw, x, y, w, h):
    """Lead 1: night missile barrage over Kyiv skyline."""
    draw.rectangle([x, y, x + w, y + h], fill=NAVY)
    # stars
    rnd = random.Random(7)
    for _ in range(26):
        sx = x + rnd.randint(4, w - 4)
        sy = y + rnd.randint(4, int(h * 0.5))
        r = rnd.choice([1, 1, 2])
        draw.ellipse([sx - r, sy - r, sx + r, sy + r], fill=(200, 205, 220))
    # skyline silhouette
    base = y + h - 26
    bx = x + 6
    rnd2 = random.Random(11)
    while bx < x + w - 10:
        bw = rnd2.randint(14, 30)
        bh = rnd2.randint(14, 52)
        draw.rectangle([bx, base - bh, bx + bw, base + 26], fill=(10, 16, 32))
        # lit windows
        for wy in range(base - bh + 5, base - 2, 9):
            for wx in range(bx + 4, bx + bw - 3, 8):
                if rnd2.random() < 0.4:
                    draw.rectangle([wx, wy, wx + 2, wy + 3], fill=(255, 200, 90))
        bx += bw + 3
    draw.rectangle([x, base, x + w, y + h], fill=(12, 18, 36))
    # missile trails (diagonal, glowing)
    for (tx, ty, ln) in [(0.18, 0.30, 46), (0.42, 0.18, 58), (0.66, 0.26, 50),
                         (0.86, 0.14, 44)]:
        px, py = x + int(w * tx), y + int(h * ty)
        draw.line([(px, py), (px + ln, py + int(ln * 0.55))], fill=(255, 120, 60),
                  width=3)
        draw.line([(px, py), (px + ln, py + int(ln * 0.55))], fill=(255, 220, 150),
                  width=1)
        draw.ellipse([px - 4, py - 4, px + 4, py + 4], fill=(255, 230, 170))
        draw.ellipse([px + ln - 3, py + int(ln * 0.55) - 3,
                      px + ln + 3, py + int(ln * 0.55) + 3], fill=(255, 90, 40))
    # flames at impact
    for fx, fr in [(0.30, 9), (0.62, 7), (0.84, 8)]:
        cx, cy = x + int(w * fx), base - 2
        draw.polygon([(cx - fr, cy), (cx, cy - fr * 2), (cx + fr, cy)],
                     fill=(255, 150, 40))
        draw.polygon([(cx - fr // 2, cy), (cx, cy - fr), (cx + fr // 2, cy)],
                     fill=(255, 220, 110))
    # labels
    draw.text((x + 8, y + 8), "KYIV", font=SANS_B(30), fill=WHITE)
    draw.text((x + 8, y + 42), "MISSILE BARRAGE", font=SANS_B(15), fill=(255, 220, 150))
    draw.rectangle([x, y + h - 22, x + w, y + h], fill=RED)
    draw.text((x + 8, y + h - 19), "01:25 LOCAL  ·  3 BRIDGES HIT",
              font=SANS_B(12), fill=WHITE)


def art_akvan(draw, x, y, w, h):
    """Lead 2: cyclone spiral over the Bay of Bengal."""
    draw.rectangle([x, y, x + w, y + h], fill=(24, 90, 110))
    # sea bands
    for i, col in enumerate([(24, 90, 110), (28, 100, 120), (22, 82, 102)]):
        draw.rectangle([x, y + i * h // 3, x + w, y + (i + 1) * h // 3], fill=col)
    # coastline hint (Odisha, left) — a broader coastal wedge
    draw.polygon([(x, y + h), (x, y + int(h * 0.30)), (x + 52, y + int(h * 0.22)),
                  (x + 88, y + int(h * 0.38)), (x + 78, y + int(h * 0.62)),
                  (x + 60, y + h)], fill=(214, 190, 140))
    draw.text((x + 6, y + int(h * 0.58)), "GOPALPUR", font=SANS_B(10), fill=INK)
    draw.text((x + 6, y + int(h * 0.72)), "ODISHA, INDIA", font=SANS(9), fill=INK)
    # spiral (Archimedean, white) — sized to fit between header and red bar
    cx, cy = x + int(w * 0.64), y + int(h * 0.52)
    for turn in range(3):
        pts = []
        for t in range(0, 361, 6):
            a = math.radians(t + turn * 55)
            r = 6 + (t / 360.0) * 20 + turn * 2
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a) * 0.92))
        draw.line(pts, fill=(235, 244, 248), width=3)
    draw.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=(255, 240, 200))
    # Gopalpur landfall dot
    gx, gy = x + 62, y + int(h * 0.40)
    draw.ellipse([gx - 5, gy - 5, gx + 5, gy + 5], fill=RED)
    draw.ellipse([gx - 8, gy - 8, gx + 8, gy + 8], outline=WHITE, width=2)
    draw.line([(gx, gy), (cx - 18, cy + 8)], fill=WHITE, width=1)
    # labels
    draw.rectangle([x, y, x + w, y + 26], fill=NAVY)
    draw.text((x + 8, y + 5), "CYCLONE AKVAN", font=SANS_B(14), fill=WHITE)
    draw.text((x + w - 108, y + 6), "BAY OF BENGAL", font=SANS_B(9), fill=SKY)
    draw.rectangle([x, y + h - 24, x + w, y + h], fill=RED)
    draw.text((x + 8, y + h - 20), "LANDFALL 08:30 IST", font=SANS_B(13), fill=WHITE)
    draw.text((x + w - 132, y + h - 19), "70–80 KM/H AT COAST",
              font=SANS_B(10), fill=(255, 220, 150))


def art_markets(draw, x, y, w, h):
    """Lead 3: dark index table + falling line chart."""
    draw.rectangle([x, y, x + w, y + h], fill=NAVY)
    # falling line chart (left)
    chart_x0, chart_y0 = x + 10, y + 34
    chart_w, chart_h = 118, h - 62
    pts = []
    for i in range(9):
        px = chart_x0 + i * chart_w // 8
        py = chart_y0 + [4, 10, 8, 22, 30, 26, 44, 56, chart_h - 6][i]
        pts.append((px, py))
    draw.line(pts, fill=(255, 70, 60), width=3)
    for (px, py) in pts:
        draw.ellipse([px - 2, py - 2, px + 2, py + 2], fill=(255, 120, 100))
    # header
    draw.text((x + 8, y + 6), "AI SELL-OFF", font=SANS_B(20), fill=WHITE)
    draw.text((x + 8, y + 28), "ASIA · INTRADAY LOWS", font=SANS_B(10),
              fill=(255, 150, 130))
    # index table (right)
    rows = [("NIKKEI", "−4.9%"), ("KOSPI", "−5.4%"), ("TAIEX", "−6.8%"),
            ("HANG SENG", "−2.0%")]
    tx = x + 138
    ty = y + 34
    for i, (name, val) in enumerate(rows):
        ry = ty + i * 20
        draw.text((tx, ry), name, font=SANS_B(12), fill=(200, 205, 220))
        vw = draw.textlength(val, font=SANS_B(13))
        draw.text((x + w - 10 - vw, ry), val, font=SANS_B(13), fill=(255, 90, 80))
        if i < 3:
            draw.line([(tx, ry + 16), (x + w - 10, ry + 16)],
                      fill=(60, 70, 95), width=1)


def art_cop31(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(16, 84, 96))
    draw.ellipse([x + 10, y + 5, x + 42, y + 37], fill=BLUE)
    draw.ellipse([x + 15, y + 10, x + 26, y + 21], fill=GREEN)
    draw.ellipse([x + 27, y + 22, x + 38, y + 32], fill=GREEN)
    draw.rectangle([x + w - 62, y + 4, x + w - 8, y + 36], fill=RED)
    draw.text((x + w - 57, y + 7), "$120BN", font=SANS_B(11), fill=WHITE)
    draw.text((x + w - 57, y + 21), "GAP", font=SANS_B(11), fill=WHITE)


def art_mercury(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(12, 14, 26))
    rnd = random.Random(3)
    for _ in range(18):
        sx = x + rnd.randint(3, w - 3)
        sy = y + rnd.randint(3, h - 3)
        draw.ellipse([sx, sy, sx + 1, sy + 1], fill=(200, 200, 210))
    draw.ellipse([x + w - 44, y + 4, x + w - 8, y + 36], fill=(180, 178, 170))
    draw.ellipse([x + w - 36, y + 10, x + w - 28, y + 18], fill=(150, 148, 140))
    draw.ellipse([x + w - 24, y + 22, x + w - 16, y + 30], fill=(150, 148, 140))
    draw.text((x + 8, y + 10), "6BN MILES", font=SANS_B(14), fill=WHITE)


def art_flags(draw, x, y, w, h):
    """EU + UK flags, side by side."""
    draw.rectangle([x, y, x + w, y + h], fill=(232, 226, 210))
    # EU flag
    ex, ey, ew, eh = x + 8, y + 4, 78, 30
    draw.rectangle([ex, ey, ex + ew, ey + eh], fill=(0, 51, 153))
    for k in range(12):
        a = math.radians(k * 30 - 90)
        px = ex + ew / 2 + 12 * math.cos(a)
        py = ey + eh / 2 + 8 * math.sin(a)
        draw.ellipse([px - 1.5, py - 1.5, px + 1.5, py + 1.5], fill=(255, 204, 0))
    # UK flag (simplified)
    ux, uy, uw, uh = x + w - 86, y + 4, 78, 30
    draw.rectangle([ux, uy, ux + uw, uy + uh], fill=(1, 33, 105))
    draw.line([(ux, uy), (ux + uw, uy + uh)], fill=WHITE, width=5)
    draw.line([(ux + uw, uy), (ux, uy + uh)], fill=WHITE, width=5)
    draw.line([(ux, uy), (ux + uw, uy + uh)], fill=(200, 16, 46), width=2)
    draw.line([(ux + uw, uy), (ux, uy + uh)], fill=(200, 16, 46), width=2)
    draw.rectangle([ux + uw // 2 - 4, uy, ux + uw // 2 + 4, uy + uh], fill=WHITE)
    draw.rectangle([ux, uy + uh // 2 - 4, ux + uw, uy + uh // 2 + 4], fill=WHITE)
    draw.rectangle([ux + uw // 2 - 2, uy, ux + uw // 2 + 2, uy + uh],
                   fill=(200, 16, 46))
    draw.rectangle([ux, uy + uh // 2 - 2, ux + uw, uy + uh // 2 + 2],
                   fill=(200, 16, 46))


def art_cpi(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(238, 232, 216))
    # two bars, values written to the right of each bar
    draw.rectangle([x + 12, y + 8, x + 30, y + 20], fill=GREY)
    draw.text((x + 36, y + 8), "2.1%", font=SANS_B(11), fill=INK)
    draw.rectangle([x + 12, y + 24, x + 34, y + 36], fill=RED)
    draw.text((x + 40, y + 24), "2.2%", font=SANS_B(11), fill=RED_DK)
    draw.text((x + 96, y + 8), "CPI CORE", font=SANS_B(11), fill=INK)
    draw.text((x + 96, y + 24), "OCT · Y/Y", font=SANS(9), fill=GREY)


def art_rates(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=NAVY)
    draw.text((x + 10, y + 4), "3.50%  5Y", font=SANS_B(13), fill=WHITE)
    draw.line([(x + 10, y + 22), (x + w - 10, y + 22)], fill=(255, 90, 80), width=2)
    draw.text((x + 10, y + 25), "3.00%  1Y", font=SANS_B(13), fill=(255, 150, 130))


def art_cricket(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(30, 110, 70))
    draw.rectangle([x + 16, y + 6, x + 44, y + h - 6], fill=(222, 196, 140),
                   outline=(160, 130, 80), width=1)
    draw.ellipse([x + w - 44, y + 8, x + w - 20, y + 32], fill=RED)
    draw.text((x + 56, y + 8), "118", font=SANS_B(24), fill=WHITE)


def art_bukele(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(24, 60, 120))
    draw.rectangle([x + 12, y + 12, x + 52, y + h - 12], fill=(240, 240, 235))
    draw.rectangle([x + 20, y + 6, x + 44, y + 14], fill=RED)
    draw.line([(x + 18, y + 22), (x + 46, y + 22)], fill=GREY, width=1)
    draw.line([(x + 18, y + 28), (x + 46, y + 28)], fill=GREY, width=1)
    draw.text((x + 62, y + 10), "FEB 2027", font=SANS_B(16), fill=WHITE)


def art_boat(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(18, 80, 120))
    for i in range(2):
        wy = y + 22 + i * 7
        draw.arc([x + 6, wy, x + w - 6, wy + 9], 0, 180, fill=(140, 200, 230),
                 width=2)
    draw.polygon([(x + 60, y + 8), (x + 96, y + 8), (x + 88, y + 20),
                  (x + 68, y + 20)], fill=(120, 70, 40))
    draw.text((x + 8, y + 8), "YENNE", font=SANS_B(12), fill=WHITE)


def art_strike(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(240, 236, 224))
    for i, col in enumerate([(0, 146, 70), (255, 255, 255), (205, 33, 42)]):
        draw.rectangle([x + 10 + i * 14, y + 8, x + 22 + i * 14, y + 30], fill=col,
                       outline=(180, 175, 160))
    draw.text((x + 62, y + 10), "100 SQUARES", font=SANS_B(14), fill=RED_DK)


def art_pill(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(245, 240, 228))
    draw.ellipse([x + 10, y + 10, x + 66, y + 34], fill=(200, 60, 90))
    draw.ellipse([x + 38, y + 10, x + 66, y + 34], fill=(250, 250, 245))
    draw.ellipse([x + 10, y + 10, x + 66, y + 34], outline=(150, 40, 70), width=2)
    draw.text((x + 76, y + 10), "60.7%", font=SANS_B(18), fill=RED_DK)


# ---- map ----
def project(lon, lat, mx, my, mw, mh):
    """Equirectangular projection from the recipe."""
    px = mx + (lon + 180.0) * mw / 360.0
    py = my + (85.0 - lat) * mh / 145.0
    return px, py


def draw_map(draw, mx, my, mw, mh):
    draw.rectangle([mx, my, mx + mw, my + mh], fill=NAVY)
    for poly in CONTINENTS:
        pts = [project(lon, lat, mx, my, mw, mh) for lon, lat in poly]
        draw.polygon(pts, fill=TAN)
    # graticule hints
    for lon in range(-150, 181, 30):
        gx, _ = project(lon, 85, mx, my, mw, mh)
        draw.line([(gx, my), (gx, my + mh)], fill=(38, 52, 84), width=1)
    # pins 4-13 first, lead pins 1-3 last (on top)
    ordered = sorted(PINS, key=lambda p: (0 if not p[3] else 1, p[0]))
    for num, lon, lat, is_lead in ordered:
        px, py = project(lon, lat, mx, my, mw, mh)
        r = 10 if is_lead else 8
        if is_lead:
            draw.ellipse([px - r - 3, py - r - 3, px + r + 3, py + r + 3],
                         outline=GOLD, width=2)
        draw.ellipse([px - r, py - r, px + r, py + r], fill=RED,
                     outline=WHITE, width=1)
        tw = draw.textlength(str(num), font=SANS_B(9))
        draw.text((px - tw / 2, py - 6), str(num), font=SANS_B(9), fill=WHITE)
    # Mercury / SPACE badge, top-right corner
    bx, by = mx + mw - 66, my + 6
    draw.rounded_rectangle([bx, by, bx + 60, by + 20], radius=4, fill=NAVY2,
                           outline=GOLD, width=1)
    draw.ellipse([bx + 5, by + 5, bx + 15, by + 15], fill=RED, outline=WHITE)
    draw.text((bx + 9, by + 4), "5", font=SANS_B(9), fill=WHITE)
    draw.text((bx + 20, by + 4), "SPACE", font=SANS_B(9), fill=GOLD)


# ---- content (recipe wording, exactly as specified) ----
STRAP = ("Missiles hit Kyiv's bridges · Cyclone Akvan ashore in India · "
         "An AI sell-off sinks Asia · COP31 deadlocked on its final day")
STRIP = [
    ("3", "killed in Kyiv as three Dnipro bridges are hit"),
    ("300,000+", "evacuated in Odisha ahead of Cyclone Akvan"),
    ("−4.9%", "Nikkei at its intraday low in the AI sell-off"),
    ("$120bn", "adaptation-finance gap left open at COP31"),
    ("118", "Phillips' historic century vs India, Wellington"),
    ("8 yrs", "BepiColombo's journey to Mercury"),
]
REGIONS = [("EUROPE", "8", NAVY), ("AMERICAS", "7", RED),
           ("ASIA-PACIFIC", "9", TEAL), ("MIDEAST", "3", AMBER),
           ("AFRICA", "3", BROWN), ("OCEANIA", "4", PURPLE),
           ("WORLD / SPACE", "2", SLATE)]
LEADS = [
    dict(kicker="01 · KYIV, UKRAINE · WAR",
         headline="Missiles hit Kyiv's Dnipro bridges; three killed",
         body=("Overnight wave from 01:25 struck three Dnipro bridges "
               "(Podilsko-Voskresenskyi, Darnytskyi, Pivdennyi); power and "
               "water cut, ±15 hurt — the war's biggest bridge attack. "
               "(Reuters, Kyiv Independent)"),
         art=art_kyiv),
    dict(kicker="02 · ODISHA, INDIA · CYCLONE",
         headline="Cyclone Akvan comes ashore near Gopalpur",
         body=("Crossed the coast about 08:30 IST, weakened to 70–80 km/h, "
               "gusts 90; 300,000+ evacuated, 423 rescue teams, 9,341 "
               "shelters, no major damage by midday. (IMD, Reuters)"),
         art=art_akvan),
    dict(kicker="03 · SEOUL / TOKYO · MARKETS",
         headline="AI sell-off sinks Asia's markets",
         body=("Chip stocks led the fall after Wall Street dropped; Nikkei "
               "−4.9% and KOSPI −5.4% at intraday lows — Asia's worst week "
               "since 2020. (Reuters)"),
         art=art_markets),
]
FEATURES = [
    dict(kicker="04 · ANTALYA, TÜRKIYE · CLIMATE",
         headline="COP31 reaches its final day deadlocked",
         body=("Draft fossil-fuel phase-out text; $120bn adaptation gap "
               "stays open. (UN News, Reuters)"),
         art=art_cop31),
    dict(kicker="05 · MERCURY · SPACE",
         headline="BepiColombo reaches Mercury after 8 years",
         body=("ESA/JAXA craft ends a 6-billion-mile trip; orbit burn set "
               "for Saturday. (ESA, BBC)"),
         art=art_mercury),
    dict(kicker="06 · BRUSSELS · EUROPE",
         headline="Burnham holds first EU–UK reset summit",
         body=("Costa & von der Leyen host the UK PM; agrifood, carbon "
               "links eyed. (EU Council)"),
         art=art_flags),
    dict(kicker="07 · TOKYO · ECONOMY",
         headline="Japan core inflation quickens to 2.2%",
         body=("October core CPI up from 2.1%, fastest this year; December "
               "BoJ hike eyed. (Reuters)"),
         art=art_cpi),
    dict(kicker="08 · BEIJING · RATES",
         headline="China holds lending rates for 18th month",
         body=("1-yr LPR stays 3.0% and 5-yr 3.5%, exactly as expected. "
               "(PBOC, Reuters)"),
         art=art_rates),
    dict(kicker="09 · WELLINGTON · CRICKET",
         headline="Phillips makes history with 118",
         body=("First NZ batter with a century in three formats in a year. "
               "(ICC, AP)"),
         art=art_cricket),
    dict(kicker="10 · SAN SALVADOR · POLITICS",
         headline="Bukele registers for a third term",
         body=("Files with the tribunal for the February 2027 vote; rights "
               "groups object. (AP)"),
         art=art_bukele),
    dict(kicker="11 · SENEGAL · MIGRATION",
         headline="Migrant boat capsizes off Yenne; 4 dead",
         body=("Dozens missing from 50–100 aboard as Canary arrivals surge. "
               "(Al Jazeera)"),
         art=art_boat),
    dict(kicker="12 · ROME · LABOUR",
         headline="Italy's CGIL holds 24-hour general strike",
         body=("Union rallies in ±100 squares against the 2027 budget; "
               "transit hit. (CGIL, AFP)"),
         art=art_strike),
    dict(kicker="13 · BARCELONA · HEALTH",
         headline="Pancreatic-cancer pill shrinks tumours",
         body=("60.7% response in an early trial, vs 23–42% chemo alone. "
               "(Reuters)"),
         art=art_pill),
]
BRIEFS = [
    ("14", "SHENZHEN", "Trump, Xi & Putin publish a joint peace declaration a day after their summit", "AP"),
    ("15", "COX'S BAZAR", "Rohingya camps weep and pray after Thursday's ICJ genocide ruling", "Reuters"),
    ("16", "HORMUZ", "Four attacks on vessels in 96 hours; 48 ships wait as the strait stays shut", "UKMTO"),
    ("17", "GAZA", "Aid groups score the peace plan's implementation at 4 of 26 points", "UN News"),
    ("18", "SEOUL", "Ruling party adopts a bid to impeach Chief Justice Cho Hee-dae", "SBS"),
    ("19", "BLANTYRE", "Malawi fuel crisis: night queues and a 20-litre daily cap", "Al Jazeera"),
    ("20", "LAS VEGAS", "Russell fastest in wet F1 practice, 1:47.272", "Formula1.com"),
    ("21", "TONGA", "The Pacific kingdom declares an emergency as the El Niño drought bites", "RNZ"),
    ("22", "MATO GROSSO", "Lula meets Chief Raoni as Indigenous land is recognised in Brazil", "Al Jazeera"),
    ("23", "BOUGAINVILLE", "Rio Tinto pledges $370m for the Panguna mine's legacy", "Reuters"),
    ("24", "CANBERRA", "Budget office warns AUKUS submarine sales could shrink the US fleet", "Reuters"),
    ("25", "FLORIDA", "St Johns River hits a record 18.3 ft; four counties shut schools", "AP"),
    ("26", "IOWA", "US Army carries out a noon detonation of 68 unstable explosive barrels", "AP"),
    ("27", "WASHINGTON", "Pentagon puts the US war cost against Iran at $48.3bn", "Reuters"),
    ("28", "LONDON", "UK & Norway fund £100m+ for two Ukrainian naval vessels", "BBC"),
    ("29", "COPENHAGEN", "Denmark's parliament approves the Greenland defence bill", "AFP"),
    ("30", "JAKARTA", "Indonesia's parliament passes the asset-forfeiture bill", "Reuters"),
    ("31", "DOHA", "U17 World Cup: Australia stun Argentina 2–0", "FIFA"),
    ("32", "JOHANNESBURG", "Harmer spins the Proteas to a Test win as Bavuma sets a record", "ICC"),
    ("33", "HONG KONG", "Badminton World Tour reaches the semifinals", "BWF"),
    ("34", "TURIN", "Alcaraz–Cobolli and Medvedev–Tiafoe close the ATP Finals groups", "ATP"),
    ("35", "WORLD · GAMES", "GTA VI ends its first full day on sale with a Metacritic score of 99", ""),
    ("36", "GLOBAL", "The UN marks World Children's Day, 20 November, across member states", "UN News"),
]
DATE_CHECK = ("First reported Thursday 19 Nov, so NOT shown as Friday's news: "
              "the Trump–Xi–Putin Shenzhen summit itself · drone strike on "
              "the Dutch & Austrian embassies in Kyiv · Anthropic's Nasdaq "
              "debut · ICJ Rohingya genocide verdict · Senate 48–51 Iran "
              "war-powers vote · GTA VI midnight launch · $190.4m Van Gogh sale.")
FOOTER = ("Every story here happened, or was first reported, on Friday 20 "
          "November 2026 in at least one time zone. Sources: Reuters, AP, "
          "AFP, BBC, IMD, UN News, Al Jazeera, ICC, EU Council, PBOC. "
          "Original vector drawings.")


# ---- layout ----
def build():
    img = Image.new("RGB", (W, H), CREAM)
    draw = ImageDraw.Draw(img)

    # subtle deterministic paper grain (seeded) under all content
    rnd = random.Random(42)
    for _ in range(5200):
        gx = rnd.randint(0, W - 1)
        gy = rnd.randint(0, H - 1)
        d = rnd.choice([-5, -4, -3, 3, 4, 5])
        draw.point((gx, gy), fill=(CREAM[0] + d, CREAM[1] + d, CREAM[2] + d))

    # ---------- masthead ----------
    draw.text((M, 8), "THE WORLD IN ONE DAY", font=SANS_B(11), fill=RED)
    corner = "FRIDAY'S NEWS · ONE PAGE · 36 STORIES · 6 CONTINENTS"
    cw = draw.textlength(corner, font=SANS(10))
    draw.text((W - M - cw, 9), corner, font=SANS(10), fill=INK)
    draw_center(draw, W // 2, 20, "Friday 20 November 2026", SERIF_B(52), INK)
    draw_center(draw, W // 2, 78, STRAP, SERIF_I(15), RED)
    hline(draw, M, W - M, 96, RULE, 2)

    # ---------- strip of 6 ----------
    cell_w = CW / 6.0
    for i, (num, cap) in enumerate(STRIP):
        cx = M + i * cell_w
        draw.text((cx + 8, 102), num, font=SERIF_B(26), fill=RED)
        draw_wrapped(draw, cx + 8, 132, cap, SANS(9), INK, cell_w - 16, 11,
                     max_lines=2)
        if i:
            vline(draw, cx, 102, 144, (200, 192, 172), 1)
    hline(draw, M, W - M, 148, (200, 192, 172), 1)

    # ---------- region bar ----------
    rx, ry = M, 154
    for name, n, col in REGIONS:
        label = f"{name} {n}"
        tw = draw.textlength(label, font=SANS_B(10))
        draw.rectangle([rx, ry, rx + tw + 14, ry + 16], fill=col)
        draw.text((rx + 7, ry + 2), label, font=SANS_B(10), fill=WHITE)
        rx += tw + 14 + 4
    tail = "ALL STORIES: FRI 20 NOV 2026"
    tw = draw.textlength(tail, font=SANS(9))
    draw.text((W - M - tw, ry + 3), tail, font=SANS(9), fill=GREY)

    # ---------- 3 lead cards ----------
    lead_w, lead_gap = 324, 12
    for i, lead in enumerate(LEADS):
        lx = M + i * (lead_w + lead_gap)
        ly = 172
        draw.rectangle([lx, ly, lx + lead_w, 406], outline=(205, 196, 176),
                       width=1)
        lead["art"](draw, lx + 1, ly + 1, lead_w - 2, 112)
        ky = ly + 118
        draw.text((lx + 8, ky), lead["kicker"], font=SANS_B(10), fill=RED)
        hy = ky + 15
        hl = wrap(draw, lead["headline"], SERIF_B(19), lead_w - 16)
        for j, ln in enumerate(hl[:3]):
            draw.text((lx + 8, hy + j * 21), ln, font=SERIF_B(19), fill=INK)
        by = hy + len(hl[:3]) * 21 + 4
        draw_wrapped(draw, lx + 8, by, lead["body"], SANS(10), INK,
                     lead_w - 16, 12.5, max_lines=3)

    # ---------- 10 feature cards (2 rows x 5) ----------
    feat_w, feat_gap = 192, 9
    for row in range(2):
        fy = 412 + row * 110
        for col in range(5):
            f = FEATURES[row * 5 + col]
            fx = M + col * (feat_w + feat_gap)
            draw.rectangle([fx, fy, fx + feat_w, fy + 108],
                           outline=(205, 196, 176), width=1)
            f["art"](draw, fx + 1, fy + 1, feat_w - 2, 40)
            ky = fy + 44
            draw.text((fx + 6, ky), f["kicker"], font=SANS_B(9), fill=RED)
            hy = ky + 13
            hl = wrap(draw, f["headline"], SERIF_B(13), feat_w - 12)
            for j, ln in enumerate(hl[:2]):
                draw.text((fx + 6, hy + j * 14), ln, font=SERIF_B(13), fill=INK)
            by = hy + len(hl[:2]) * 14 + 2
            draw_wrapped(draw, fx + 6, by, f["body"], SANS(9), INK,
                         feat_w - 12, 10.5, max_lines=2)

    # ---------- map + briefs ----------
    band_y = 644
    # map panel
    draw.text((M, band_y + 4), "WHERE IT HAPPENED", font=SANS_B(11), fill=RED)
    draw.text((M, band_y + 18), "Pins 1–13 mark the drawn stories",
              font=SANS(8), fill=GREY)
    map_x, map_y, map_w, map_h = M, band_y + 36, 336, 168
    draw_map(draw, map_x, map_y, map_w, map_h)
    draw.text((M, band_y + 36 + 168 + 8), "1–3 Lead (gold ring) · 4–13 Features",
              font=SANS(8), fill=GREY)
    draw.text((M, band_y + 36 + 168 + 20), "Positions approximate.",
              font=SANS(8), fill=GREY)
    # briefs
    bx0, bx1 = 362, W - M
    draw.text((bx0, band_y + 4), "ALSO ON FRIDAY 20 NOVEMBER — 23 MORE STORIES",
              font=SANS_B(11), fill=RED)
    tail = "World Briefs (14–36)"
    tw = draw.textlength(tail, font=SANS(9))
    draw.text((bx1 - tw, band_y + 5), tail, font=SANS(9), fill=GREY)
    col_w = 317
    cols = [(bx0, BRIEFS[:11]), (bx0 + col_w + 14, BRIEFS[11:])]
    for cx, items in cols:
        cy = band_y + 24
        for num, place, text, src in items:
            prefix = f"{num} {place} — "
            full = prefix + text + (f" ({src})" if src else "")
            lines = wrap(draw, full, SANS(9), col_w)
            for j, ln in enumerate(lines[:2]):
                if j == 0:
                    # bold prefix, regular remainder
                    pw = draw.textlength(prefix, font=SANS_B(9))
                    draw.text((cx, cy), prefix, font=SANS_B(9), fill=RED_DK)
                    draw.text((cx + pw, cy), ln[len(prefix):], font=SANS(9),
                              fill=INK)
                else:
                    draw.text((cx, cy), ln, font=SANS(9), fill=INK)
                cy += 11
            cy += 1
            if cy > 928:
                print(f"WARNING: briefs overflow at {num} {place}")
    hline(draw, M, W - M, 930, (200, 192, 172), 1)

    # ---------- DATE CHECK ----------
    draw.rectangle([M, 936, W - M, 984], outline=RED, width=2, fill=PAPER)
    draw.text((M + 8, 940), "DATE CHECK", font=SANS_B(11), fill=RED)
    draw_wrapped(draw, M + 8, 954, DATE_CHECK, SANS(10), INK, CW - 16, 12,
                 max_lines=2)

    # ---------- footer ----------
    draw_wrapped(draw, M, 990, FOOTER, SANS(8), GREY, CW, 10, max_lines=2)

    return img


def main():
    img = build()
    img.save(OUT, format="PNG", optimize=True)
    print("saved", OUT, os.path.getsize(OUT), "bytes")


if __name__ == "__main__":
    main()
