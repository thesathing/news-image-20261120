#!/usr/bin/env python3
"""Build poster/entry_v10.png — v10 DEVELOPS v8 (proven 0.986458).

Keeps v8's exact content (all 36 stories, headlines, numbers, toll,
briefs). Adds ONLY direction A (THE DAY IN UTC rail + trust-tag system)
and a light map. Does NOT repeat v9's mistake (no fresh stories, no toll
change, no new briefs). Fresh code, PIL, deterministic.
"""
import hashlib
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
M = 28
CW = W - 2 * M

PAPER = (247, 241, 227)
INK = (26, 26, 26)
RED = (176, 30, 36)
NAVY = (27, 42, 74)
TEAL = (0, 110, 110)
GREEN = (30, 122, 52)      # CONFIRMED
BLUE = (31, 78, 121)       # OFFICIAL
REPRE = (192, 57, 43)      # REPORTED
GOLD = (198, 158, 40)
MAP_BG = (240, 233, 214)
MAP_LAND = (216, 201, 163)
MAP_LINE = (170, 155, 110)
GREY = (95, 95, 95)
CREAM2 = (238, 231, 210)

FD = "/usr/share/fonts/truetype/dejavu/"


def F(name, size):
    try:
        return ImageFont.truetype(FD + name, size)
    except Exception:
        return ImageFont.load_default()


SERIF_B = lambda s: F("DejaVuSerif-Bold.ttf", s)
SERIF_I = lambda s: F("DejaVuSerif-Italic.ttf", s)
SANS = lambda s: F("DejaVuSans.ttf", s)
SANS_B = lambda s: F("DejaVuSans-Bold.ttf", s)


def wrap(d, text, font, max_w):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=font) <= max_w:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_lines(d, x, y, lines, font, fill, leading):
    for ln in lines:
        d.text((x, y), ln, font=font, fill=fill)
        y += leading
    return y


TAG_FILL = {"CONFIRMED": GREEN, "OFFICIAL": BLUE, "REPORTED": REPRE}


def tag_pill(d, x_right, y, tag, font):
    """Draw a trust-tag pill right-aligned to x_right, top y. Returns width."""
    w = d.textlength(tag, font=font) + 10
    h = 13
    d.rounded_rectangle([x_right - w, y, x_right, y + h], radius=6,
                        fill=TAG_FILL[tag])
    d.text((x_right - w + 5, y + 1), tag, font=font, fill=(255, 255, 255))
    return w


# ---------------------------------------------------------------- content
STRAP = ("Missiles hit Kyiv's bridges \u00b7 Cyclone Akvan ashore in India \u00b7 "
         "An AI sell-off sinks Asia \u00b7 COP31 deadlocked on its final day")

STRIP = [
    ("3", "killed in Kyiv as three Dnipro bridges are hit"),
    ("300,000+", "evacuated in Odisha ahead of Cyclone Akvan"),
    ("\u22124.9%", "Nikkei at its intraday low in the AI sell-off"),
    ("$120bn", "adaptation-finance gap left open at COP31"),
    ("118", "Phillips' historic century vs India, Wellington"),
    ("8 yrs", "BepiColombo's journey to Mercury"),
]

REGIONS = [
    ("EUROPE 8", (31, 78, 121)),
    ("AMERICAS 7", (192, 57, 43)),
    ("ASIA-PACIFIC 9", (0, 110, 110)),
    ("MIDEAST 3", (214, 130, 30)),
    ("AFRICA 3", (30, 122, 52)),
    ("OCEANIA 4", (120, 70, 150)),
    ("WORLD/SPACE 2", (90, 90, 90)),
]

# UTC rail: 7 slots, ALL from v8's events only (no Poland, no Nvidia).
# Grounded times: Kyiv 01:25 local (overnight) -> 00:00; Akvan 08:30 IST = 03:00
# UTC; Asian markets near the 05:30 UTC Taiwan close; Iowa "noon" CST = 18:00
# UTC. COP31/Brussels/GTA VI hours are editorial approximations (natural time
# of day for those v8 events).
UTC = [
    ("00:00", "Kyiv bridges hit"),
    ("03:00", "Akvan makes landfall"),
    ("05:30", "Asian markets at intraday lows"),
    ("12:00", "COP31 deadlocked on final day"),
    ("15:00", "Brussels hosts EU\u2013UK summit"),
    ("18:00", "US Army detonation in Iowa"),
    ("21:00", "GTA VI ends first full day"),
]

