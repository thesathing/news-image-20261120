#!/usr/bin/env python3
"""Build poster v9 for make.fun news-image-20261120 (A+B+C combined).
Fresh generator, written from scratch. PIL only, deterministic.
Output: poster/entry_v9.png (1024x1024, <= 1,048,576 bytes).
"""
import hashlib
import math
import os
import textwrap

from PIL import Image, ImageDraw, ImageFont

WORK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(WORK, "poster", "entry_v9.png")

W, H = 1024, 1024
MARGIN = 14
CW = W - 2 * MARGIN  # 996

# ---------- palette ----------
CREAM = (245, 239, 224)      # paper
CREAM2 = (238, 231, 210)     # slightly darker paper
INK = (26, 26, 26)           # near-black text
NAVY = (26, 42, 74)          # dark navy
NAVY2 = (18, 30, 58)         # darker navy
RED = (185, 28, 28)          # headline red
RED2 = (220, 38, 38)
GOLD = (212, 175, 55)
TEAL = (13, 148, 136)
TEAL_DK = (8, 110, 100)
MUTED = (90, 90, 90)
LINE = (180, 170, 150)
LIGHT_MAP_BG = (246, 241, 228)
LAND = (216, 199, 163)       # tan land on light map
LAND2 = (206, 188, 150)
WHITE = (255, 255, 255)
GREEN_TAG = (22, 101, 52)    # CONFIRMED
BLUE_TAG = (30, 64, 175)     # OFFICIAL
GRAY_TAG = (87, 83, 78)      # REPORTED

# region colours (pins + legend)
REG_COL = {
    "EUROPE": (30, 64, 175),
    "ASIA-PACIFIC": (13, 148, 136),
    "AMERICAS": (220, 38, 38),
    "MIDEAST": (234, 88, 12),
    "AFRICA": (22, 163, 74),
    "OCEANIA": (124, 58, 237),
    "WORLD/SPACE": (120, 113, 108),
}

FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def f_serif(size, bold=False):
    name = "DejaVuSerif-Bold.ttf" if bold else "DejaVuSerif.ttf"
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


def f_sans(size, bold=False):
    name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


def text_w(draw, xy, s, font, fill, anchor="la"):
    draw.text(xy, s, font=font, fill=fill, anchor=anchor)


def wrap(s, font, max_w, draw):
    """Wrap s to lines fitting max_w pixels (greedy by words)."""
    words = s.split()
    lines, cur = [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=font) <= max_w:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def para(draw, x, y, s, font, fill, max_w, leading=3):
    """Draw wrapped paragraph, return y after last line."""
    for ln in wrap(s, font, max_w, draw):
        draw.text((x, y), ln, font=font, fill=fill)
        y += font.size + leading
    return y


def tag(draw, x, y, label, bg, font=None):
    """Small filled pill tag; returns width."""
    f = font or f_sans(8, bold=True)
    tw = draw.textlength(label, font=f)
    w = int(tw) + 10
    h = 13
    draw.rounded_rectangle([x, y, x + w, y + h], radius=6, fill=bg)
    draw.text((x + 5, y + 2), label, font=f, fill=WHITE)
    return w


# ---------- data ----------
UTC_SLOTS = [
    ("00:00", "Kyiv bridges hit"),
    ("02:00", "Akvan makes landfall"),
    ("05:30", "Taiwan ends \u22126.2%"),
    ("05:50", "Missile lands in Poland"),
    ("15:00", "COP31 runs past close"),
    ("19:10", "Report of Nvidia probe"),
    ("21:00", "S&P 500 ends \u22123.7%"),
]

STRIP = [
    ("9", "at least 9 killed in Kyiv; three bridges hit"),
    ("300,000+", "evacuated in Odisha ahead of Cyclone Akvan"),
    ("\u22124.9%", "Nikkei at its intraday low in the AI sell-off"),
    ("46", "ships waiting at Hormuz"),
    ("118", "Phillips' historic century vs India, Wellington"),
    ("0", "COP31 fossil-fuel mentions in the draft"),
]

REGIONS = [
    ("EUROPE", 8, (30, 64, 175)),
    ("AMERICAS", 6, (220, 38, 38)),
    ("ASIA-PACIFIC", 9, (13, 148, 136)),
    ("MIDEAST", 5, (234, 88, 12)),
    ("AFRICA", 2, (22, 163, 74)),
    ("OCEANIA", 4, (124, 58, 237)),
    ("WORLD/SPACE", 2, (120, 113, 108)),
]

LEADS = [
    {
        "num": "01",
        "kicker": "KYIV, UKRAINE \u00b7 WAR",
        "head": "Missiles hit Kyiv's Dnipro bridges; at least nine killed",
        "body": ("Overnight wave from 01:25 struck three Dnipro bridges "
                 "(Podilsko-Voskresenskyi, Darnytskyi, Pivdennyi); about 110 "
                 "missiles and 400 drones; power and water cut \u2014 the war's "
                 "biggest bridge attack. (Reuters, Kyiv Independent)"),
        "trust": ("CONFIRMED", GREEN_TAG),
    },
    {
        "num": "02",
        "kicker": "ODISHA, INDIA \u00b7 CYCLONE",
        "head": "Cyclone Akvan comes ashore near Gopalpur",
        "body": ("Crossed the coast about 08:30 IST, weakened to 70\u201380 km/h, "
                 "gusts 90; 300,000+ evacuated, 423 rescue teams, 9,341 shelters, "
                 "no major damage by midday. (IMD, Reuters)"),
        "trust": ("OFFICIAL", BLUE_TAG),
    },
    {
        "num": "03",
        "kicker": "SEOUL / TOKYO \u00b7 MARKETS",
        "head": "AI sell-off sinks Asia's markets",
        "body": ("Chip stocks led the fall after Wall Street dropped; Nikkei "
                 "\u22124.9% and KOSPI \u22125.4% at intraday lows \u2014 Asia's worst "
                 "week since 2020. (Reuters)"),
        "trust": ("CONFIRMED", GREEN_TAG),
    },
]

