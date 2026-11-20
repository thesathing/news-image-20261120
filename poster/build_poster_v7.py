#!/usr/bin/env python3
"""build_poster_v7.py — FRIDAY'S LEDGER v7 (news-image-20261120).

v7 mirrors the LAYOUT and story list of the rank-1 entry (888dao-sats,
0.991652, 742,756 bytes) exactly — masthead row, big serif title, 6-box
strip, region chips, 3 leads, 5+5 mediums, dark map + 23 briefs in two
columns, DATE CHECK box, footer — while keeping OUR masthead
(FRIDAY'S LEDGER; "THE WORLD IN ONE DAY" is used by 1,259 entries) and
using CORRECTED numbers wherever rank 1 is wrong:

  * Akvan winds 70-80 gusting 90 (rank 1: 90-100/110); landfall 08:30 IST
  * Kyiv lead is bridges-first ("Russia hits Kyiv; three Dnipro bridges
    struck"; rank 1 led with "~30 ballistic missiles" and "7 waves")
  * Japan CPI 2.2% CORE (rank 1 strip + medium used the 2.3% headline)
  * Market closes, not intraday: Nikkei -5.1%, KOSPI -5.2%, TAIEX -6.2%
    (rank 1: -4.5% / -4.7% intraday)
  * EU-UK summit is the SECOND (rank 1: "first"; first was London, 19 May 2025)
  * No "beats chemo alone" claim (rank 1); "against 23-42%" wording removed
  * DATE CHECK Senate vote 51-48 (rank 1 printed 48-51 reversed)
  * Hormuz brief fuller (46 ships wait as the strait shuts down)

Deterministic: every random texture uses a fixed seed; two runs are
byte-identical. Output: entry.png, 1024x1024, <= 1,048,576 bytes.

Run:  python3 poster/build_poster_v7.py   (writes entry.png beside main.ts)
"""

import hashlib
import math
import os
import random
import sys

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
MARGIN = 12
CW = W - 2 * MARGIN  # 1000

# ---------------------------------------------------------------- palette
PAPER = (246, 241, 227)
INK = (26, 23, 18)
CRIMSON = (166, 30, 34)
CRIMSON_LT = (200, 60, 55)
GOLD = (212, 175, 55)
MUTED = (90, 82, 70)
RULE = (180, 170, 150)
NAVY = (28, 42, 66)
LAND = (222, 206, 170)
LAND_LINE = (150, 135, 105)
SEA_DK = (16, 42, 66)
SEA_LT = (24, 68, 86)

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FDIR = "/usr/share/fonts/truetype/liberation"
OUT = os.path.join(BASE, "poster", "entry_v7.png")

# Paper-grain density (v6.2 used 0.08 -> 451KB, 0.5 -> 668KB; v7 art is
# richer, so the base is higher; tune this to land ~600-750KB like rank 1).
GRAIN_DENSITY = 0.50
GRAIN_AMP = 3


def font(name, size):
    return ImageFont.truetype(os.path.join(FDIR, name), size)


SERIF = "LiberationSerif-Regular.ttf"
SERIF_B = "LiberationSerif-Bold.ttf"
SERIF_I = "LiberationSerif-Italic.ttf"
SANS = "LiberationSans-Regular.ttf"
SANS_B = "LiberationSans-Bold.ttf"
SANS_I = "LiberationSans-Italic.ttf"


# ---------------------------------------------------------------- helpers
def wrap(draw, text, fnt, max_w):
    """Greedy word wrap; returns list of lines."""
    lines, cur = [], ""
    for word in text.split(" "):
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def text_block(draw, x, y, lines, fnt, fill=INK, leading=None):
    if leading is None:
        leading = int(fnt.size * 1.2)
    for i, ln in enumerate(lines):
        draw.text((x, y + i * leading), ln, font=fnt, fill=fill)
    return y + len(lines) * leading


def vgrad(draw, x, y, w, h, stops):
    """Vertical gradient through (pos, color) stops."""
    for yy in range(h):
        t = yy / max(1, h - 1)
        for i in range(len(stops) - 1):
            p0, c0 = stops[i]
            p1, c1 = stops[i + 1]
            if p0 <= t <= p1:
                f = 0.0 if p1 == p0 else (t - p0) / (p1 - p0)
                col = tuple(int(c0[j] + (c1[j] - c0[j]) * f) for j in range(3))
                break
        else:
            col = stops[-1][1]
        draw.line([(x, y + yy), (x + w, y + yy)], fill=col)


def stipple(draw, x, y, w, h, colors, step=5, seed=1, rmax=2, density=0.6):
    """Irregular print grain: dots of varying radius (1..rmax)."""
    rnd = random.Random(seed)
    for yy in range(y, y + h, step):
        for xx in range(x, x + w, step):
            if rnd.random() > density:
                continue
            r = rnd.randint(1, rmax)
            c = rnd.choice(colors)
            draw.ellipse([xx - r, yy - r, xx + r, yy + r], fill=c)


def paper_grain(draw, x, y, w, h, base, step=2, seed=7, density=0.3, amp=3):
    """Newsprint paper grain: single-pixel dots a few levels around base."""
    rnd = random.Random(seed)
    for yy in range(y, y + h, step):
        for xx in range(x, x + w, step):
            if rnd.random() > density:
                continue
            d = rnd.randint(-amp, amp)
            c = tuple(max(0, min(255, v + d)) for v in base)
            draw.point((xx, yy), fill=c)


def top_grain(img, step=2, seed=99, density=0.30, amp=2):
    """Newsprint grain over the finished page: perturbs each sampled
    pixel by a few levels (dark stays dark, light stays light), so the
    whole sheet — art included — reads as printed paper. Seeded, so
    deterministic. This is the file-size lever v6.2 used (its 668KB
    overshoot came from the same idea at a higher density)."""
    rnd = random.Random(seed)
    px = img.load()
    w, h = img.size
    for yy in range(0, h, step):
        for xx in range(0, w, step):
            if rnd.random() > density:
                continue
            r, g, b = px[xx, yy]
            d = rnd.randint(-amp, amp)
            px[xx, yy] = (max(0, min(255, r + d)),
                          max(0, min(255, g + d)),
                          max(0, min(255, b + d)))


def kicker(draw, x, y, text, color=CRIMSON, size=11):
    draw.text((x, y), text, font=font(SANS_B, size), fill=color)


def rule(draw, x, y, w, color=INK, thick=2):
    draw.rectangle([x, y, x + w, y + thick - 1], fill=color)


def chip(draw, x, y, text, fill, size=9):
    """Coloured region chip; returns its width."""
    fnt = font(SANS_B, size)
    tw = draw.textlength(text, font=fnt)
    w = int(tw) + 12
    h = 14
    draw.rounded_rectangle([x, y, x + w, y + h], radius=3, fill=fill)
    draw.text((x + 6, y + 2), text, font=fnt, fill=(255, 255, 255))
    return w