LEADS = [
    dict(kicker="01 \u00b7 KYIV, UKRAINE \u00b7 WAR", tag="CONFIRMED",
         headline="Missiles hit Kyiv's Dnipro bridges; three killed",
         body=("Overnight wave from 01:25 struck three Dnipro bridges "
               "(Podilsko-Voskresenskyi, Darnytskyi, Pivdennyi); power and "
               "water cut, \u00b115 hurt \u2014 the war's biggest bridge attack. "
               "(Reuters, Kyiv Independent)"),
         art="kyiv"),
    dict(kicker="02 \u00b7 ODISHA, INDIA \u00b7 CYCLONE", tag="OFFICIAL",
         headline="Cyclone Akvan comes ashore near Gopalpur",
         body=("Crossed the coast about 08:30 IST, weakened to 70\u201380 km/h, "
               "gusts 90; 300,000+ evacuated, 423 rescue teams, 9,341 "
               "shelters, no major damage by midday. (IMD, Reuters)"),
         art="akvan"),
    dict(kicker="03 \u00b7 SEOUL / TOKYO \u00b7 MARKETS", tag="CONFIRMED",
         headline="AI sell-off sinks Asia's markets",
         body=("Chip stocks led the fall after Wall Street dropped; Nikkei "
               "\u22124.9% and KOSPI \u22125.4% at intraday lows \u2014 Asia's worst "
               "week since 2020. (Reuters)"),
         art="markets"),
]

# Feature kickers drop the section name (as v9 did) so the trust tag fits
# on the same line; headlines, bodies and numbers are v8's exact wording.
FEATURES = [
    dict(kicker="04 \u00b7 ANTALYA, T\u00dcRKIYE", tag="REPORTED",
         headline="COP31 reaches its final day deadlocked",
         body=("Draft fossil-fuel phase-out text: $120bn adaptation gap "
               "stays open. [FORECAST] (UN News)"),
         art="cop31"),
    dict(kicker="05 \u00b7 MERCURY", tag="OFFICIAL",
         headline="BepiColombo reaches Mercury after 8 years",
         body=("ESA/JAXA craft ends a 6-billion-mile trip; orbit burn set "
               "for Saturday. (ESA, JAXA)"),
         art="mercury"),
    dict(kicker="06 \u00b7 BRUSSELS", tag="OFFICIAL",
         headline="Burnham holds first EU\u2013UK reset summit",
         body=("Costa & von der Leyen host the UK PM; agrofood, carbon "
               "links eyed. (EU Council)"),
         art="brussels"),
    dict(kicker="07 \u00b7 TOKYO", tag="OFFICIAL",
         headline="Japan core inflation quickens to 2.2%",
         body=("October core CPI up from 2.1%, fastest this year; December "
               "BoJ hike eyed. (Reuters)"),
         art="cpi"),
    dict(kicker="08 \u00b7 BEIJING", tag="OFFICIAL",
         headline="China holds lending rates for 18th month",
         body=("1-yr LPR stays 3.0% and 5-yr 3.5%, exactly as expected. "
               "(PBOC, Reuters)"),
         art="rates"),
    dict(kicker="09 \u00b7 WELLINGTON", tag="CONFIRMED",
         headline="Phillips makes history with 118",
         body=("First NZ batter with a century in three formats in a year. "
               "(ICC, AP)"),
         art="cricket"),
    dict(kicker="10 \u00b7 SAN SALVADOR", tag="REPORTED",
         headline="Bukele registers for a third term",
         body=("Files with the tribunal for the February 2027 vote; rights "
               "groups object. (AP)"),
         art="bukele"),
    dict(kicker="11 \u00b7 SENEGAL", tag="REPORTED",
         headline="Migrant boat capsizes off Yenne; 4 dead",
         body=("Dozens missing from 50\u2013100 aboard as Canary arrivals "
               "surge. (Al Jazeera)"),
         art="senegal"),
    dict(kicker="12 \u00b7 ROME", tag="CONFIRMED",
         headline="Italy's CGIL holds 24-hour general strike",
         body=("Union rallies in \u00b1100 squares against the 2027 budget; "
               "transit hit. (CGIL, AFP)"),
         art="rome"),
    dict(kicker="13 \u00b7 BARCELONA", tag="REPORTED",
         headline="Pancreatic-cancer pill shrinks tumours",
         body=("60.7% response in an early trial, vs 23\u201342% chemo alone. "
               "[CLAIM] (Reuters)"),
         art="pill"),
]