# features: (num, place, section, headline, body, trust(label,bg), art, source_tag)
FEATURES = [
    ("04", "ANTALYA, T\u00dcRKIYE", "CLIMATE",
     "COP31 reaches its final day deadlocked",
     ("Draft fossil-fuel phase-out text. $120bn adaptation gap stays open. "
      "[FORECAST] Talks may run into the weekend. (UN News)"),
     ("REPORTED", GRAY_TAG), "cop31", "Ongoing \u00b7 UN News"),
    ("05", "MERCURY", "SPACE",
     "BepiColombo reaches Mercury after 8 years",
     ("ESA/JAXA craft ends a 6-billion-mile trip; orbit burn set for "
      "Saturday. (ESA, JAXA)"),
     ("OFFICIAL", BLUE_TAG), "mercury", "Arrived \u00b7 ESA"),
    ("06", "BRUSSELS", "EUROPE",
     "Burnham holds first EU\u2013UK reset summit",
     ("Costa & von der Leyen host the UK PM; agrifood, carbon links eyed. "
      "(EU Council)"),
     ("OFFICIAL", BLUE_TAG), "brussels", "Agreed \u00b7 Reuters"),
    ("07", "TOKYO", "ECONOMY",
     "Japan core inflation quickens to 2.2%",
     ("October core CPI up from 2.1%, fastest this year; December BoJ hike "
      "eyed. (Reuters)"),
     ("OFFICIAL", BLUE_TAG), "cpi", "Official \u00b7 Reuters"),
    ("08", "BEIJING", "RATES",
     "China holds lending rates for 18th month",
     ("1-yr LPR stays 3.0% and 5-yr 3.5%, exactly as expected. "
      "(PBOC, Reuters)"),
     ("OFFICIAL", BLUE_TAG), "rates", "Official \u00b7 PBOC"),
    ("09", "WELLINGTON", "CRICKET",
     "Phillips makes history with 118",
     ("First NZ batter with a century in three formats in a year. "
      "(ICC, AP)"),
     ("CONFIRMED", GREEN_TAG), "cricket", "Confirmed \u00b7 ICC"),
    ("10", "POLAND", "DEFENCE",
     "Missile lands in a Polish field",
     ("KH-101 debris found in a field near the border; officials say no "
      "injuries. (Reuters)"),
     ("OFFICIAL", BLUE_TAG), "poland", "Officials say \u00b7 Reuters"),
    ("11", "SANTA CLARA", "TECH",
     "Nvidia falls 14% on SEC probe report",
     ("Shares slide after a report of an SEC inquiry into chip sales; S&P "
      "500 ends \u22123.7%. (Reuters)"),
     ("REPORTED", GRAY_TAG), "nvidia", "Reported \u00b7 Reuters"),
    ("12", "HORMUZ", "ENERGY",
     "Tanker ablaze as Hormuz waits",
     ("Fourth attack on a vessel in 96 hours; 46 ships wait; Brent $92.50. "
      "[CLAIM] (Reuters)"),
     ("REPORTED", GRAY_TAG), "hormuz", "Reported \u00b7 Reuters"),
    ("13", "BARCELONA", "HEALTH",
     "Pancreatic-cancer pill shrinks tumours",
     ("60.7% response in an early trial, vs 23\u201342% chemo alone. "
      "(Reuters)"),
     ("REPORTED", GRAY_TAG), "pill", "Early trial \u00b7 Reuters"),
]

BRIEFS = [
    ("14", "SHENZHEN", "Trump, Xi & Putin publish a joint peace declaration a day after the summit (AP)"),
    ("15", "COX'S BAZAR", "Rohingya camps weep and pray after Thursday's ICJ genocide ruling (Reuters)"),
    ("16", "HORMUZ", "Four attacks on vessels in 96 hours; 46 ships wait in the strait (UNCTAD)"),
    ("17", "GAZA", "Aid groups score the peace plan's implementation at 4 of 26 points (UN News)"),
    ("18", "SEOUL", "Ruling party adopts a bid to impeach Chief Justice Cho Hee-dae (SBS)"),
    ("19", "BLANTYRE", "Malawi fuel crisis: night queues and a 20-litre daily cap (Al Jazeera)"),
    ("20", "LAS VEGAS", "Russell fastest in wet F1 practice, 1:47.272 (Formula1.com)"),
    ("21", "TONGA", "The Pacific kingdom declares an emergency as the El Ni\u00f1o drought bites (RNZ)"),
    ("22", "MATO GROSSO", "Lula meets Chief Raoni as Indigenous land is recognised in Brazil (Al Jazeera)"),
    ("23", "BOUGAINVILLE", "Rio Tinto pledges $370m for the Panguna mine's legacy (Reuters)"),
    ("24", "CANBERRA", "Budget office warns AUKUS submarine sales could shrink the US fleet (Reuters)"),
    ("25", "FLORIDA", "St Johns River hits a record 18.3 ft; four counties shut schools (AP)"),
    ("26", "BUENOS AIRES", "Argentina's peso hits 1,070 to the dollar (Reuters)"),
    ("27", "WASHINGTON", "Pentagon puts the US war against Iran at $48.3bn (Reuters)"),
    ("28", "LONDON", "UK & Norway fund \u00a3100m+ for two Ukrainian naval vessels (BBC)"),
    ("29", "COPENHAGEN", "Denmark's parliament approves the Greenland defence bill (AFP)"),
    ("30", "JAKARTA", "Indonesia's parliament passes the asset-forfeiture bill (Reuters)"),
    ("31", "DOHA", "U17 World Cup: Australia stun Argentina 2\u20130 (FIFA)"),
    ("32", "JOHANNESBURG", "Harmer spins the Proteas to a Test win as Bavuma sets a record (ICC)"),
    ("33", "HONG KONG", "Badminton World Tour reaches the semifinals (BWF)"),
    ("34", "TURIN", "Alcaraz\u2013Cobolli and Medvedev\u2013Tiafoe close out the ATP Finals groups (ATP)"),
    ("35", "RIYADH", "Houthi missile strikes the KAFD tower district (Reuters)"),
    ("36", "GLOBAL", "The UN marks World Children's Day, 20 November, across member states (UN News)"),
]