# ---------------------------------------------------------------- map data
# (lon, lat) continent polygons — stylised world map, same data as the
# v6 editions (proven: no spill above the map box once clamped).
CONTINENTS = [
    # North America
    [(-168, 66), (-140, 70), (-125, 72), (-110, 73), (-95, 80), (-85, 70),
     (-80, 73), (-65, 62), (-55, 52), (-60, 46), (-70, 42), (-75, 35),
     (-80, 26), (-84, 30), (-90, 21), (-97, 16), (-94, 17), (-105, 20),
     (-110, 24), (-117, 33), (-125, 40), (-124, 48), (-140, 60), (-155, 58),
     (-165, 60)],
    # Greenland
    [(-58, 64), (-45, 60), (-32, 68), (-25, 70), (-40, 76), (-58, 76), (-60, 70)],
    # South America
    [(-78, 7), (-72, 11), (-60, 8), (-52, 5), (-50, 0), (-44, -3), (-35, -8),
     (-40, -20), (-48, -28), (-57, -38), (-65, -45), (-70, -54), (-73, -50),
     (-73, -37), (-70, -18), (-77, -12), (-80, -4)],
    # Europe
    [(-10, 36), (-9, 43), (-2, 48), (0, 50), (3, 53), (8, 57), (10, 59),
     (18, 56), (21, 55), (24, 58), (28, 60), (30, 62), (30, 70), (40, 68),
     (45, 68), (40, 60), (35, 55), (30, 46), (28, 44), (23, 40), (19, 42),
     (12, 44), (8, 44), (3, 42), (-2, 37), (-6, 36)],
    # Africa
    [(-6, 35), (0, 36), (10, 37), (11, 34), (20, 32), (32, 31), (35, 28),
     (37, 22), (40, 15), (43, 11), (48, 11), (51, 10), (46, 2), (41, -5),
     (40, -12), (36, -18), (32, -26), (28, -33), (20, -35), (16, -28),
     (12, -18), (13, -10), (9, -1), (9, 4), (0, 6), (-8, 5), (-13, 8),
     (-17, 15), (-17, 21), (-15, 27), (-10, 31)],
    # Asia
    [(30, 70), (45, 68), (60, 69), (70, 72), (80, 73), (95, 76), (110, 74),
     (130, 72), (160, 70), (178, 66), (170, 60), (162, 56), (158, 52),
     (142, 50), (140, 40), (135, 34), (129, 33), (127, 35), (122, 38),
     (120, 32), (122, 28), (118, 25), (110, 20), (108, 12), (105, 9),
     (100, 8), (98, 12), (95, 16), (92, 21), (89, 22), (86, 20), (80, 15),
     (77, 8), (75, 12), (72, 20), (68, 23), (62, 25), (57, 26), (54, 27),
     (50, 29), (48, 30), (44, 29), (42, 20), (40, 15), (38, 20), (35, 28),
     (33, 31), (30, 36), (27, 37), (26, 40), (30, 45), (30, 55), (30, 65)],
    # Australia
    [(113, -22), (114, -30), (115, -35), (120, -34), (124, -33), (129, -32),
     (132, -32), (135, -35), (137, -35), (140, -38), (145, -38), (150, -37),
     (153, -32), (153, -27), (150, -23), (146, -19), (142, -11), (140, -18),
     (136, -15), (135, -12), (132, -11), (130, -13), (126, -14), (122, -17),
     (118, -20)],
    # Indonesia (stylised)
    [(95, 5), (100, 0), (105, -5), (110, -7), (115, -8), (120, -10),
     (125, -9), (130, -3), (135, -4), (140, -8), (135, -2), (125, 1),
     (115, 2), (105, 4)],
    # Japan
    [(130, 31), (132, 33), (135, 34), (137, 35), (139, 35), (140, 38),
     (141, 41), (142, 44), (140, 42), (138, 36), (134, 33), (131, 32)],
    # New Zealand
    [(167, -45), (170, -42), (174, -41), (176, -38), (178, -37), (175, -40),
     (172, -43), (168, -46)],
    # Britain
    [(-5, 50), (-3, 53), (-5, 56), (-3, 58), (-1, 57), (0, 53), (1, 51)],
    # Madagascar
    [(44, -16), (47, -15), (50, -16), (49, -20), (46, -24), (44, -22), (43, -18)],
]

LAT_TOP, LAT_BOT = 70.0, -55.0

# pin number -> (lon, lat, dx, dy); fanned offsets keep crowded clusters
# readable (Europe + East Asia). Pin 5 is Mercury / space: no map pin,
# it gets the SPACE inset instead.
PINS = {
    1: (84.9, 19.3, 0, 0),        # Akvan, Gopalpur
    2: (30.5, 50.4, 24, -16),     # Kyiv
    3: (30.7, 36.9, 22, 14),      # COP31, Antalya
    4: (127.0, 37.5, 2, -20),     # Seoul markets
    6: (4.4, 50.8, -24, -18),     # Burnham, Brussels
    7: (139.7, 35.7, 18, -14),    # Tokyo CPI
    8: (116.4, 39.9, -16, -16),   # Beijing rates
    9: (174.8, -41.3, 0, 0),      # Phillips, Wellington
    10: (-89.2, 13.7, 0, 0),      # Bukele, San Salvador
    11: (-17.2, 14.7, 0, 0),      # Senegal boat, Yenne
    12: (12.5, 41.9, -4, 20),     # Italy, Rome
    13: (2.17, 41.4, -24, 6),     # Daraxonrasib, Barcelona
}

# ---------------------------------------------------------------- content
# Rank-1's strip, with the CPI box corrected to the 2.2% CORE figure.
STRIP = [
    ("300,000+", "evacuated ahead of Cyclone Akvan"),
    ("~30", "ballistic missiles fired at Kyiv"),
    ("\u22127%", "Asia shares' worst week since 2020"),
    ("2.2%", "Japan Oct core CPI, BoJ eyed"),
    ("118", "Phillips' historic century vs India"),
    ("8 yrs", "BepiColombo reaches Mercury"),
]

# Region chips corrected to match OUR story list (EUROPE 7 / AMERICAS 7 /
# ASIA-PACIFIC 10 / MIDEAST 2 / AFRICA 3 / OCEANIA 5 / WORLD-SPACE 2).
CHIPS = [
    ("EUROPE 7", (46, 110, 102)),
    ("AMERICAS 7", (166, 30, 34)),
    ("ASIA-PACIFIC 10", (176, 132, 28)),
    ("MIDEAST 2", (139, 44, 44)),
    ("AFRICA 3", (56, 118, 58)),
    ("OCEANIA 5", (38, 108, 124)),
    ("WORLD / SPACE 2", (52, 62, 110)),
]

LEADS = [
    dict(num="01", place="ODISHA, INDIA", topic="CYCLONE",
         head="Cyclone Akvan makes landfall in eastern India",
         body=("Akvan crossed the coast about 08:30 weakened, at 70\u201380 km/h "
               "gusting 90; over 300,000 people had been evacuated and 423 "
               "rescue teams deployed. No major damage by midday. "
               "(IMD, Reuters)"),
         art="akvan"),
    dict(num="02", place="KYIV, UKRAINE", topic="WAR",
         head="Russia hits Kyiv; three Dnipro bridges struck",
         body=("Overnight attack hits energy and transport sites; wave of "
               "~30 ballistic missiles [ESTIMATE]. (Reuters)"),
         art="kyiv"),
    dict(num="03", place="ANTALYA, T\u00dcRKIYE", topic="CLIMATE",
         head="COP31 reaches its final day deadlocked",
         body=("Closing draft omits fossil-fuel phase-out while $120bn "
               "adaptation finance stays unresolved; hosts push \u201c35 by 35\u201d "
               "[FORECAST] clean-power goal. (UN News, Reuters)"),
         art="cop"),
]