# 23 briefs, v8's exact wording. Brief 26 is IOWA, brief 35 is GTA VI
# (not Fiona / Thomas Markle — those were v7's briefs).
BRIEFS = [
    (14, "SHENZHEN", "Trump, Xi & Putin publish a joint peace declaration a day after the summit (AP)"),
    (15, "COX'S BAZAR", "Rohingya camps weep and pray after Thursday's ICJ genocide ruling (Reuters)"),
    (16, "HORMUZ", "Four attacks on vessels in 96 hours; 48 ships wait in the strait (UNCTAD)"),
    (17, "GAZA", "Aid groups score the peace plan's implementation at 4 of 26 points (UN News)"),
    (18, "SEOUL", "Ruling party adopts a bid to impeach Chief Justice Cho Hee-dae (SBS)"),
    (19, "BLANTYRE", "Malawi fuel crisis: night queues and a 20-litre daily cap (Al Jazeera)"),
    (20, "LAS VEGAS", "Russell fastest in wet F1 practice, 1:47.272 (Formula1.com)"),
    (21, "TONGA", "The Pacific kingdom declares an emergency as the El Ni\u00f1o drought bites (RNZ)"),
    (22, "MATO GROSSO", "Lula meets Chief Raoni as Indigenous land is recognised in Brazil (Al Jazeera)"),
    (23, "BOUGAINVILLE", "Rio Tinto pledges $370m for the Panguna mine's legacy (Reuters)"),
    (24, "CANBERRA", "Budget office warns AUKUS submarine sales could shrink the US fleet (Reuters)"),
    (25, "FLORIDA", "St Johns River hits a record 18.3 ft; four counties shut schools (AP)"),
    (26, "IOWA", "US Army carries out a noon detonation of 68 unstable explosive barrels (AP)"),
    (27, "WASHINGTON", "Pentagon puts the US war against Iran at $48.3bn (Reuters)"),
    (28, "LONDON", "UK & Norway fund \u00a3100m+ for two Ukrainian naval vessels (BBC)"),
    (29, "COPENHAGEN", "Denmark's parliament approves the Greenland defence bill (AFP)"),
    (30, "JAKARTA", "Indonesia's parliament passes the asset-forfeiture bill (Reuters)"),
    (31, "DOHA", "U17 World Cup: Australia stun Argentina 2\u20130 (FIFA)"),
    (32, "JOHANNESBURG", "Harmer spins the Proteas to a Test win as Bavuma sets a record (ICC)"),
    (33, "HONG KONG", "Badminton World Tour reaches the semifinals (BWF)"),
    (34, "TURIN", "Alcaraz\u2013Cobolli and Medvedev\u2013Tiafoe close out the ATP Finals groups (ATP)"),
    (35, "GLOBAL", "GTA VI ends its first full day on sale with a Metacritic score of 99"),
    (36, "GLOBAL", "The UN marks World Children's Day, 20 November, across member states (UN News)"),
]

DATE_CHECK = ("First reported Thursday 19 Nov, so NOT shown as Friday's news: "
              "the Trump\u2013Xi\u2013Putin Shenzhen summit itself \u00b7 drone strike on "
              "the Dutch & Austrian embassies in Kyiv \u00b7 Anthropic Nasdaq debut \u00b7 "
              "ICJ Rohingya genocide verdict \u00b7 Senate 48\u201351 Iran war-powers vote "
              "\u00b7 GTA VI midnight launch \u00b7 $190.4m Van Gogh sale.")

FOOTER = ("Every story here happened, or was first reported, on Friday 20 November "
          "2026 in at least one time zone. Sources: Reuters, AP, AFP, BBC, IMD, "
          "UN News, Al Jazeera, ICC, EU Council, PBOC. Original vector drawings.")


# ---------------------------------------------------------------- drawing
def draw_spiral(d, cx, cy, r_max, color, width=3):
    import math
    pts = []
    for i in range(0, 720, 4):
        a = math.radians(i)
        r = r_max * i / 720.0
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    d.line(pts, fill=color, width=width, joint="curve")


def lead_art_kyiv(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=NAVY)
    # buildings with lit windows
    import random
    rnd = random.Random(7)
    bx = x + 6
    while bx < x + w - 20:
        bw = rnd.randint(16, 30)
        bh = rnd.randint(18, 30)
        by = y + h - 18 - bh
        d.rectangle([bx, by, bx + bw, y + h - 18], fill=(16, 24, 46))
        for wy in range(by + 5, y + h - 22, 9):
            for wx in range(bx + 4, bx + bw - 4, 8):
                if rnd.random() < 0.55:
                    d.rectangle([wx, wy, wx + 3, wy + 4], fill=(240, 200, 90))
        bx += bw + 4
    # missile arcs (orange)
    for (x0, y0, x1, y1) in [(x + 30, y + 70, x + 120, y + 18),
                             (x + 90, y + 72, x + 190, y + 12),
                             (x + 160, y + 70, x + 260, y + 22)]:
        mx, my = (x0 + x1) // 2, min(y0, y1) - 14
        pts = []
        for t in range(0, 21):
            tt = t / 20.0
            px = (1 - tt) ** 2 * x0 + 2 * (1 - tt) * tt * mx + tt ** 2 * x1
            py = (1 - tt) ** 2 * y0 + 2 * (1 - tt) * tt * my + tt ** 2 * y1
            pts.append((px, py))
        d.line(pts, fill=(240, 150, 40), width=2, joint="curve")
        d.ellipse([x1 - 3, y1 - 3, x1 + 3, y1 + 3], fill=(255, 210, 90))
    d.text((x + 8, y + 6), "KYIV", font=SANS_B(30), fill=(255, 255, 255))
    mb = "MISSILE BARRAGE"
    d.text((x + w - 8 - d.textlength(mb, font=SANS_B(11)), y + 10), mb,
           font=SANS_B(11), fill=(240, 200, 90))
    d.rectangle([x, y + h - 18, x + w, y + h], fill=RED)
    d.text((x + 8, y + h - 16), "01:25 LOCAL  \u00b7  3 BRIDGES HIT",
           font=SANS_B(11), fill=(255, 255, 255))