DATE_CHECK = ("First reported Thursday 19 Nov, so NOT shown as Friday's news: the "
              "Trump\u2013Xi\u2013Putin Shenzhen summit itself \u00b7 drone strike on the Dutch "
              "& Austrian embassies in Kyiv \u00b7 Anthropic Nasdaq debut \u00b7 ICJ Rohingya "
              "genocide verdict \u00b7 Senate 48\u201351 Iran war-powers vote \u00b7 GTA VI "
              "midnight launch \u00b7 $190.4m Van Gogh sale.")

# map pins: (num, lon, lat, region, lead?)
PINS = [
    (1, 30.5, 50.4, "EUROPE", True),
    (2, 84.9, 19.3, "ASIA-PACIFIC", True),
    (3, 139.7, 35.7, "ASIA-PACIFIC", True),
    (4, 30.7, 36.9, "EUROPE", False),
    (6, 4.4, 50.9, "EUROPE", False),
    (7, 147.0, 28.0, "ASIA-PACIFIC", False),
    (8, 116.4, 39.9, "ASIA-PACIFIC", False),
    (9, 174.0, -41.0, "OCEANIA", False),
    (10, 25.0, 54.0, "EUROPE", False),
    (11, -122.0, 37.4, "AMERICAS", False),
    (12, 56.5, 26.5, "MIDEAST", False),
    (13, 0.8, 40.5, "EUROPE", False),
]

# simplified continents as lon/lat polygons (own authoring)
CONTINENTS = [
    # North America
    [(-168, 66), (-150, 70), (-135, 69), (-125, 71), (-115, 73), (-100, 73),
     (-90, 74), (-82, 73), (-75, 72), (-68, 62), (-60, 55), (-55, 52),
     (-60, 47), (-65, 44), (-70, 42), (-75, 36), (-80, 32), (-81, 26),
     (-84, 30), (-89, 29), (-92, 19), (-95, 16), (-92, 15), (-86, 13),
     (-83, 9), (-80, 8), (-85, 11), (-90, 14), (-95, 16), (-97, 16),
     (-100, 18), (-105, 20), (-108, 23), (-111, 26), (-114, 29), (-117, 33),
     (-122, 37), (-124, 42), (-125, 48), (-130, 55), (-140, 60), (-150, 59),
     (-158, 58), (-165, 60), (-168, 66)],
    # South America
    [(-79, 9), (-75, 11), (-70, 12), (-64, 10), (-60, 8), (-55, 5),
     (-51, 4), (-50, 0), (-44, -3), (-38, -5), (-35, -8), (-37, -13),
     (-39, -18), (-41, -23), (-48, -27), (-52, -33), (-58, -38), (-63, -41),
     (-66, -45), (-68, -50), (-70, -54), (-73, -50), (-73, -44), (-72, -37),
     (-71, -30), (-70, -22), (-77, -12), (-80, -5), (-81, 1), (-79, 9)],
    # Europe
    [(-10, 36), (-9, 38), (-9, 43), (-2, 44), (-1, 46), (-4, 48),
     (0, 50), (2, 51), (4, 53), (7, 54), (8, 57), (10, 59),
     (13, 56), (18, 56), (21, 55), (24, 58), (26, 60), (30, 62),
     (30, 66), (28, 70), (24, 71), (18, 70), (14, 67), (12, 65),
     (10, 63), (6, 62), (5, 59), (5, 57), (2, 55), (-2, 53),
     (-5, 50), (-8, 48), (-10, 43), (-10, 36)],
    # Africa
    [(-17, 15), (-16, 20), (-15, 27), (-10, 31), (-6, 34), (-1, 35),
     (5, 37), (10, 37), (15, 32), (20, 32), (25, 32), (30, 31),
     (32, 31), (34, 28), (36, 24), (38, 20), (40, 15), (43, 12),
     (48, 11), (51, 12), (48, 7), (44, 2), (41, -2), (40, -8),
     (39, -15), (37, -20), (35, -24), (33, -27), (30, -30), (26, -34),
     (20, -35), (16, -32), (14, -26), (12, -18), (12, -10), (9, 4),
     (5, 5), (0, 6), (-7, 5), (-12, 8), (-17, 12), (-17, 15)],
    # Asia (mainland)
    [(30, 36), (33, 36), (36, 36), (39, 38), (42, 39), (45, 41),
     (48, 42), (51, 44), (54, 46), (58, 46), (62, 48), (66, 50),
     (70, 53), (74, 57), (78, 62), (82, 66), (86, 68), (90, 70),
     (95, 72), (100, 73), (105, 72), (110, 73), (115, 72), (120, 72),
     (125, 70), (130, 69), (135, 66), (138, 62), (141, 59), (142, 55),
     (141, 50), (139, 45), (137, 41), (134, 38), (130, 35), (128, 33),
     (125, 32), (122, 30), (120, 27), (118, 24), (115, 22), (112, 21),
     (109, 18), (106, 12), (104, 9), (101, 8), (98, 10), (96, 15),
     (93, 17), (91, 21), (89, 22), (86, 20), (83, 18), (80, 15),
     (77, 8), (76, 10), (74, 15), (72, 20), (70, 22), (67, 24),
     (64, 25), (61, 25), (58, 26), (56, 27), (54, 27), (52, 28),
     (50, 29), (48, 30), (45, 30), (43, 29), (40, 31), (38, 33),
     (36, 36), (33, 36), (30, 36)],
    # SE Asia islands (Indonesia / Malaysia)
    [(95, 5), (98, 6), (100, 2), (102, -2), (104, -5), (106, -6),
     (110, -7), (114, -8), (118, -9), (120, -10), (119, -5), (117, 0),
     (115, 3), (112, 2), (110, 4), (107, 2), (104, 2), (101, 3),
     (99, 5), (95, 5)],
    # Japan
    [(130, 31), (132, 33), (134, 34), (136, 35), (138, 36), (140, 38),
     (141, 41), (142, 44), (144, 44), (145, 42), (143, 40), (141, 37),
     (140, 35), (137, 35), (134, 34), (131, 32), (130, 31)],
    # Australia
    [(113, -22), (114, -30), (115, -35), (119, -35), (124, -33), (129, -32),
     (132, -32), (135, -35), (138, -35), (140, -38), (144, -38), (147, -39),
     (150, -37), (153, -32), (153, -27), (150, -22), (146, -19), (142, -11),
     (139, -15), (136, -12), (132, -12), (128, -14), (124, -16), (120, -19),
     (116, -21), (113, -22)],
    # New Zealand
    [(167, -45), (170, -43), (173, -41), (175, -39), (177, -38), (178, -37),
     (176, -39), (174, -41), (172, -43), (169, -46), (167, -45)],
    # UK
    [(-5, 50), (-3, 53), (-5, 56), (-3, 58), (-1, 57), (0, 53),
     (1, 51), (-2, 50), (-5, 50)],
    # Madagascar
    [(44, -16), (47, -15), (50, -16), (50, -20), (47, -25), (44, -25),
     (43, -20), (44, -16)],
]