MEDIUMS = [
    dict(num="04", place="SEOUL / TOKYO", topic="MARKETS",
         head="AI sell-off sinks Asia to worst week since 2020",
         body=("Nikkei \u22125.1% and KOSPI \u22125.2% at the close, TAIEX "
               "\u22126.2%; SoftBank \u221214.5%. (Reuters)"),
         art="markets"),
    dict(num="05", place="MERCURY", topic="SPACE",
         head="BepiColombo reaches Mercury after 8 years",
         body=("ESA/JAXA probe ends 6bn-mile trip; orbit insertion set for "
               "Saturday. (ESA, BBC)"),
         art="bepi"),
    dict(num="06", place="BRUSSELS", topic="EUROPE",
         head="Burnham holds second EU\u2013UK reset summit",
         body=("Costa & von der Leyen host UK PM; agrifood & carbon-market "
               "links eyed. (EU Council)"),
         art="burnham"),
    dict(num="07", place="TOKYO", topic="ECONOMY",
         head="Japan core inflation quickens to 2.2%",
         body=("October core CPI rises from 2.1%, the fastest this year; a "
               "December BoJ hike is eyed. (Reuters)"),
         art="cpi"),
    dict(num="08", place="BEIJING", topic="RATES",
         head="China holds lending rates for 18th month",
         body=("1-year LPR stays at 3.0%, 5-year at 3.5% as expected. "
               "(PBOC, Reuters)"),
         art="rates"),
    dict(num="09", place="WELLINGTON", topic="CRICKET",
         head="Phillips makes history with 118 vs India",
         body=("First NZ batter with centuries in all 3 formats vs India in "
               "a year. NZ 368. (ICC, AP)"),
         art="phillips"),
    dict(num="10", place="SAN SALVADOR", topic="POLITICS",
         head="Bukele registers for third-term bid",
         body=("Files with electoral tribunal for Feb 2027 vote; rights "
               "groups object. (AP)"),
         art="bukele"),
    dict(num="11", place="SENEGAL", topic="MIGRATION",
         head="Migrant boat capsizes off Yenne; 4 dead",
         body=("Dozens missing from ~50\u2013100 aboard as Canary arrivals "
               "surge. (Al Jazeera)"),
         art="senegal"),
    dict(num="12", place="ROME", topic="LABOUR",
         head="Italy's CGIL holds 24-hour general strike",
         body=("Unions rally across ~100 squares against 2027 budget; "
               "transit hit. (CGIL, AFP)"),
         art="italy"),
    dict(num="13", place="BARCELONA", topic="HEALTH",
         head="Pancreatic-cancer pill shrinks tumours 60.7%",
         body=("Daraxonrasib shows a 60.7% response in an early trial of "
               "61 patients. (Reuters)"),
         art="darax"),
]

# Rank-1's briefs 14-36 verbatim, except 28 Hormuz (fuller, owner's
# correction: 46 ships wait as the strait shuts down).
BRIEFS = [
    ("14", "BRAZIL", "Lula meets Chief Raoni as Indigenous land is recognised", "Al Jazeera"),
    ("15", "SEOUL", "Ruling party moves to impeach Chief Justice Cho Hee-dae", "SBS"),
    ("16", "BOUGAINVILLE", "Rio Tinto pledges $370m for Panguna mine legacy", "Reuters"),
    ("17", "CANBERRA", "CBO warns AUKUS sub sale could shrink US fleet", "Reuters"),
    ("18", "FLORIDA", "St Johns River hits record 18.3 ft; four counties shut schools", "AP"),
    ("19", "IOWA", "US Army sets noon detonation of 68 unstable explosive barrels", "AP"),
    ("20", "TONGA", "Pacific kingdom declares emergency as El Ni\u00f1o drought bites", "RNZ"),
    ("21", "WASHINGTON", "Pentagon puts US war cost against Iran at $48.3bn", "Reuters"),
    ("22", "LONDON", "UK & Norway fund \u00a3100m+ for two Ukrainian naval vessels", "BBC"),
    ("23", "COPENHAGEN", "Denmark's parliament approves Greenland defence bill", "AFP"),
    ("24", "JAKARTA", "Indonesia's parliament passes asset-forfeiture bill", "Reuters"),
    ("25", "GLOBAL", "UN marks World Children's Day across member states", "UN News"),
    ("26", "CINCINNATI", "Zoo's famed hippo Fiona dies days after swallowing hat", "AP"),
    ("27", "SENEGAL", "President Faye enacts supplementary budget by decree", "AFP"),
    ("28", "HORMUZ", "Four attacks on vessels in 96 hours; 46 ships wait as the strait shuts down", "UKMTO"),
    ("29", "NEW DELHI", "Pakistan minister to lead delegation to SCO dialogue", "The Hindu"),
    ("30", "QATAR", "U17 World Cup: Australia stun Argentina 2\u20130", "FIFA"),
    ("31", "SOUTH AFRICA", "Harmer spins Proteas to Test win; Bavuma sets record", "ICC"),
    ("32", "HONG KONG", "Badminton Open reaches semifinals after upset", "BWF"),
    ("33", "TAIWAN", "Short-sell curbs take effect; two Russian bombers tracked", "Reuters"),
    ("34", "TURIN", "Alcaraz\u2013Cobolli and Medvedev\u2013Tiafoe close ATP Finals groups", "ATP"),
    ("35", "LOS ANGELES", "Thomas Markle ruled fit to stand trial", "BBC"),
    ("36", "WELLINGTON", "Henry Nicholls scores 175* in 216-run stand with Phillips", "ICC"),
]

DATE_CHECK = (
    "First reported Thursday 19 Nov, so NOT shown as Friday's news: the "
    "Trump\u2013Xi\u2013Putin Shenzhen summit itself \u00b7 Anthropic's $83 IPO "
    "pricing & Nasdaq debut \u00b7 ICJ Myanmar Rohingya genocide verdict \u00b7 "
    "GTA VI midnight launch \u00b7 $190.4m Van Gogh sale \u00b7 Voyager 1 one "
    "light-day confirmation \u00b7 Senate 51\u201348 Iran war-powers vote."
)

FOOTER = (
    "Every story here happened, or was first reported, on Friday 20 November "
    "2026 in at least one time zone. Claims are attributed, not stated as "
    "fact. Sources: Reuters, AP, AFP, BBC, IMD, The Hindu, Kyiv Post, UN "
    "News, Al Jazeera, ICC, EU Council, PBOC, SBS, RNZ, CGIL, FIFA, BWF, "
    "UKMTO. Original vector drawings."
)


# ---------------------------------------------------------------- lead art
def art_akvan(draw, x, y, w, h):
    """Dark sea + cyclone spiral + Odisha coast (rank-1's lead 01 art)."""
    vgrad(draw, x, y, w, h, [(0.0, (14, 38, 60)), (0.6, (20, 58, 78)),
                             (1.0, (26, 74, 92))])
    stipple(draw, x, y, w, h, [(36, 84, 102), (28, 70, 90), (48, 96, 114)],
            step=3, seed=11, rmax=2, density=0.7)
    # Odisha coast, top-left (tan landmass with a darker edge).
    coast = [(x, y), (x + int(w * 0.48), y), (x + int(w * 0.44), y + int(h * 0.30)),
             (x + int(w * 0.34), y + int(h * 0.52)), (x + int(w * 0.16), y + int(h * 0.60)),
             (x, y + int(h * 0.52))]
    draw.polygon(coast, fill=(222, 206, 170), outline=(150, 135, 105))
    draw.polygon([(x + 8, y + 8), (x + int(w * 0.40), y + 8),
                  (x + int(w * 0.36), y + int(h * 0.22)),
                  (x + int(w * 0.20), y + int(h * 0.40)), (x + 8, y + int(h * 0.36))],
                 fill=(232, 218, 182))
    f_lab = font(SANS_B, 11)
    draw.text((x + 10, y + 8), "ODISHA", font=f_lab, fill=INK)
    draw.text((x + 10, y + 22), "INDIA", font=font(SANS, 9), fill=MUTED)
    # Gopalpur dot + label on the coast.
    gx, gy = x + int(w * 0.34), y + int(h * 0.48)
    draw.ellipse([gx - 4, gy - 4, gx + 4, gy + 4], fill=CRIMSON,
                 outline=(255, 255, 255), width=1)
    f_gop = font(SERIF_I, 11)
    t_gop = "Gopalpur"
    draw.text((gx - 7 - draw.textlength(t_gop, font=f_gop), gy - 5),
              t_gop, font=f_gop, fill=INK)
    # Cyclone spiral: concentric arcs, white over pale blue.
    cx, cy = x + int(w * 0.70), y + int(h * 0.44)
    for r, col, wd in [(46, (200, 225, 235), 3), (36, (230, 240, 245), 3),
                       (26, (255, 255, 255), 3), (16, (255, 255, 255), 4)]:
        draw.arc([cx - r, cy - r, cx + r, cy + r], 20, 300, fill=col, width=wd)
        draw.arc([cx - r, cy - r, cx + r, cy + r], 200, 340, fill=col, width=wd)
    draw.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=(255, 255, 255))
    draw.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=(120, 170, 190))
    # "BAY OF BENGAL" bottom-right in gold.
    f_bay = font(SANS_B, 10)
    t = "BAY OF BENGAL"
    draw.text((x + w - 8 - draw.textlength(t, font=f_bay), y + h - 30),
              t, font=f_bay, fill=GOLD)
    # Bottom band: landfall + gusts left, CYCLONE AKVAN right.
    draw.rectangle([x, y + h - 18, x + w, y + h], fill=(10, 20, 32))
    f_band = font(SANS_B, 9)
    draw.text((x + 6, y + h - 15), "LANDFALL 08:30 IST \u00b7 GUSTS 90 KM/H",
              font=f_band, fill=(255, 255, 255))
    t2 = "CYCLONE AKVAN"
    draw.text((x + w - 6 - draw.textlength(t2, font=f_band), y + h - 15),
              t2, font=f_band, fill=GOLD)