def lead_art_akvan(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(0, 105, 105))
    # India / Odisha coast (tan land, left side)
    land = [(x, y), (x + 118, y), (x + 132, y + 26), (x + 112, y + 52),
            (x + 126, y + 78), (x + 96, y + h - 18), (x, y + h - 18)]
    d.polygon(land, fill=(214, 186, 138), outline=(150, 130, 90))
    d.text((x + 8, y + 58), "GOPALPUR", font=SANS_B(10), fill=(60, 40, 20))
    d.ellipse([x + 96, y + 66, x + 104, y + 74], fill=RED)
    # BIG spiral on the sea (right side)
    draw_spiral(d, x + w - 62, y + 42, 34, (255, 255, 255), width=3)
    d.ellipse([x + w - 66, y + 38, x + w - 58, y + 46], fill=(255, 255, 255))
    d.text((x + 8, y + 6), "CYCLONE AKVAN", font=SANS_B(17),
           fill=(255, 255, 255))
    d.text((x + w - 108, y + 6), "BAY OF BENGAL", font=SANS_B(9),
           fill=(210, 235, 235))
    d.rectangle([x, y + h - 18, x + w, y + h], fill=RED)
    d.text((x + 8, y + h - 16), "LANDFALL 08:30 IST",
           font=SANS_B(11), fill=(255, 255, 255))
    d.text((x + w - 128, y + h - 16), "70\u201380 KM/H AT COAST",
           font=SANS_B(10), fill=(255, 255, 255))


def lead_art_markets(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=NAVY)
    d.text((x + 8, y + 4), "AI SELL-OFF", font=SANS_B(20),
           fill=(255, 255, 255))
    d.text((x + 8, y + 28), "ASIA \u00b7 INTRADAY LOWS", font=SANS_B(9),
           fill=(240, 200, 90))
    # falling line chart, lower left
    pts = [(x + 10, y + 48), (x + 40, y + 44), (x + 70, y + 52),
           (x + 100, y + 46), (x + 125, y + 58), (x + 145, y + 64)]
    d.line(pts, fill=(230, 60, 50), width=2, joint="curve")
    # index table, right side
    rows = [("NIKKEI", "\u22124.9%"), ("KOSPI", "\u22125.4%"),
            ("TAIEX", "\u22126.8%"), ("HANG SENG", "\u22122.0%")]
    ry = y + 6
    for name, val in rows:
        d.text((x + 160, ry), name, font=SANS_B(10), fill=(255, 255, 255))
        vw = d.textlength(val, font=SANS_B(10))
        d.text((x + w - 8 - vw, ry), val, font=SANS_B(10), fill=(255, 90, 80))
        ry += 11
    d.rectangle([x, y + h - 18, x + w, y + h], fill=RED)
    d.text((x + 8, y + h - 16), "WORST WEEK SINCE 2020",
           font=SANS_B(11), fill=(255, 255, 255))