# ---------- drawing helpers ----------

def draw_spiral(draw, cx, cy, r_max, turns, color, width=3):
    """Archimedean spiral, white, large."""
    pts = []
    steps = int(turns * 90)
    for i in range(steps + 1):
        t = i / steps
        ang = t * turns * 2 * math.pi
        r = t * r_max
        pts.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
    draw.line(pts, fill=color, width=width, joint="curve")


def draw_masthead(d):
    y = 8
    text_w(d, (MARGIN, y), "THE WORLD IN ONE DAY", f_sans(12, bold=True), RED)
    right = "FRIDAY'S NEWS \u00b7 ONE PAGE \u00b7 36 STORIES \u00b7 6 CONTINENTS"
    text_w(d, (W - MARGIN, y), right, f_sans(10, bold=True), INK, anchor="ra")
    text_w(d, (MARGIN, 22), "Friday 20 November 2026", f_serif(44, bold=True), INK)
    strap = ("Missiles hit Kyiv's bridges \u00b7 Cyclone Akvan ashore in India \u00b7 "
             "An AI sell-off sinks Asia \u00b7 COP31 deadlocked on its final day")
    text_w(d, (MARGIN, 72), strap, f_serif(13, bold=False), RED)


def draw_utc(d):
    y0, y1 = 90, 126
    d.rectangle([MARGIN, y0, W - MARGIN, y1], fill=CREAM2, outline=LINE)
    lx = MARGIN + 6
    text_w(d, (lx, y0 + 4), "THE DAY", f_sans(10, bold=True), RED)
    text_w(d, (lx, y0 + 17), "IN UTC", f_sans(10, bold=True), RED)
    slot_x0 = MARGIN + 78
    slot_w = (W - MARGIN - slot_x0) / 7.0
    for i, (t, ev) in enumerate(UTC_SLOTS):
        x = slot_x0 + i * slot_w
        if i > 0:
            d.line([(x - 4, y0 + 4), (x - 4, y1 - 4)], fill=LINE, width=1)
        text_w(d, (x, y0 + 3), t, f_sans(11, bold=True), NAVY)
        for j, ln in enumerate(wrap(ev, f_sans(9), slot_w - 8, d)):
            if j > 1:
                break
            text_w(d, (x, y0 + 17 + j * 10), ln, f_sans(9), INK)


def draw_strip(d):
    y0, y1 = 128, 176
    d.line([(MARGIN, y0), (W - MARGIN, y0)], fill=INK, width=2)
    d.line([(MARGIN, y1), (W - MARGIN, y1)], fill=INK, width=1)
    cell_w = CW / 6.0
    for i, (num, deck) in enumerate(STRIP):
        x = MARGIN + i * cell_w
        if i > 0:
            d.line([(x - 5, y0 + 4), (x - 5, y1 - 4)], fill=LINE, width=1)
        text_w(d, (x, y0 + 2), num, f_serif(26, bold=True), RED)
        yy = y0 + 30
        for ln in wrap(deck, f_sans(9), cell_w - 12, d)[:2]:
            text_w(d, (x, yy), ln, f_sans(9), INK)
            yy += 10


def draw_regions(d):
    y = 178
    x = MARGIN
    f = f_sans(10, bold=True)
    for name, n, col in REGIONS:
        label = f"{name} {n}"
        tw = d.textlength(label, font=f)
        w = int(tw) + 12
        d.rounded_rectangle([x, y, x + w, y + 17], radius=3, fill=col)
        d.text((x + 6, y + 3), label, font=f, fill=WHITE)
        x += w + 4
    text_w(d, (W - MARGIN, y + 3), "ALL STORIES: FRI 20 NOV 2026",
           f_sans(9, bold=True), MUTED, anchor="ra")


# ---------- lead art ----------

def art_kyiv(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=NAVY2)
    # stars
    for sx, sy in [(200, 12), (250, 20), (290, 8), (310, 22), (180, 28),
                   (230, 10), (280, 30)]:
        d.ellipse([x + sx - 1, y + sy - 1, x + sx + 1, y + sy + 1], fill=WHITE)
    # skyline (short, bottom only so text stays clear)
    base = y + h - 26
    buildings = [(0, 55, 26), (32, 40, 34), (70, 62, 24), (118, 34, 36),
                 (160, 58, 26), (205, 42, 34), (250, 60, 24), (292, 38, 32)]
    for bx, bw, bh in buildings:
        d.rectangle([x + bx, base - bh, x + bx + bw, base], fill=(8, 12, 26))
        for wy in range(base - bh + 6, base - 4, 11):
            for wx in range(bx + 6, bx + bw - 6, 12):
                if (wx + wy) % 3 == 0:
                    d.rectangle([x + wx, wy, x + wx + 4, wy + 5], fill=(255, 210, 90))
    # missile arcs (right half only, clear of the title)
    for ax0, ay0, ax1, ay1 in [(180, 14, 260, 34), (230, 10, 310, 30),
                               (200, 22, 290, 44)]:
        pts = []
        for i in range(21):
            t = i / 20.0
            px = x + ax0 + (ax1 - ax0) * t
            py = y + ay0 + (ay1 - ay0) * t - 14 * math.sin(t * math.pi)
            pts.append((px, py))
        d.line(pts, fill=(255, 140, 40), width=2, joint="curve")
        d.ellipse([x + ax1 - 3, y + ay1 - 3, x + ax1 + 3, y + ay1 + 3],
                  fill=(255, 180, 60))
    # data label on art (top-left)
    text_w(d, (x + 8, y + 6), "111 MISSILES + 404 DRONES",
           f_sans(11, bold=True), (255, 220, 90))
    # title block (left, clear of buildings and arcs)
    text_w(d, (x + 8, y + 24), "KYIV", f_serif(26, bold=True), WHITE)
    text_w(d, (x + 8, y + 52), "MISSILE BARRAGE", f_sans(10, bold=True),
           (255, 210, 90))
    # red bar at bottom
    d.rectangle([x, y + h - 26, x + w, y + h], fill=RED)
    text_w(d, (x + 8, y + h - 22), "01:25 LOCAL \u00b7 3 BRIDGES HIT",
           f_sans(10, bold=True), WHITE)
    # officials-count tag top-right (clear of data label)
    tag(d, x + w - 118, y + 5, "Officials' count", BLUE_TAG)