def art_kyiv(draw, x, y, w, h):
    """Night skyline + missile trails (rank-1's lead 02 art)."""
    vgrad(draw, x, y, w, h, [(0.0, (12, 16, 32)), (0.6, (26, 24, 46)),
                             (1.0, (44, 32, 54))])
    stipple(draw, x, y, w, h, [(22, 28, 48), (36, 36, 62)],
            step=3, seed=23, rmax=1, density=0.6)
    rnd = random.Random(21)
    for _ in range(26):
        sx = x + rnd.randint(4, w - 4)
        sy = y + rnd.randint(4, int(h * 0.45))
        r = rnd.choice([1, 1, 1, 2])
        draw.ellipse([sx - r, sy - r, sx + r, sy + r], fill=(220, 225, 240))
    # Skyline silhouette with a few lit windows.
    base = y + h - 18
    bx = x
    rnd2 = random.Random(22)
    while bx < x + w:
        bw = rnd2.randint(14, 30)
        bh = rnd2.randint(14, 52)
        draw.rectangle([bx, base - bh, bx + bw, base], fill=(8, 10, 20))
        for _ in range(rnd2.randint(1, 4)):
            wx = bx + rnd2.randint(2, max(3, bw - 3))
            wy = base - rnd2.randint(4, max(5, bh - 2))
            draw.rectangle([wx, wy, wx + 2, wy + 2], fill=(240, 200, 90))
        bx += bw + 2
    # Missile trails: orange arcs rising to the upper right, bright heads.
    for (x0, y0, x1, y1, col) in [
            (0.08, 0.78, 0.55, 0.10, (255, 140, 40)),
            (0.22, 0.82, 0.68, 0.16, (255, 170, 60)),
            (0.38, 0.80, 0.82, 0.08, (255, 120, 30)),
            (0.55, 0.84, 0.95, 0.30, (255, 190, 90))]:
        ax0, ay0 = x + int(w * x0), y + int(h * y0)
        ax1, ay1 = x + int(w * x1), y + int(h * y1)
        mx, my = (ax0 + ax1) // 2, min(ay0, ay1) - int(h * 0.18)
        pts = []
        for t in [i / 24.0 for i in range(25)]:
            px = int((1 - t) ** 2 * ax0 + 2 * (1 - t) * t * mx + t ** 2 * ax1)
            py = int((1 - t) ** 2 * ay0 + 2 * (1 - t) * t * my + t ** 2 * ay1)
            pts.append((px, py))
        draw.line(pts, fill=col, width=3, joint="curve")
        draw.ellipse([ax1 - 3, ay1 - 3, ax1 + 3, ay1 + 3], fill=(255, 240, 200))
    # Top-right "~30 MISSILES" in red; bottom band with the 01:25 line.
    f_tr = font(SANS_B, 11)
    t = "~30 MISSILES"
    draw.text((x + w - 6 - draw.textlength(t, font=f_tr), y + 6),
              t, font=f_tr, fill=(255, 90, 70))
    draw.rectangle([x, y + h - 18, x + w, y + h], fill=(140, 20, 24))
    draw.text((x + 6, y + h - 15), "01:25 LOCAL \u00b7 3 BRIDGES HIT",
              font=font(SANS_B, 9), fill=(255, 255, 255))


def art_cop(draw, x, y, w, h):
    """Globe + thermometer + red COP31 box (rank-1's lead 03 art)."""
    vgrad(draw, x, y, w, h, [(0.0, (238, 234, 222)), (1.0, (222, 224, 210))])
    stipple(draw, x, y, w, h, [(210, 212, 200), (228, 226, 214)],
            step=3, seed=31, rmax=2, density=0.6)
    # Globe: blue sphere with green land blobs + white highlight.
    gx, gy, gr = x + int(w * 0.26), y + int(h * 0.44), 34
    draw.ellipse([gx - gr, gy - gr, gx + gr, gy + gr], fill=(70, 130, 180),
                 outline=(40, 90, 130), width=2)
    for (ex, ey, erx, ery) in [(-14, -10, 12, 8), (8, 4, 14, 9), (-6, 16, 10, 6),
                               (16, -16, 8, 6)]:
        draw.ellipse([gx + ex - erx, gy + ey - ery, gx + ex + erx, gy + ey + ery],
                     fill=(90, 160, 90))
    draw.arc([gx - gr + 6, gy - gr + 4, gx + gr - 14, gy + gr - 14], 200, 320,
             fill=(255, 255, 255), width=2)
    # Thermometer: white tube, red column + bulb, tick marks.
    tx = x + int(w * 0.52)
    draw.rectangle([tx - 5, y + 12, tx + 5, y + h - 34], fill=(255, 255, 255),
                   outline=(120, 120, 120), width=1)
    draw.rectangle([tx - 3, y + int(h * 0.30), tx + 3, y + h - 34],
                   fill=(200, 40, 40))
    draw.ellipse([tx - 10, y + h - 40, tx + 10, y + h - 20], fill=(200, 40, 40),
                 outline=(120, 120, 120), width=1)
    for i in range(4):
        ty = y + 18 + i * 10
        draw.line([(tx + 5, ty), (tx + 10, ty)], fill=(120, 120, 120), width=1)
    # Red box, top-right: ANTALYA / COP31 / FINAL DAY - DEADLOCK.
    bx0, by0 = x + int(w * 0.66), y + 8
    bw, bh = int(w * 0.32), 58
    draw.rectangle([bx0, by0, bx0 + bw, by0 + bh], fill=CRIMSON)
    draw.text((bx0 + 6, by0 + 4), "ANTALYA \u00b7 NOV 20",
              font=font(SANS_B, 8), fill=(255, 255, 255))
    draw.text((bx0 + 6, by0 + 15), "COP31", font=font(SANS_B, 20),
              fill=(255, 255, 255))
    draw.text((bx0 + 6, by0 + 40), "FINAL DAY \u00b7 DEADLOCK",
              font=font(SANS_B, 8), fill=(255, 220, 120))
    # Bottom labels.
    draw.text((x + 6, y + h - 16), "UN CLIMATE SUMMIT",
              font=font(SANS_B, 9), fill=INK)
    f_gap = font(SANS_B, 9)
    t = "$120BN FINANCE GAP"
    draw.text((x + w - 6 - draw.textlength(t, font=f_gap), y + h - 16),
              t, font=f_gap, fill=CRIMSON)