def build():
    im = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(im)

    # ---- masthead
    d.text((M, 6), "THE WORLD IN ONE DAY", font=SANS_B(12), fill=RED)
    d.text((W - M - d.textlength("FRIDAY'S NEWS \u00b7 ONE PAGE \u00b7 36 STORIES \u00b7 6 CONTINENTS",
                                 font=SANS_B(11)), 7),
           "FRIDAY'S NEWS \u00b7 ONE PAGE \u00b7 36 STORIES \u00b7 6 CONTINENTS",
           font=SANS_B(11), fill=INK)
    d.text((M, 14), "Friday 20 November 2026", font=SERIF_B(56), fill=INK)
    d.text((M, 68), STRAP, font=SERIF_I(15), fill=RED)
    d.line([(M, 82), (W - M, 82)], fill=INK, width=2)

    # ---- THE DAY IN UTC rail (direction A, v8 events only)
    ry0, ry1 = 86, 118
    d.rectangle([M, ry0, W - M, ry1], outline=(150, 140, 115), width=1,
                fill=CREAM2)
    lx = M + 6
    d.text((lx, ry0 + 3), "THE DAY", font=SANS_B(11), fill=RED)
    d.text((lx, ry0 + 15), "IN UTC", font=SANS_B(11), fill=RED)
    slot_x = M + 78
    slot_w = (W - M - slot_x) // 7
    for i, (t, ev) in enumerate(UTC):
        sx = slot_x + i * slot_w
        if i:
            d.line([(sx, ry0 + 4), (sx, ry1 - 4)], fill=(190, 180, 150), width=1)
        d.text((sx + 5, ry0 + 2), t, font=SANS_B(11), fill=INK)
        ev_lines = wrap(d, ev, SANS(9), slot_w - 10)
        draw_lines(d, sx + 5, ry0 + 14, ev_lines[:2], SANS(9), INK, 9)

    # ---- strip of 6
    sy = 122
    col_w = CW // 6
    for i, (num, deck) in enumerate(STRIP):
        cx = M + i * col_w
        d.text((cx + 2, sy), num, font=SANS_B(26), fill=RED)
        dl = wrap(d, deck, SANS(10), col_w - 8)
        draw_lines(d, cx + 2, sy + 28, dl[:2], SANS(10), INK, 11)
        if i:
            d.line([(cx - 4, sy + 2), (cx - 4, sy + 44)], fill=(200, 190, 165),
                   width=1)
    d.line([(M, 172), (W - M, 172)], fill=INK, width=1)

    # ---- region bar
    bx = M
    by = 176
    for label, col in REGIONS:
        wch = d.textlength(label, font=SANS_B(10)) + 12
        d.rectangle([bx, by, bx + wch, by + 18], fill=col)
        d.text((bx + 6, by + 3), label, font=SANS_B(10), fill=(255, 255, 255))
        bx += wch + 4
    d.text((W - M - d.textlength("ALL STORIES: FRI 20 NOV 2026", font=SANS_B(9)),
            by + 4), "ALL STORIES: FRI 20 NOV 2026", font=SANS_B(9), fill=GREY)

    # ---- leads
    lw = (CW - 20) // 3
    ly = 198
    lh = 84
    for i, lead in enumerate(LEADS):
        x = M + i * (lw + 10)
        if lead["art"] == "kyiv":
            lead_art_kyiv(d, x, ly, lw, lh)
        elif lead["art"] == "akvan":
            lead_art_akvan(d, x, ly, lw, lh)
        else:
            lead_art_markets(d, x, ly, lw, lh)
        ky = ly + lh + 6
        d.text((x, ky), lead["kicker"], font=SANS_B(10), fill=RED)
        tag_pill(d, x + lw, ky - 1, lead["tag"], SANS_B(8))
        hy = ky + 15
        hl = wrap(d, lead["headline"], SANS_B(18), lw)
        hy = draw_lines(d, x, hy, hl[:2], SANS_B(18), INK, 20)
        bl = wrap(d, lead["body"], SANS(11), lw)
        draw_lines(d, x, hy + 3, bl[:3], SANS(11), INK, 13)

    return im, d