def art_akvan(d, x, y, w, h):
    # sea
    d.rectangle([x, y, x + w, y + h], fill=TEAL_DK)
    # India landmass (rough, left side)
    land = [(8, 10), (70, 6), (110, 30), (95, 70), (60, 105), (20, 100),
            (2, 60), (8, 10)]
    d.polygon([(x + px, y + py) for px, py in land], fill=(222, 200, 150))
    text_w(d, (x + 10, y + 34), "GOPALPUR", f_sans(9, bold=True), (60, 40, 10))
    d.ellipse([x + 52 - 4, y + 58 - 4, x + 52 + 4, y + 58 + 4], fill=RED)
    # BIG spiral, clear of title (top) and red bar (bottom)
    draw_spiral(d, x + w - 62, y + 54, 36, 4.5, WHITE, width=4)
    draw_spiral(d, x + w - 62, y + 54, 21, 3.5, (200, 235, 225), width=3)
    d.ellipse([x + w - 66, y + 50, x + w - 58, y + 58], fill=WHITE)
    text_w(d, (x + w - 118, y + 6), "BAY OF BENGAL", f_sans(9, bold=True), WHITE)
    text_w(d, (x + 8, y + 6), "CYCLONE AKVAN", f_serif(20, bold=True), WHITE)
    d.rectangle([x, y + h - 26, x + w, y + h], fill=RED)
    text_w(d, (x + 8, y + h - 22), "LANDFALL 08:30 IST",
           f_sans(10, bold=True), WHITE)
    text_w(d, (x + w - 8, y + h - 22), "70\u201380 KM/H AT COAST",
           f_sans(10, bold=True), WHITE, anchor="ra")


def art_markets(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=NAVY2)
    text_w(d, (x + 8, y + 6), "AI SELL-OFF", f_serif(22, bold=True), WHITE)
    text_w(d, (x + 8, y + 30), "ASIA \u00b7 INTRADAY LOWS", f_sans(9, bold=True),
           (255, 210, 90))
    # declining line chart
    pts = []
    for i, v in enumerate([0.95, 0.80, 0.88, 0.60, 0.70, 0.35, 0.45, 0.10]):
        px = x + 14 + i * 20
        py = y + 44 + (1 - v) * 26
        pts.append((px, py))
    d.line(pts, fill=(255, 90, 60), width=3, joint="curve")
    # index table (4 rows, clear of the red bar)
    rows = [("NIKKEI", "\u22124.9%"), ("KOSPI", "\u22125.4%"),
            ("TAIEX", "\u22126.8%"), ("HANG SENG", "\u22122.0%")]
    ry = y + 40
    for name, val in rows:
        text_w(d, (x + 178, ry), name, f_sans(11, bold=True), WHITE)
        text_w(d, (x + w - 10, ry), val, f_sans(11, bold=True), (255, 90, 60),
               anchor="ra")
        ry += 13
    d.rectangle([x, y + h - 26, x + w, y + h], fill=RED)
    text_w(d, (x + 8, y + h - 22), "WORST WEEK SINCE 2020",
           f_sans(10, bold=True), WHITE)


LEAD_ART = {"kyiv": art_kyiv, "akvan": art_akvan, "markets": art_markets}
LEAD_ART_KEYS = ["kyiv", "akvan", "markets"]


def draw_leads(d):
    y0, y1 = 198, 314
    col_w = (CW - 12) / 3.0
    for i, lead in enumerate(LEADS):
        x = MARGIN + i * (col_w + 6)
        LEAD_ART[LEAD_ART_KEYS[i]](d, int(x), y0, int(col_w), y1 - y0)
        # text under art
        ty = y1 + 6
        tlabel, tbg = lead["trust"]
        text_w(d, (x, ty), f"{lead['num']} \u00b7 {lead['kicker']}",
               f_sans(9, bold=True), RED)
        tw = tag(d, x + col_w - 74, ty - 1, tlabel, tbg)
        ty += 14
        ty = para(d, x, ty, lead["head"], f_serif(16, bold=True), INK,
                  col_w, leading=1)
        ty += 2
        para(d, x, ty, lead["body"], f_sans(10), INK, col_w, leading=2)


# ---------- feature illustrations ----------

def _art_bg(d, x, y, w, h, col):
    d.rectangle([x, y, x + w, y + h], fill=col)