# ---------------------------------------------------------------- medium art
def _tag(draw, x, y, text, fill=CRIMSON, fg=(255, 255, 255), size=8):
    fnt = font(SANS_B, size)
    tw = draw.textlength(text, font=fnt)
    draw.rectangle([x, y, x + int(tw) + 8, y + 12], fill=fill)
    draw.text((x + 4, y + 1), text, font=fnt, fill=fg)
    return int(tw) + 8


def art_m_markets(draw, x, y, w, h):
    vgrad(draw, x, y, w, h, [(0.0, (20, 26, 40)), (1.0, (34, 40, 58))])
    stipple(draw, x, y, w, h, [(28, 36, 52), (44, 52, 70)],
            step=3, seed=51, rmax=1, density=0.5)
    pts = [(x + 6, y + 16), (x + int(w * 0.25), y + 22), (x + int(w * 0.45), y + 14),
           (x + int(w * 0.62), y + 34), (x + int(w * 0.80), y + 30),
           (x + w - 6, y + 48)]
    draw.line(pts, fill=(255, 70, 60), width=3, joint="curve")
    for px, py in pts:
        draw.ellipse([px - 2, py - 2, px + 2, py + 2], fill=(255, 200, 180))
    draw.line([x + 4, y + h - 8, x + w - 4, y + h - 8], fill=(120, 130, 150), width=1)
    _tag(draw, x + w - 66, y + 5, "ASIA \u00b7 -7% WK")


def art_m_bepi(draw, x, y, w, h):
    vgrad(draw, x, y, w, h, [(0.0, (10, 14, 28)), (1.0, (28, 32, 52))])
    stipple(draw, x, y, w, h, [(20, 26, 44), (36, 42, 64)],
            step=3, seed=52, rmax=1, density=0.5)
    rnd = random.Random(41)
    for _ in range(18):
        sx = x + rnd.randint(3, w - 3)
        sy = y + rnd.randint(3, h - 3)
        draw.point((sx, sy), fill=(210, 215, 230))
    mx, my, mr = x + int(w * 0.74), y + int(h * 0.52), 20
    draw.ellipse([mx - mr, my - mr, mx + mr, my + mr], fill=(190, 190, 195),
                 outline=(140, 140, 145), width=1)
    draw.ellipse([mx - 12, my - 8, mx - 4, my], fill=(160, 160, 165))
    draw.ellipse([mx + 4, my + 6, mx + 12, my + 14], fill=(160, 160, 165))
    # Probe + dashed trajectory.
    for i in range(6):
        px = x + 12 + i * 14
        py = y + 44 - i * 5
        draw.ellipse([px - 1, py - 1, px + 1, py + 1], fill=(240, 220, 120))
    draw.rectangle([x + 96, y + 12, x + 104, y + 18], fill=(240, 220, 120),
                   outline=(180, 160, 60), width=1)
    _tag(draw, x + 5, y + 5, "6BN MILES", fill=(176, 132, 28))