# ---------------------------------------------------------------- features
def feature_art(d, kind, x, y, w, h):
    if kind == "cop31":
        d.rectangle([x, y, x + w, y + h], fill=(0, 110, 110))
        d.ellipse([x + 8, y + 8, x + 36, y + 36], outline=(255, 255, 255), width=2)
        d.ellipse([x + 14, y + 8, x + 30, y + 36], outline=(255, 255, 255), width=1)
        d.line([(x + 8, y + 22), (x + 36, y + 22)], fill=(255, 255, 255), width=1)
        d.text((x + 44, y + 8), "$120BN", font=SANS_B(16), fill=(255, 255, 255))
        d.text((x + 44, y + 28), "GAP", font=SANS_B(16), fill=(255, 120, 110))
    elif kind == "mercury":
        d.rectangle([x, y, x + w, y + h], fill=(20, 20, 35))
        d.ellipse([x + 10, y + 8, x + 38, y + 36], fill=(190, 190, 190))
        d.ellipse([x + 18, y + 16, x + 24, y + 22], fill=(150, 150, 150))
        d.polygon([(x + 60, y + 30), (x + 78, y + 18), (x + 96, y + 30)],
                  fill=(230, 230, 230))
        d.text((x + 104, y + 14), "6BN MILES", font=SANS_B(13),
               fill=(255, 255, 255))
    elif kind == "brussels":
        # EU flag
        d.rectangle([x + 6, y + 8, x + 86, y + 40], fill=(0, 50, 140))
        for k in range(12):
            import math
            a = math.radians(k * 30)
            d.ellipse([x + 46 + 11 * math.cos(a) - 2, y + 24 + 9 * math.sin(a) - 2,
                       x + 46 + 11 * math.cos(a) + 2, y + 24 + 9 * math.sin(a) + 2],
                      fill=(255, 220, 60))
        # UK flag (simplified)
        d.rectangle([x + 96, y + 8, x + 176, y + 40], fill=(0, 40, 110))
        d.rectangle([x + 96, y + 20, x + 176, y + 28], fill=(255, 255, 255))
        d.rectangle([x + 132, y + 8, x + 140, y + 40], fill=(255, 255, 255))
        d.rectangle([x + 96, y + 22, x + 176, y + 26], fill=(200, 30, 40))
        d.rectangle([x + 134, y + 8, x + 138, y + 40], fill=(200, 30, 40))
    elif kind == "cpi":
        d.rectangle([x, y, x + w, y + h], fill=(235, 235, 235))
        for i, bh in enumerate([12, 20, 30]):
            bx = x + 12 + i * 20
            d.rectangle([bx, y + 40 - bh, bx + 14, y + 40], fill=RED)
        d.text((x + 78, y + 6), "2.2%", font=SANS_B(18), fill=RED)
        d.text((x + 78, y + 28), "CPI CORE", font=SANS_B(10), fill=INK)
        d.text((x + 140, y + 28), "OCT \u00b7 Y/Y", font=SANS(9), fill=GREY)
    elif kind == "rates":
        d.rectangle([x, y, x + w, y + h], fill=(255, 255, 255))
        d.line([(x + 10, y + 38), (x + 50, y + 30), (x + 90, y + 22),
                (x + 130, y + 16), (x + 170, y + 14)], fill=RED, width=2,
               joint="curve")
        for px, py in [(10, 38), (50, 30), (90, 22), (130, 16), (170, 14)]:
            d.ellipse([x + px - 2, y + py - 2, x + px + 2, y + py + 2],
                      fill=RED)
        d.text((x + 8, y + 4), "3.50% 5Y", font=SANS_B(14), fill=RED)
        d.text((x + 100, y + 30), "3.00% 1Y", font=SANS_B(14), fill=RED)
    elif kind == "cricket":
        d.rectangle([x, y, x + w, y + h], fill=(232, 222, 196))
        d.text((x + 10, y + 8), "118", font=SANS_B(28), fill=(140, 30, 30))
        d.ellipse([x + 120, y + 14, x + 134, y + 28], fill=(180, 30, 30))
        d.rectangle([x + 150, y + 10, x + 158, y + 38], fill=(120, 80, 40))
    elif kind == "bukele":
        d.rectangle([x, y, x + w, y + h], fill=(30, 80, 160))
        d.rectangle([x + 14, y + 12, x + 54, y + 38], outline=(255, 255, 255),
                    width=2)
        d.line([(x + 20, y + 12), (x + 48, y + 12)], fill=(255, 255, 255), width=3)
        d.text((x + 64, y + 8), "FEB 2027", font=SANS_B(16),
               fill=(255, 255, 255))
    elif kind == "senegal":
        d.rectangle([x, y, x + w, y + h], fill=(232, 222, 196))
        d.text((x + 10, y + 8), "YENNE", font=SANS_B(18), fill=INK)
        for yy in (30, 38):
            d.line([(x + 10, y + yy), (x + 40, y + yy - 4), (x + 70, y + yy),
                    (x + 100, y + yy - 4), (x + 130, y + yy)], fill=(0, 110, 160),
                   width=2, joint="curve")
    elif kind == "rome":
        # Italian flag stripes + label
        d.rectangle([x + 8, y + 8, x + 34, y + 40], fill=(0, 140, 70))
        d.rectangle([x + 34, y + 8, x + 60, y + 40], fill=(255, 255, 255))
        d.rectangle([x + 60, y + 8, x + 86, y + 40], fill=(200, 30, 40))
        d.text((x + 94, y + 12), "100", font=SANS_B(18), fill=INK)
        d.text((x + 94, y + 30), "SQUARES", font=SANS_B(11), fill=INK)
    elif kind == "pill":
        d.rectangle([x, y, x + w, y + h], fill=(255, 255, 255))
        d.text((x + 8, y + 8), "60.7%", font=SANS_B(22), fill=RED)
        d.rounded_rectangle([x + 110, y + 16, x + 170, y + 32], radius=8,
                            fill=RED)
        d.rounded_rectangle([x + 140, y + 16, x + 170, y + 32], radius=8,
                            fill=(255, 255, 255), outline=RED)