def art_cop31(d, x, y, w, h):
    _art_bg(d, x, y, w, h, (15, 90, 95))
    # globe
    cx, cy, r = x + 34, y + h // 2, 17
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(70, 160, 200),
              outline=(220, 240, 235), width=2)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(220, 240, 235))
    d.arc([cx - r, cy - r, cx + r, cy + r], 200, 340, fill=(220, 240, 235), width=1)
    d.line([(cx - r, cy), (cx + r, cy)], fill=(220, 240, 235), width=1)
    d.line([(cx, cy - r), (cx, cy + r)], fill=(220, 240, 235), width=1)
    # thermometer
    d.rectangle([x + 66, y + 6, x + 74, y + h - 12], fill=WHITE, outline=RED)
    d.rectangle([x + 68, y + 14, x + 72, y + h - 14], fill=RED)
    d.ellipse([x + 63, y + h - 16, x + 77, y + h - 2], fill=RED)
    text_w(d, (x + 86, y + 6), "NO", f_sans(13, bold=True), WHITE)
    text_w(d, (x + 86, y + 20), "DEAL", f_sans(13, bold=True), WHITE)


def art_mercury(d, x, y, w, h):
    _art_bg(d, x, y, w, h, (12, 14, 30))
    for sx, sy in [(12, 8), (60, 14), (110, 6), (150, 12), (180, 8)]:
        d.ellipse([x + sx, y + sy, x + sx + 1, y + sy + 1], fill=WHITE)
    cx, cy, r = x + 40, y + h // 2 + 2, 16
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(170, 170, 175))
    for ox, oy, orr in [(32, cy - 5, 3), (46, cy + 6, 4), (36, cy + 8, 2)]:
        d.ellipse([x + ox - orr, oy - orr, x + ox + orr, oy + orr],
                  fill=(130, 130, 135))
    # spacecraft: body + solar panels
    d.rectangle([x + 78, y + 16, x + 96, y + 28], fill=(200, 200, 210))
    d.rectangle([x + 70, y + 19, x + 78, y + 25], fill=(60, 120, 200))
    d.rectangle([x + 96, y + 19, x + 104, y + 25], fill=(60, 120, 200))
    d.line([(x + 96, y + 22), (x + 120, y + 34)], fill=(255, 200, 80), width=2)
    text_w(d, (x + 112, y + 30), "6BN MILES", f_sans(10, bold=True), WHITE)