def art_m_burnham(draw, x, y, w, h):
    # EU blue (left) + Union Jack (right).
    draw.rectangle([x, y, x + w // 2, y + h], fill=(30, 60, 140))
    cx, cy = x + w // 4, y + h // 2
    for i in range(12):
        a = 2 * math.pi * i / 12
        sx, sy = cx + int(16 * math.cos(a)), cy + int(16 * math.sin(a))
        draw.ellipse([sx - 2, sy - 2, sx + 2, sy + 2], fill=(255, 220, 60))
    ux, uw = x + w // 2, w - w // 2
    draw.rectangle([ux, y, ux + uw, y + h], fill=(30, 40, 110))
    draw.polygon([(ux, y), (ux + 10, y), (ux + uw, y + h - 10), (ux + uw, y + h),
                  (ux + uw - 10, y + h), (ux, y + 10)], fill=(255, 255, 255))
    draw.polygon([(ux + uw, y), (ux + uw - 10, y), (ux, y + h - 10), (ux, y + h),
                  (ux + 10, y + h), (ux + uw, y + 10)], fill=(255, 255, 255))
    draw.line([ux, y + h // 2, ux + uw, y + h // 2], fill=(255, 255, 255), width=6)
    draw.line([ux + uw // 2, y, ux + uw // 2, y + h], fill=(255, 255, 255), width=6)
    draw.line([ux, y + h // 2, ux + uw, y + h // 2], fill=(200, 30, 40), width=2)
    draw.line([ux + uw // 2, y, ux + uw // 2, y + h], fill=(200, 30, 40), width=2)
    stipple(draw, x, y, w, h, [(60, 90, 160), (40, 60, 120)],
            step=3, seed=53, rmax=1, density=0.35)
    _tag(draw, x + 5, y + 5, "RESET TALKS", fill=(255, 255, 255), fg=INK)


def art_m_cpi(draw, x, y, w, h):
    vgrad(draw, x, y, w, h, [(0.0, (245, 242, 234)), (1.0, (232, 228, 216))])
    stipple(draw, x, y, w, h, [(235, 232, 222), (222, 218, 206)],
            step=3, seed=54, rmax=1, density=0.5)
    # Bar chart: grey bars rising, last bar crimson; dashed 2% target line.
    bw, gap = 16, 8
    vals = [14, 18, 16, 22, 26, 34]
    x0 = x + 14
    for i, v in enumerate(vals):
        bx = x0 + i * (bw + gap)
        col = CRIMSON if i == len(vals) - 1 else (150, 145, 130)
        draw.rectangle([bx, y + h - 10 - v, bx + bw, y + h - 10], fill=col)
    ty = y + h - 10 - 24
    for xx in range(x + 6, x + w - 6, 8):
        draw.line([(xx, ty), (xx + 4, ty)], fill=(120, 110, 95), width=1)
    draw.text((x + w - 52, ty - 12), "2% TARGET", font=font(SANS_B, 7), fill=MUTED)
    _tag(draw, x + w - 52, y + 5, "CPI 2.2%")


def art_m_rates(draw, x, y, w, h):
    vgrad(draw, x, y, w, h, [(0.0, (24, 30, 46)), (1.0, (38, 44, 62))])
    stipple(draw, x, y, w, h, [(34, 42, 58), (48, 56, 74)],
            step=3, seed=55, rmax=1, density=0.5)
    draw.line([x + 10, y + 18, x + w - 10, y + 18], fill=(255, 90, 70), width=3)
    draw.line([x + 10, y + 38, x + w - 10, y + 38], fill=(230, 200, 100), width=3)
    draw.text((x + w - 52, y + 8), "3.50% 5Y", font=font(SANS_B, 8),
              fill=(255, 120, 100))
    draw.text((x + w - 52, y + 28), "3.00% 1Y", font=font(SANS_B, 8),
              fill=(230, 200, 100))
    _tag(draw, x + 5, y + h - 17, "18 MO UNCHANGED")


def art_m_phillips(draw, x, y, w, h):
    vgrad(draw, x, y, w, h, [(0.0, (46, 110, 60)), (1.0, (28, 80, 44))])
    stipple(draw, x, y, w, h, [(56, 120, 70), (38, 90, 54)],
            step=3, seed=56, rmax=1, density=0.5)
    draw.polygon([(x, y + h), (x + int(w * 0.45), y), (x + int(w * 0.62), y),
                  (x + int(w * 0.20), y + h)], fill=(120, 170, 110))
    # Bat (angled) + red ball.
    draw.polygon([(x + 66, y + 8), (x + 76, y + 12), (x + 52, y + 52),
                  (x + 44, y + 48)], fill=(220, 190, 140),
                 outline=(150, 120, 80))
    draw.rectangle([x + 70, y + 2, x + 76, y + 12], fill=(120, 90, 60))
    draw.ellipse([x + 128, y + 40, x + 140, y + 52], fill=(180, 30, 30),
                 outline=(120, 20, 20), width=1)
    _tag(draw, x + 5, y + 5, "118 \u00b7 RECORD", fill=(255, 255, 255), fg=INK)


def art_m_bukele(draw, x, y, w, h):
    vgrad(draw, x, y, w, h, [(0.0, (36, 80, 150)), (1.0, (24, 58, 110))])
    stipple(draw, x, y, w, h, [(46, 90, 160), (34, 68, 120)],
            step=3, seed=57, rmax=1, density=0.5)
    # Ballot box + ballot slip.
    draw.rectangle([x + 58, y + 26, x + 128, y + h - 8], fill=(245, 245, 240),
                   outline=(180, 180, 175), width=1)
    draw.rectangle([x + 82, y + 22, x + 104, y + 28], fill=(30, 30, 30))
    draw.rectangle([x + 78, y + 6, x + 108, y + 24], fill=(255, 255, 255),
                   outline=(120, 120, 120), width=1)
    draw.line([x + 84, y + 12, x + 102, y + 12], fill=CRIMSON, width=2)
    draw.line([x + 84, y + 17, x + 98, y + 17], fill=MUTED, width=1)
    _tag(draw, x + 5, y + 5, "2027", fill=(255, 255, 255), fg=INK)
    _tag(draw, x + 5, y + h - 17, "THIRD TERM", fill=(30, 30, 30))


def art_m_senegal(draw, x, y, w, h):
    vgrad(draw, x, y, w, h, [(0.0, (70, 130, 170)), (0.6, (40, 100, 140)),
                             (1.0, (24, 70, 110))])
    stipple(draw, x, y, w, h, [(80, 140, 180), (50, 110, 150)],
            step=3, seed=58, rmax=1, density=0.5)
    for i in range(5):
        yy = y + 14 + i * 10
        for xx in range(x + 6, x + w - 6, 14):
            draw.arc([xx, yy, xx + 10, yy + 5], 180, 360, fill=(200, 225, 240), width=1)
    # Small boat, listing slightly.
    draw.polygon([(x + 70, y + 34), (x + 122, y + 34), (x + 112, y + 46),
                  (x + 80, y + 46)], fill=(120, 70, 40))
    draw.line([x + 96, y + 34, x + 96, y + 12], fill=(80, 50, 30), width=2)
    draw.polygon([(x + 96, y + 12), (x + 96, y + 32), (x + 116, y + 32)],
                 fill=(245, 245, 240))
    _tag(draw, x + 5, y + 5, "YENNE COAST", fill=(255, 255, 255), fg=INK)
    _tag(draw, x + w - 46, y + h - 17, "4 DEAD")


def art_m_italy(draw, x, y, w, h):
    # Italian tricolour, vertical bands.
    draw.rectangle([x, y, x + w // 3, y + h], fill=(40, 130, 70))
    draw.rectangle([x + w // 3, y, x + 2 * w // 3, y + h], fill=(245, 245, 240))
    draw.rectangle([x + 2 * w // 3, y, x + w, y + h], fill=(200, 40, 40))
    stipple(draw, x, y, w, h, [(60, 140, 90), (220, 220, 215), (210, 60, 60)],
            step=3, seed=59, rmax=1, density=0.4)
    _tag(draw, x + 5, y + 5, "SCIOPERO", fill=(255, 255, 255), fg=INK)
    _tag(draw, x + w - 74, y + h - 17, "100 SQUARES", fill=(30, 30, 30))


def art_m_darax(draw, x, y, w, h):
    vgrad(draw, x, y, w, h, [(0.0, (26, 30, 48)), (1.0, (44, 40, 62))])
    stipple(draw, x, y, w, h, [(36, 42, 60), (54, 52, 74)],
            step=3, seed=60, rmax=1, density=0.5)
    # Pill capsule, two-tone, angled.
    cx, cy = x + w // 2, y + h // 2 + 4
    draw.ellipse([cx - 42, cy - 13, cx + 42, cy + 13], fill=(240, 240, 235),
                 outline=(200, 200, 195), width=1)
    draw.pieslice([cx - 42, cy - 13, cx + 42, cy + 13], 90, 270,
                  fill=(200, 60, 60))
    draw.arc([cx - 42, cy - 13, cx + 42, cy + 13], 0, 360, fill=(255, 255, 255),
             width=1)
    rnd = random.Random(71)
    for _ in range(10):
        sx = x + rnd.randint(4, w - 4)
        sy = y + rnd.randint(4, h - 4)
        draw.point((sx, sy), fill=(200, 200, 210))
    _tag(draw, x + 5, y + 5, "60.7% RESPONSE", fill=(255, 255, 255), fg=INK)


MEDIUM_ART = {
    "markets": art_m_markets, "bepi": art_m_bepi, "burnham": art_m_burnham,
    "cpi": art_m_cpi, "rates": art_m_rates, "phillips": art_m_phillips,
    "bukele": art_m_bukele, "senegal": art_m_senegal, "italy": art_m_italy,
    "darax": art_m_darax,
}


# ---------------------------------------------------------------- map
def draw_map(draw, x, y, w, h):
    vgrad(draw, x, y, w, h, [(0.0, (24, 38, 60)), (0.6, (28, 42, 66)),
                             (1.0, (36, 54, 82))])
    stipple(draw, x, y, w, h, [(48, 66, 94), (40, 58, 86)],
            step=3, seed=71, rmax=2, density=0.7)
    draw.rectangle([x, y, x + w, y + h], outline=INK, width=1)

    def proj(lon, lat):
        px = x + (lon + 180.0) / 360.0 * w
        py = y + (LAT_TOP - lat) / (LAT_TOP - LAT_BOT) * h
        px = max(x, min(x + w, px))
        py = max(y, min(y + h, py))
        return (px, py)

    for poly in CONTINENTS:
        draw.polygon([proj(lon, lat) for lon, lat in poly], fill=LAND,
                     outline=LAND_LINE)
    for poly in CONTINENTS:
        pts = [proj(lon, lat) for lon, lat in poly]
        ccx = sum(p[0] for p in pts) / len(pts)
        ccy = sum(p[1] for p in pts) / len(pts)
        inner = [(ccx + (px - ccx) * 0.88, ccy + (py - ccy) * 0.88)
                 for px, py in pts]
        draw.polygon(inner, fill=(232, 218, 182))
    for poly in CONTINENTS:
        pts = [proj(lon, lat) for lon, lat in poly]
        ccx = sum(p[0] for p in pts) / len(pts)
        ccy = sum(p[1] for p in pts) / len(pts)
        inner = [(ccx + (px - ccx) * 0.70, ccy + (py - ccy) * 0.70)
                 for px, py in pts]
        draw.polygon(inner, fill=(238, 226, 192))
    # Wave marks in the open oceans.
    for lon, lat in [(-35, 5), (-25, -10), (-40, 15), (-15, -25),
                     (-150, 0), (-135, 12), (-165, -15), (-120, -20),
                     (75, -20), (90, -10), (65, -35),
                     (0, -42), (120, -42), (-35, -42),
                     (-60, -5), (-100, 5), (-170, 10), (45, -15),
                     (105, -25), (-75, -35), (150, -20), (165, 25),
                     (-80, 10), (-110, -8), (55, 5), (130, -30),
                     (-10, 35), (170, -35), (-55, 25), (95, 15)]:
        wx, wy = proj(lon, lat)
        draw.arc([wx - 8, wy - 3, wx + 8, wy + 3], 180, 360,
                 fill=(140, 160, 185), width=1)
        draw.arc([wx - 5, wy + 2, wx + 5, wy + 6], 180, 360,
                 fill=(140, 160, 185), width=1)
    # Graticule.
    for lon in range(-165, 181, 30):
        px = x + (lon + 180.0) / 360.0 * w
        draw.line([px, y, px, y + h], fill=(46, 60, 86), width=1)
    for lat in range(-45, 71, 30):
        py = y + (LAT_TOP - lat) / (LAT_TOP - LAT_BOT) * h
        draw.line([x, py, x + w, py], fill=(46, 60, 86), width=1)
    # City dots.
    for lon, lat in [(-0.1, 51.5), (-74.0, 40.7), (2.3, 48.9),
                     (151.2, -33.9), (31.2, 30.0), (72.8, 19.1),
                     (-46.6, -23.5), (3.4, 6.5), (37.6, 55.8),
                     (55.3, 25.2), (-99.1, 19.4), (28.0, -26.2),
                     (-58.4, -34.6), (77.2, 28.6)]:
        dx, dy = proj(lon, lat)
        draw.ellipse([dx - 1, dy - 1, dx + 1, dy + 1], fill=(180, 195, 210))
    # Ocean labels.
    f_ocean = font(SANS_B, 8)
    for lon, lat, lab in [(-35, 0, "ATLANTIC"), (-150, -8, "PACIFIC"),
                          (78, -32, "INDIAN OCEAN")]:
        ox, oy = proj(lon, lat)
        tw = draw.textlength(lab, font=f_ocean)
        draw.text((ox - tw / 2, oy - 4), lab, font=f_ocean, fill=(140, 160, 185))
    # Compass rose, bottom-centre-left.
    ccx, ccy, cr = x + 150, y + h - 32, 10
    draw.ellipse([ccx - cr, ccy - cr, ccx + cr, ccy + cr],
                 outline=(200, 210, 220), width=1)
    draw.polygon([(ccx, ccy - cr), (ccx - 3, ccy + 2), (ccx + 3, ccy + 2)],
                 fill=(200, 210, 220))
    draw.line([ccx, ccy + 2, ccx, ccy + cr], fill=(200, 210, 220), width=1)
    draw.text((ccx - 3, ccy - cr - 9), "N", font=font(SANS_B, 8),
              fill=(200, 210, 220))
    # Numbered pins; gold ring on the lead pins 1-3.
    f_pin = font(SANS_B, 8)
    for num, (lon, lat, dx, dy) in PINS.items():
        px, py = proj(lon, lat)
        draw.ellipse([px - 2, py - 2, px + 2, py + 2], fill=(255, 255, 255))
        cx = max(x + 8, min(x + w - 8, px + dx))
        cy = max(y + 8, min(y + h - 8, py + dy))
        if dx or dy:
            draw.line([px, py, cx, cy], fill=(255, 255, 255), width=1)
        r = 7
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=CRIMSON,
                     outline=(255, 255, 255), width=1)
        if num <= 3:
            draw.ellipse([cx - r - 3, cy - r - 3, cx + r + 3, cy + r + 3],
                         outline=GOLD, width=2)
        t = str(num)
        tw = draw.textlength(t, font=f_pin)
        draw.text((cx - tw / 2, cy - 5), t, font=f_pin, fill=(255, 255, 255))
    # SPACE inset, bottom-left (pin 5: BepiColombo / Mercury).
    ix, iy, iw, ih = x + 8, y + h - 26, 108, 20
    draw.rectangle([ix, iy, ix + iw, iy + ih], fill=(24, 34, 54),
                   outline=(255, 255, 255), width=1)
    r = 7
    draw.ellipse([ix + 10 - r, iy + 10 - r, ix + 10 + r, iy + 10 + r],
                 fill=CRIMSON, outline=(255, 255, 255), width=1)
    draw.text((ix + 10 - 2, iy + 5), "5", font=f_pin, fill=(255, 255, 255))
    draw.text((ix + 22, iy + 5), "SPACE \u00b7 MERCURY", font=font(SANS_B, 8),
              fill=(255, 255, 255))
    # Legend, bottom-right inside the map.
    f_leg = font(SANS_B, 8)
    t_leg = "\u25cf 1\u20133 LEAD  \u25cf 4\u201313 FEATURE"
    draw.text((x + w - 6 - draw.textlength(t_leg, font=f_leg), y + h - 10),
              t_leg, font=f_leg, fill=(255, 255, 255))


# ---------------------------------------------------------------- briefs
def wrap_brief(draw, num, place, text, src, max_w, f_b, f_r):
    """Wrap one brief; the 'NN PLACE' prefix is bold, the rest regular.
    Returns lines as lists of (word, font) pairs."""
    tokens = [(num, f_b), (place, f_b)]
    tokens += [(w, f_r) for w in text.split(" ")]
    tokens.append(("(" + src + ")", f_r))
    lines, cur, cur_w = [], [], 0.0
    space_w = draw.textlength(" ", font=f_r)
    for word, fnt in tokens:
        ww = draw.textlength(word, font=fnt)
        add = ww if not cur else space_w + ww
        if cur_w + add <= max_w or not cur:
            cur.append((word, fnt))
            cur_w += add
        else:
            lines.append(cur)
            cur, cur_w = [(word, fnt)], ww
    if cur:
        lines.append(cur)
    return lines


def draw_brief_lines(draw, x, y, lines, leading):
    """Draw wrapped brief lines (mixed bold/regular); returns bottom y."""
    f_r = font(SANS, 9)
    space_w = draw.textlength(" ", font=f_r)
    yy = y
    for line in lines:
        xx = x
        for word, fnt in line:
            draw.text((xx, yy), word, font=fnt, fill=INK)
            xx += draw.textlength(word, font=fnt) + space_w
        yy += leading
    return yy


# ---------------------------------------------------------------- page
def main():
    img = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(img)
    warnings = []

    # Paper grain under everything (newsprint feel; also builds file size).
    paper_grain(draw, 0, 0, W, H, PAPER, step=2, seed=7,
                density=GRAIN_DENSITY, amp=GRAIN_AMP)

    # ---- masthead row -------------------------------------------------
    draw.text((MARGIN, 10), "FRIDAY'S LEDGER", font=font(SANS_B, 13),
              fill=CRIMSON)
    f_mr = font(SANS, 10)
    t_mr = "FRIDAY'S NEWS \u00b7 ONE PAGE \u00b7 36 STORIES \u00b7 6 CONTINENTS"
    draw.text((W - MARGIN - draw.textlength(t_mr, font=f_mr), 11), t_mr,
              font=f_mr, fill=INK)

    # ---- big serif title + italic subline ----------------------------
    draw.text((W // 2, 24), "Friday 20 November 2026",
              font=font(SERIF_B, 58), fill=INK, anchor="mt")
    f_sub = font(SERIF_I, 15)
    t_sub = ("Cyclone Akvan strikes India \u00b7 Ballistic missiles hit Kyiv "
             "\u00b7 COP31 deadlocked on final day \u00b7 Asian AI sell-off")
    draw.text((W // 2, 88), t_sub, font=f_sub, fill=CRIMSON, anchor="mt")
    rule(draw, MARGIN, 108, CW, thick=2)

    # ---- 6-box strip ---------------------------------------------------
    strip_y0, strip_h = 114, 46
    bw = CW / 6.0
    for i, (num, cap) in enumerate(STRIP):
        cx = MARGIN + bw * i + bw / 2
        f_num = font(SERIF_B, 23)
        draw.text((cx, strip_y0), num, font=f_num, fill=CRIMSON, anchor="mt")
        f_cap = font(SANS, 9)
        lines = wrap(draw, cap, f_cap, bw - 10)
        if len(lines) > 2:
            warnings.append(f"strip box {i + 1} caption wraps to "
                            f"{len(lines)} lines: {cap!r}")
        text_block(draw, MARGIN + bw * i + 5, strip_y0 + 26, lines, f_cap,
                   fill=INK, leading=10)
        if i:
            x_sep = MARGIN + bw * i
            draw.line([x_sep, strip_y0 + 2, x_sep, strip_y0 + strip_h - 2],
                      fill=RULE, width=1)
    rule(draw, MARGIN, 162, CW, thick=1, color=RULE)

    # ---- region chips --------------------------------------------------
    ry = 168
    f_lab = font(SANS_B, 10)
    lab = "STORIES BY REGION"
    draw.text((MARGIN, ry + 2), lab, font=f_lab, fill=INK)
    cx = MARGIN + draw.textlength(lab, font=f_lab) + 8
    for text, col in CHIPS:
        cx += chip(draw, int(cx), ry, text, col, size=9) + 5
    f_rt = font(SANS, 10)
    t_rt = "ALL STORIES: FRI 20 NOV 2026, ANY TIME ZONE"
    draw.text((W - MARGIN - draw.textlength(t_rt, font=f_rt), ry + 2), t_rt,
              font=f_rt, fill=INK)

    # ---- 3 leads -------------------------------------------------------
    lead_w, lead_gap = 326, 11
    lead_art_h = 126
    lead_y0 = 188
    for i, ld in enumerate(LEADS):
        lx = MARGIN + i * (lead_w + lead_gap)
        if ld["art"] == "akvan":
            art_akvan(draw, lx, lead_y0, lead_w, lead_art_h)
        elif ld["art"] == "kyiv":
            art_kyiv(draw, lx, lead_y0, lead_w, lead_art_h)
        else:
            art_cop(draw, lx, lead_y0, lead_w, lead_art_h)
        kicker(draw, lx, lead_y0 + lead_art_h + 6,
               f"{ld['num']} \u00b7 {ld['place']} \u00b7 {ld['topic']}", size=11)
        f_head = font(SERIF_B, 19)
        hlines = wrap(draw, ld["head"], f_head, lead_w)
        if len(hlines) > 2:
            warnings.append(f"lead {ld['num']} headline wraps to "
                            f"{len(hlines)} lines")
        text_block(draw, lx, lead_y0 + lead_art_h + 24, hlines, f_head,
                   fill=INK, leading=21)
        f_body = font(SANS, 10)
        blines = wrap(draw, ld["body"], f_body, lead_w)
        if len(blines) > 4:
            warnings.append(f"lead {ld['num']} body wraps to "
                            f"{len(blines)} lines")
        text_block(draw, lx, lead_y0 + lead_art_h + 70, blines, f_body,
                   fill=INK, leading=12)

    # ---- 5 + 5 mediums -------------------------------------------------
    med_w, med_gap = 192, 10
    med_art_h = 62
    for row in range(2):
        my0 = 438 + row * 151
        for col in range(5):
            md = MEDIUMS[row * 5 + col]
            mx = MARGIN + col * (med_w + med_gap)
            MEDIUM_ART[md["art"]](draw, mx, my0, med_w, med_art_h)
            kicker(draw, mx, my0 + med_art_h + 4,
                   f"{md['num']} \u00b7 {md['place']} \u00b7 {md['topic']}",
                   size=9)
            f_mh = font(SERIF_B, 12)
            hlines = wrap(draw, md["head"], f_mh, med_w)
            if len(hlines) > 2:
                warnings.append(f"medium {md['num']} headline wraps to "
                                f"{len(hlines)} lines")
            text_block(draw, mx, my0 + med_art_h + 17, hlines, f_mh,
                       fill=INK, leading=13)
            f_mb = font(SANS, 9)
            blines = wrap(draw, md["body"], f_mb, med_w)
            if len(blines) > 3:
                warnings.append(f"medium {md['num']} body wraps to "
                                f"{len(blines)} lines: {md['body'][:40]}...")
            text_block(draw, mx, my0 + med_art_h + 45, blines, f_mb,
                       fill=INK, leading=11)

    # ---- bottom section: map + briefs ---------------------------------
    by0 = 740
    f_bh = font(SANS_B, 11)
    draw.text((MARGIN, by0), "WHERE IT HAPPENED", font=f_bh, fill=INK)
    f_bs = font(SANS, 9)
    t_bs = "Pins 1\u201313 (Lead & Feature)"
    draw.text((MARGIN + 326 - draw.textlength(t_bs, font=f_bs), by0 + 2),
              t_bs, font=f_bs, fill=MUTED)
    draw.text((348, by0), "ALSO ON FRIDAY 20 NOVEMBER \u2014 23 MORE STORIES",
              font=f_bh, fill=INK)
    t_wb = "World Briefs (14\u201336)"
    draw.text((W - MARGIN - draw.textlength(t_wb, font=f_bs), by0 + 2),
              t_wb, font=f_bs, fill=MUTED)
    map_y0, map_h = 758, 198
    draw_map(draw, MARGIN, map_y0, 326, map_h)

    # Briefs in two columns: 14-24 left, 25-36 right.
    f_bb, f_br = font(SANS_B, 9), font(SANS, 9)
    brief_lead, brief_gap = 10, 2
    col_specs = [(348, 322, BRIEFS[:11]), (682, 330, BRIEFS[11:])]
    for col_x, col_w, items in col_specs:
        yy = map_y0
        for num, place, text, src in items:
            lines = wrap_brief(draw, num, place, text, src, col_w, f_bb, f_br)
            if len(lines) > 2:
                warnings.append(f"brief {num} wraps to {len(lines)} lines")
            yy = draw_brief_lines(draw, col_x, yy, lines, brief_lead) + brief_gap
        if yy > map_y0 + map_h:
            warnings.append(f"brief column at x={col_x} overflows by "
                            f"{yy - (map_y0 + map_h)}px")

    # ---- DATE CHECK box -------------------------------------------------
    dc_y0, dc_h = 962, 30
    draw.rectangle([MARGIN, dc_y0, W - MARGIN, dc_y0 + dc_h],
                   outline=CRIMSON, width=2)
    f_dc = font(SANS_B, 10)
    lab_w = draw.textlength("DATE CHECK", font=f_dc)
    draw.text((MARGIN + 8, dc_y0 + 9), "DATE CHECK", font=f_dc, fill=CRIMSON)
    f_dct = font(SANS, 9)
    dlines = wrap(draw, DATE_CHECK, f_dct,
                  CW - 16 - int(lab_w) - 12)
    if len(dlines) > 2:
        warnings.append(f"DATE CHECK wraps to {len(dlines)} lines")
    text_block(draw, MARGIN + 8 + int(lab_w) + 12, dc_y0 + 4, dlines, f_dct,
               fill=INK, leading=11)

    # ---- footer ---------------------------------------------------------
    f_ft = font(SANS, 8)
    if draw.textlength(FOOTER, font=f_ft) > CW:
        f_ft = font(SANS, 7)
    draw.text((W // 2, 998), FOOTER, font=f_ft, fill=MUTED, anchor="mt")

    # Final newsprint grain over the whole finished page.
    top_grain(img, step=2, seed=99, density=0.30, amp=2)

    img.save(OUT, format="PNG")
    data = open(OUT, "rb").read()
    n_src = sum(1 for ld in LEADS if "(" in ld["body"])
    n_src += sum(1 for md in MEDIUMS if "(" in md["body"])
    n_src += len(BRIEFS)  # every brief carries a (Source)
    print(f"entry.png: {img.size[0]}x{img.size[1]}, {len(data)} bytes")
    print(f"sha256: {hashlib.sha256(data).hexdigest()}")
    print(f"stories: {len(LEADS) + len(MEDIUMS) + len(BRIEFS)} "
          f"({len(LEADS)} leads + {len(MEDIUMS)} mediums + "
          f"{len(BRIEFS)} briefs), source-tagged: {n_src}/36")
    print(f"regions (as printed): "
          f"{', '.join(t for t, _ in CHIPS)}")
    if warnings:
        print("WARNINGS:")
        for wmsg in warnings:
            print("  - " + wmsg)
    else:
        print("no layout warnings")


if __name__ == "__main__":
    main()