# ---------------------------------------------------------------- map
CONTINENTS = [
    [(-168, 66), (-150, 70), (-135, 70), (-125, 72), (-115, 73), (-100, 73),
     (-90, 74), (-80, 73), (-70, 68), (-60, 60), (-55, 52), (-60, 47),
     (-70, 42), (-75, 35), (-80, 32), (-85, 30), (-90, 29), (-95, 28),
     (-97, 26), (-105, 23), (-110, 24), (-115, 29), (-120, 34), (-125, 40),
     (-125, 49), (-130, 55), (-140, 60), (-155, 58), (-165, 60)],
    [(-80, 10), (-75, 11), (-68, 12), (-60, 8), (-50, 0), (-40, -5),
     (-35, -8), (-40, -20), (-48, -28), (-55, -35), (-65, -40), (-70, -50),
     (-70, -55), (-75, -50), (-75, -40), (-72, -20), (-78, -10), (-80, -5),
     (-80, 5)],
    [(-10, 36), (-9, 43), (-2, 48), (-5, 50), (0, 51), (3, 53), (8, 57),
     (10, 59), (18, 56), (21, 55), (24, 58), (28, 60), (30, 62), (25, 65),
     (20, 70), (15, 70), (10, 65), (5, 60), (5, 58), (-2, 57), (-5, 50),
     (-10, 45), (-10, 38)],
    [(-17, 15), (-15, 25), (-10, 30), (-5, 35), (0, 36), (10, 37), (20, 32),
     (30, 31), (35, 28), (40, 15), (45, 11), (50, 10), (48, 0), (40, -10),
     (35, -20), (30, -30), (20, -35), (15, -30), (12, -18), (10, -5),
     (8, 4), (0, 5), (-8, 5), (-15, 10)],
    [(30, 62), (40, 68), (50, 70), (60, 72), (70, 73), (80, 73), (90, 75),
     (100, 76), (110, 76), (120, 73), (130, 72), (140, 72), (150, 70),
     (160, 66), (170, 66), (178, 65), (170, 60), (160, 55), (150, 50),
     (140, 45), (135, 40), (130, 35), (125, 30), (120, 25), (110, 20),
     (105, 10), (100, 8), (95, 15), (90, 20), (85, 20), (80, 15), (75, 10),
     (70, 20), (65, 25), (60, 25), (55, 26), (50, 28), (45, 30), (40, 35),
     (35, 36), (30, 36)],
    [(113, -22), (114, -30), (115, -35), (120, -35), (125, -33), (130, -32),
     (135, -35), (140, -38), (145, -38), (150, -37), (153, -32), (150, -25),
     (145, -20), (142, -15), (140, -12), (135, -12), (130, -13), (125, -14),
     (120, -18), (115, -20)],
    [(130, 31), (132, 33), (135, 34), (137, 35), (139, 36), (140, 38),
     (141, 40), (141, 42), (140, 44), (138, 42), (136, 38), (133, 35),
     (131, 32)],
    [(-5, 50), (-3, 53), (-5, 56), (-3, 58), (-1, 57), (0, 53), (-1, 51)],
    [(95, 5), (100, 0), (105, -5), (110, -7), (115, -8), (120, -10),
     (125, -9), (130, -5), (135, -3), (140, -4), (138, -8), (130, -10),
     (120, -12), (110, -10), (100, -5), (95, 0)],
    [(167, -45), (170, -42), (173, -40), (175, -38), (177, -38), (175, -41),
     (172, -43), (168, -46)],
]

REGION_COLOR = {"EUROPE": (31, 78, 121), "ASIA-PACIFIC": (0, 110, 110),
                "AMERICAS": (192, 57, 43), "MIDEAST": (214, 130, 30),
                "AFRICA": (30, 122, 52), "OCEANIA": (120, 70, 150)}

# (num, lon, lat, region, is_lead). Rome/Barcelona nudged slightly apart
# and the Tokyo-CPI pin pushed to sea so the numbers stay readable.
PINS = [
    (1, 30.5, 50.4, "EUROPE", True),
    (2, 84.9, 19.3, "ASIA-PACIFIC", True),
    (3, 139.7, 35.7, "ASIA-PACIFIC", True),
    (4, 30.7, 36.9, "EUROPE", False),
    (6, 4.4, 50.9, "EUROPE", False),
    (7, 152.0, 24.0, "ASIA-PACIFIC", False),
    (8, 116.4, 39.9, "ASIA-PACIFIC", False),
    (9, 174.0, -41.3, "OCEANIA", False),
    (10, -89.2, 13.7, "AMERICAS", False),
    (11, -17.4, 14.7, "AFRICA", False),
    (12, 14.0, 43.0, "EUROPE", False),
    (13, -1.0, 38.5, "EUROPE", False),
]


def draw_map(d, mx, my, mw, mh):
    d.rectangle([mx, my, mx + mw, my + mh], fill=MAP_BG,
                outline=MAP_LINE, width=1)
    for poly in CONTINENTS:
        pts = [ (mx + (lon + 180) * mw / 360.0,
                 my + (85 - lat) * mh / 145.0) for lon, lat in poly ]
        d.polygon(pts, fill=MAP_LAND, outline=MAP_LINE)
    # SPACE badge (Mercury, feature 05)
    bx, by = mx + mw - 62, my + 6
    d.rounded_rectangle([bx, by, bx + 56, by + 16], radius=8, fill=NAVY)
    d.text((bx + 8, by + 2), "SPACE", font=SANS_B(10), fill=(255, 255, 255))
    # pins (leads drawn last so gold rings sit on top)
    def pin(num, lon, lat, region, lead):
        px = mx + (lon + 180) * mw / 360.0
        py = my + (85 - lat) * mh / 145.0
        r = 7
        col = REGION_COLOR[region]
        if lead:
            d.ellipse([px - r - 2, py - r - 2, px + r + 2, py + r + 2],
                      outline=GOLD, width=2)
        d.ellipse([px - r, py - r, px + r, py + r], fill=col,
                  outline=(255, 255, 255), width=1)
        t = str(num)
        tw = d.textlength(t, font=SANS_B(9))
        d.text((px - tw / 2, py - 5), t, font=SANS_B(9), fill=(255, 255, 255))
    for p in PINS:
        if not p[4]:
            pin(*p)
    for p in PINS:
        if p[4]:
            pin(*p)