def art_brussels(d, x, y, w, h):
    _art_bg(d, x, y, w, h, (30, 50, 110))
    # EU flag
    d.rectangle([x + 10, y + 8, x + 62, y + h - 8], fill=(0, 51, 153))
    for k in range(12):
        a = k * math.pi / 6
        d.ellipse([x + 36 + 11 * math.cos(a) - 1, y + h // 2 + 9 * math.sin(a) - 1,
                   x + 36 + 11 * math.cos(a) + 1, y + h // 2 + 9 * math.sin(a) + 1],
                  fill=(255, 204, 0))
    # UK flag
    fx, fy = x + 72, y + 8
    d.rectangle([fx, fy, fx + 52, fy + h - 16], fill=(1, 33, 105))
    d.line([(fx, fy), (fx + 52, fy + h - 16)], fill=WHITE, width=4)
    d.line([(fx + 52, fy), (fx, fy + h - 16)], fill=WHITE, width=4)
    d.line([(fx, fy), (fx + 52, fy + h - 16)], fill=(200, 16, 46), width=2)
    d.line([(fx + 52, fy), (fx, fy + h - 16)], fill=(200, 16, 46), width=2)
    d.rectangle([fx + 24, fy, fx + 28, fy + h - 16], fill=WHITE)
    d.rectangle([fx, fy + (h - 16) // 2 - 2, fx + 52, fy + (h - 16) // 2 + 2],
                fill=WHITE)
    d.rectangle([fx + 25, fy, fx + 27, fy + h - 16], fill=(200, 16, 46))
    d.rectangle([fx, fy + (h - 16) // 2 - 1, fx + 52, fy + (h - 16) // 2 + 1],
                fill=(200, 16, 46))
    # handshake arrows
    d.line([(x + 134, y + 12), (x + 150, y + 12)], fill=(255, 204, 0), width=3)
    d.polygon([(x + 150, y + 8), (x + 150, y + 16), (x + 156, y + 12)],
              fill=(255, 204, 0))
    d.line([(x + 150, y + 30), (x + 134, y + 30)], fill=(255, 204, 0), width=3)
    d.polygon([(x + 134, y + 26), (x + 134, y + 34), (x + 128, y + 30)],
              fill=(255, 204, 0))


def art_cpi(d, x, y, w, h):
    _art_bg(d, x, y, w, h, (245, 239, 224))
    d.line([(x + 8, y + h - 8), (x + w - 8, y + h - 8)], fill=INK, width=2)
    bars = [(20, 12), (55, 18), (90, 26), (125, 34)]
    for bx, bh in bars:
        d.rectangle([x + bx, y + h - 8 - bh, x + bx + 24, y + h - 8],
                    fill=RED)
    text_w(d, (x + 152, y + 4), "2.2%", f_sans(14, bold=True), RED)
    text_w(d, (x + 152, y + 20), "CPI", f_sans(9, bold=True), INK)
    text_w(d, (x + 152, y + 30), "CORE", f_sans(9, bold=True), INK)


def art_rates(d, x, y, w, h):
    _art_bg(d, x, y, w, h, (245, 239, 224))
    d.line([(x + 8, y + h - 8), (x + w - 8, y + h - 8)], fill=INK, width=2)
    pts = [(x + 12, y + 20), (x + 60, y + 20), (x + 110, y + 22),
           (x + 160, y + 20), (x + 185, y + 20)]
    d.line(pts, fill=NAVY, width=3, joint="curve")
    for px, py in pts:
        d.ellipse([px - 2, py - 2, px + 2, py + 2], fill=RED)
    text_w(d, (x + 10, y + 4), "3.50% 5Y", f_sans(11, bold=True), NAVY)
    text_w(d, (x + 110, y + 26), "3.00% 1Y", f_sans(11, bold=True), NAVY)


def art_cricket(d, x, y, w, h):
    _art_bg(d, x, y, w, h, (20, 90, 50))
    # bat
    d.rectangle([x + 30, y + 8, x + 52, y + h - 8], fill=(210, 180, 120),
                outline=(120, 90, 40), width=2)
    d.rectangle([x + 38, y + 2, x + 44, y + 10], fill=(120, 90, 40))
    # ball
    d.ellipse([x + 78, y + 12, x + 100, y + 34], fill=(185, 28, 28),
              outline=WHITE, width=2)
    d.arc([x + 78, y + 12, x + 100, y + 34], 30, 210, fill=WHITE, width=2)
    text_w(d, (x + 112, y + 8), "118", f_serif(20, bold=True), WHITE)
    text_w(d, (x + 112, y + 28), "RUNS", f_sans(9, bold=True), (255, 220, 90))


def art_poland(d, x, y, w, h):
    _art_bg(d, x, y, w, h, (200, 220, 235))
    # simplified Poland outline
    poly = [(30, 12), (70, 8), (110, 14), (130, 28), (120, 40),
            (80, 44), (40, 40), (22, 26), (30, 12)]
    d.polygon([(x + px, y + py) for px, py in poly], fill=(250, 250, 245),
              outline=NAVY)
    d.ellipse([x + 66 - 4, y + 26 - 4, x + 66 + 4, y + 26 + 4], fill=RED)
    # missile
    d.polygon([(x + 140, y + 10), (x + 158, y + 14), (x + 140, y + 18)],
              fill=(60, 60, 60))
    d.rectangle([x + 118, y + 11, x + 140, y + 17], fill=(90, 90, 90))
    d.polygon([(x + 118, y + 11), (x + 110, y + 6), (x + 118, y + 14)],
              fill=(60, 60, 60))
    d.polygon([(x + 118, y + 17), (x + 110, y + 22), (x + 118, y + 14)],
              fill=(60, 60, 60))
    text_w(d, (x + 130, y + 30), "KH-101", f_sans(10, bold=True), RED)


def art_nvidia(d, x, y, w, h):
    _art_bg(d, x, y, w, h, (15, 20, 25))
    # chip
    cx, cy = x + 46, y + h // 2
    d.rectangle([cx - 22, cy - 18, cx + 22, cy + 18], fill=(30, 40, 50),
                outline=(120, 200, 80), width=2)
    d.rectangle([cx - 12, cy - 10, cx + 12, cy + 10], fill=(120, 200, 80))
    for k in range(5):
        px = cx - 18 + k * 9
        d.line([(px, cy - 24), (px, cy - 18)], fill=(150, 150, 150), width=2)
        d.line([(px, cy + 18), (px, cy + 24)], fill=(150, 150, 150), width=2)
    text_w(d, (x + 84, y + 6), "\u221214%", f_serif(18, bold=True), (255, 90, 60))
    text_w(d, (x + 84, y + 26), "SEC PROBE", f_sans(9, bold=True), WHITE)


def art_hormuz(d, x, y, w, h):
    _art_bg(d, x, y, w, h, (10, 40, 70))
    # sea
    d.rectangle([x, y + h - 12, x + w, y + h], fill=(20, 90, 120))
    # tanker hull
    d.polygon([(x + 20, y + 24), (x + 120, y + 24), (x + 132, y + 34),
               (x + 14, y + 34)], fill=(60, 60, 60))
    d.rectangle([x + 96, y + 12, x + 118, y + 24], fill=(200, 200, 200))
    # flames
    for fx, fy, fs in [(40, 22, 10), (58, 20, 13), (78, 22, 11), (96, 20, 9)]:
        d.polygon([(x + fx - fs, y + fy), (x + fx, y + fy - fs - 6),
                   (x + fx + fs, y + fy)], fill=(255, 140, 0))
        d.polygon([(x + fx - fs // 2, y + fy), (x + fx, y + fy - fs),
                   (x + fx + fs // 2, y + fy)], fill=(255, 220, 0))
    # smoke
    for sx, sy, sr in [(50, 8, 4), (70, 5, 5), (90, 8, 4)]:
        d.ellipse([x + sx - sr, y + sy - sr, x + sx + sr, y + sy + sr],
                  fill=(120, 120, 120))
    text_w(d, (x + 142, y + 8), "$92.50", f_sans(12, bold=True), (255, 200, 80))
    text_w(d, (x + 142, y + 24), "BRENT", f_sans(9, bold=True), WHITE)


def art_pill(d, x, y, w, h):
    _art_bg(d, x, y, w, h, (250, 245, 235))
    # capsule, diagonal
    d.ellipse([x + 20, y + 10, x + 62, y + 38], fill=(185, 28, 28))
    d.ellipse([x + 20, y + 10, x + 62, y + 38], outline=RED)
    d.chord([x + 20, y + 10, x + 62, y + 38], 300, 120, fill=WHITE)
    d.ellipse([x + 20, y + 10, x + 62, y + 38], outline=(120, 120, 120))
    text_w(d, (x + 76, y + 6), "60.7%", f_serif(18, bold=True), RED)
    text_w(d, (x + 76, y + 26), "RESPONSE", f_sans(9, bold=True), INK)


FEATURE_ART = {
    "cop31": art_cop31, "mercury": art_mercury, "brussels": art_brussels,
    "cpi": art_cpi, "rates": art_rates, "cricket": art_cricket,
    "poland": art_poland, "nvidia": art_nvidia, "hormuz": art_hormuz,
    "pill": art_pill,
}


def draw_features(d):
    y_rows = [408, 512]
    col_w = (CW - 4 * 6) / 5.0
    art_h = 46
    for idx, feat in enumerate(FEATURES):
        row = idx // 5
        col = idx % 5
        x = MARGIN + col * (col_w + 6)
        y = y_rows[row]
        num, place, sec, head, body, (tlabel, tbg), art, src = feat
        # art panel + source tag strip
        FEATURE_ART[art](d, int(x), y, int(col_w), art_h)
        d.rectangle([x, y + art_h - 11, x + col_w, y + art_h], fill=(0, 0, 0))
        text_w(d, (x + 4, y + art_h - 10), src, f_sans(7, bold=True), WHITE)
        # kicker line: place left, trust tag right (no overlap with art)
        ty = y + art_h + 3
        text_w(d, (x, ty), f"{num} \u00b7 {place}",
               f_sans(8, bold=True), RED)
        tag(d, x + col_w - 66, ty - 1, tlabel, tbg)
        ty += 12
        ty = para(d, x, ty, head, f_sans(11, bold=True), INK, col_w, leading=0)
        para(d, x, ty + 1, body, f_sans(9), INK, col_w, leading=0)


# ---------- light map + briefs ----------

def proj(lon, lat, bx, by, bw, bh):
    px = bx + (lon + 180.0) * bw / 360.0
    py = by + (85.0 - lat) * bh / 145.0
    return px, py


def draw_map(d):
    bx, by, bw, bh = MARGIN, 636, 340, 180
    d.rectangle([bx, by, bx + bw, by + bh], fill=LIGHT_MAP_BG, outline=LINE)
    # continents
    for poly in CONTINENTS:
        pts = [proj(lon, lat, bx, by, bw, bh) for lon, lat in poly]
        d.polygon(pts, fill=LAND, outline=(180, 168, 135))
    # graticule (light)
    for lon in range(-150, 181, 30):
        px, _ = proj(lon, 85, bx, by, bw, bh)
        d.line([(px, by), (px, by + bh)], fill=(230, 224, 210), width=1)
    for lat in range(-60, 86, 30):
        _, py = proj(-180, lat, bx, by, bw, bh)
        d.line([(bx, py), (bx + bw, py)], fill=(230, 224, 210), width=1)
    # pins (region-coloured, numbered; gold ring on leads 1-3)
    for num, lon, lat, region, lead in PINS:
        px, py = proj(lon, lat, bx, by, bw, bh)
        col = REG_COL[region]
        r = 7
        if lead:
            d.ellipse([px - r - 2, py - r - 2, px + r + 2, py + r + 2],
                      outline=GOLD, width=2)
        d.ellipse([px - r, py - r, px + r, py + r], fill=col,
                  outline=WHITE, width=1)
        f = f_sans(8, bold=True)
        tw = d.textlength(str(num), font=f)
        d.text((px - tw / 2, py - 5), str(num), font=f, fill=WHITE)
    # SPACE badge (Mercury, feature 5)
    tag(d, bx + bw - 62, by + 6, "SPACE", (30, 64, 175))
    # region legend under map
    ly = by + bh + 8
    lx = bx
    f = f_sans(8, bold=True)
    for name in ["EUROPE", "ASIA-PACIFIC", "AMERICAS", "MIDEAST", "AFRICA",
                 "OCEANIA", "WORLD/SPACE"]:
        col = REG_COL[name]
        d.ellipse([lx, ly + 1, lx + 7, ly + 8], fill=col)
        tw = d.textlength(name, font=f)
        d.text((lx + 10, ly), name, font=f, fill=INK)
        lx += 10 + int(tw) + 8
    text_w(d, (bx, ly + 12), "1\u20133 Lead (gold ring) \u00b7 4\u201313 Features \u00b7 Positions approximate.",
           f_sans(8), MUTED)


def draw_briefs(d):
    x0 = MARGIN + 340 + 12
    col_w = (W - MARGIN - x0 - 10) / 2.0
    y0 = 636
    # left column: briefs 14-24 (11), right column: 25-36 (12)
    cols = [BRIEFS[:11], BRIEFS[11:]]
    for ci, col in enumerate(cols):
        x = x0 + ci * (col_w + 10)
        y = y0
        for num, place, body in col:
            head = f"{num} {place} \u2014 "
            # draw head in bold red, then body wrapped
            f_head = f_sans(9, bold=True)
            f_body = f_sans(9)
            # wrap body with head on first line
            first_w = col_w - d.textlength(head, font=f_head)
            lines = wrap(body, f_body, first_w, d)
            d.text((x, y), head, font=f_head, fill=RED)
            hx = x + d.textlength(head, font=f_head)
            if lines:
                d.text((hx, y), lines[0], font=f_body, fill=INK)
                y += 11
                for ln in lines[1:2]:
                    d.text((x, y), ln, font=f_body, fill=INK)
                    y += 11
            else:
                y += 11
            y += 2


def draw_section_headers(d):
    text_w(d, (MARGIN, 620), "WHERE IT HAPPENED", f_sans(11, bold=True), RED)
    text_w(d, (MARGIN + 352, 620), "ALSO ON FRIDAY 20 NOVEMBER \u2014 23 MORE STORIES",
           f_sans(11, bold=True), RED)


def draw_datecheck(d):
    y0, y1 = 928, 978
    d.rectangle([MARGIN, y0, W - MARGIN, y1], outline=RED, width=2)
    text_w(d, (MARGIN + 8, y0 + 4), "DATE CHECK", f_sans(11, bold=True), RED)
    para(d, MARGIN + 8, y0 + 18, DATE_CHECK, f_sans(10), INK,
         W - 2 * MARGIN - 16, leading=2)


def draw_footer(d):
    y = 984
    x = MARGIN
    # trust legend pills
    for label, bg in [("CONFIRMED", GREEN_TAG), ("OFFICIAL", BLUE_TAG),
                      ("REPORTED", GRAY_TAG)]:
        w = tag(d, x, y, label, bg)
        x += w + 4
    text_w(d, (x, y + 1),
           "2+ outlets \u00b7 on the record \u00b7 one outlet \u00b7 claims attributed, forecasts flagged",
           f_sans(9), MUTED)
    text_w(d, (MARGIN, 1000),
           "Every story here happened, or was first reported, on Friday 20 November 2026 in at least one time zone. "
           "Sources: Reuters, AP, AFP, BBC, IMD, UN News, Al Jazeera, ICC, EU Council, PBOC. Original vector drawings.",
           f_sans(9), MUTED)


# ---------- main ----------

def main():
    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)
    draw_masthead(d)
    draw_utc(d)
    draw_strip(d)
    draw_regions(d)
    draw_leads(d)
    draw_features(d)
    draw_section_headers(d)
    draw_map(d)
    draw_briefs(d)
    draw_datecheck(d)
    draw_footer(d)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    img.save(OUT, format="PNG", optimize=True)
    data = open(OUT, "rb").read()
    print("out:", OUT)
    print("size:", len(data), "bytes")
    print("sha256:", hashlib.sha256(data).hexdigest())
    print("dims:", img.size, img.mode)


if __name__ == "__main__":
    main()