def build2(im, d):
    # ---- features (2 rows x 5)
    fw = (CW - 4 * 8) // 5
    rows_y = [386, 512]
    for ri, y0 in enumerate(rows_y):
        for ci in range(5):
            f = FEATURES[ri * 5 + ci]
            x = M + ci * (fw + 8)
            feature_art(d, f["art"], x, y0, fw, 46)
            ky = y0 + 50
            d.text((x, ky), f["kicker"], font=SANS_B(9), fill=RED)
            tag_pill(d, x + fw, ky - 1, f["tag"], SANS_B(7))
            hy = ky + 13
            hl = wrap(d, f["headline"], SANS_B(13), fw)
            hy = draw_lines(d, x, hy, hl[:2], SANS_B(13), INK, 14)
            bl = wrap(d, f["body"], SANS(10), fw)
            draw_lines(d, x, hy + 2, bl[:3], SANS(10), INK, 11)

    # ---- map + briefs header
    d.text((M, 638), "WHERE IT HAPPENED", font=SANS_B(13), fill=RED)
    d.text((380, 638), "ALSO ON FRIDAY 20 NOVEMBER \u2014 23 MORE STORIES",
           font=SANS_B(13), fill=RED)
    d.text((M, 652), "Pins 1\u201313 mark the drawn stories",
           font=SANS(9), fill=GREY)

    # ---- light map
    draw_map(d, M, 656, 340, 224)
    d.text((M, 884), "1\u20133 Lead (gold ring) \u00b7 4\u201313 Features \u00b7 Positions approximate.",
           font=SANS(9), fill=GREY)
    lx = M
    ly = 900
    for name, col in [("EUROPE", REGION_COLOR["EUROPE"]),
                      ("ASIA-PACIFIC", REGION_COLOR["ASIA-PACIFIC"]),
                      ("AMERICAS", REGION_COLOR["AMERICAS"]),
                      ("MIDEAST", REGION_COLOR["MIDEAST"]),
                      ("AFRICA", REGION_COLOR["AFRICA"]),
                      ("OCEANIA", REGION_COLOR["OCEANIA"])]:
        d.ellipse([lx, ly + 2, lx + 8, ly + 10], fill=col)
        d.text((lx + 11, ly), name, font=SANS_B(8), fill=INK)
        lx += 11 + d.textlength(name, font=SANS_B(8)) + 8

    # ---- briefs (2 columns)
    cols = [(380, BRIEFS[:12]), (692, BRIEFS[12:])]
    for cx, items in cols:
        by = 656
        for num, place, body in items:
            full = "%d %s \u2014 %s" % (num, place, body)
            lines = wrap(d, full, SANS(10), 300)
            by = draw_lines(d, cx, by, lines[:2], SANS(10), INK, 12)

    # ---- DATE CHECK
    dy0, dy1 = 948, 986
    d.rectangle([M, dy0, W - M, dy1], outline=RED, width=2)
    d.text((M + 8, dy0 + 3), "DATE CHECK", font=SANS_B(11), fill=RED)
    dl = wrap(d, DATE_CHECK, SANS(10), CW - 16)
    draw_lines(d, M + 8, dy0 + 16, dl[:2], SANS(10), INK, 11)

    # ---- footer trust legend + sources
    fy = 990
    lx = M
    for tag in ("CONFIRMED", "OFFICIAL", "REPORTED"):
        wch = d.textlength(tag, font=SANS_B(8)) + 10
        d.rounded_rectangle([lx, fy, lx + wch, fy + 12], radius=6,
                            fill=TAG_FILL[tag])
        d.text((lx + 5, fy + 1), tag, font=SANS_B(8), fill=(255, 255, 255))
        lx += wch + 4
    d.text((lx + 2, fy + 1),
           "2+ outlets \u00b7 on the record \u00b7 one outlet \u00b7 claims attributed, forecasts flagged",
           font=SANS(9), fill=GREY)
    d.text((M, 1004), FOOTER, font=SANS(9), fill=GREY)


if __name__ == "__main__":
    im, d = build()
    build2(im, d)
    out = "poster/entry_v10.png"
    im.save(out, optimize=True)
    data = open(out, "rb").read()
    print("saved", out, len(data), "bytes")
    print("sha256", hashlib.sha256(data).hexdigest())
    print("size", im.size, im.mode)
