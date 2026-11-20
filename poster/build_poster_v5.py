#!/usr/bin/env python3
"""Build the v5 poster for make.fun news-image-20261120 (MATERIAL UPGRADE
from v4, driven by the rank-1 teardown — rank1_teardown.md is the spec).

v5 leaps: (1) per-story source tags on all 36 stories, each outlet verified
as having reported that story on 20 Nov; (2) region rebalance toward
Europe 8 / Americas 8 / APAC 9-10 / Mideast 3 / Africa 3 / Oceania 4 /
World 1 (4 Europe briefs + 1 Africa brief swapped for verified 20 Nov
stories from thin regions, incl. sport / science-culture / weather);
(3) lead art 88 -> ~150 px tall and single-line briefs, map/briefs zone
shrunk to pay for it; (4) dark backgrounds on mediums 07 + 09 (and a
deeper blue on 10) so all 10 medium arts are dark like rank 1's;
(6) DATE CHECK gains Voyager 1, footer sources expand to outlets used,
map gains "Pins 1-13" subhead. Kept from v4: masthead FRIDAY'S LEDGER,
6-number strip, 13 modules, 36 stories, determinism.
Deliberately NOT copied from rank 1: IMD winds 70-80 gusting 90 (not
90-100/110), no "seven waves", no Dutch/Austrian embassy damage as a
20 Nov item, no "beats chemo alone", verified Nikkei -4.85% / Kospi
-5.16%, Senate vote 51-48. v4 file kept intact as fallback.
Pure-Python / Pillow drawing. No network, no randomness, no timestamps,
so the PNG is byte-identical on every run.
Layout (1024x1024): top line, huge date + italic strapline, 6-number
strip, region chips, 3 big leads with large hand-drawn art, 10 medium
modules each with its own small illustrated art + label chip, a dark
numbered world map beside a 23-brief ALSO-list, a DATE CHECK box and a
footer. 36 stories total, six regions + space.
Masthead is our own: FRIDAY'S LEDGER (0 occurrences in the live
leaderboard titles). All artwork is hand-drawn here with PIL shapes
(no faces, no photos). Short label chips inside art are crisp PIL text,
never generated lettering.
Run:  python3 poster/build_poster_v5.py   (writes entry.png next to main.ts)
"""
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
BG = (245, 240, 230)      # stone paper #F5F0E6
INK = (26, 23, 18)        # ink black
CRIMSON = (166, 30, 34)   # accent
TEAL = (47, 93, 90)       # slate-teal accent
TEAL_LT = (120, 158, 150)
MUTED = (90, 82, 70)
RULE = (180, 170, 150)
GOLD = (238, 217, 164)
RIVER = (143, 176, 168)
SMOKE = (185, 178, 164)
CARD_BG = (250, 246, 238)
NAVY = (28, 42, 66)       # dark map ocean (rank-1 style)
LAND = (222, 206, 170)    # map land beige
LAND_LINE = (150, 135, 105)

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FDIR = "/usr/share/fonts/truetype/liberation"


def font(name, size):
    return ImageFont.truetype(os.path.join(FDIR, name), size)


SERIF = "LiberationSerif-Regular.ttf"
SERIF_B = "LiberationSerif-Bold.ttf"
SERIF_I = "LiberationSerif-Italic.ttf"
SANS = "LiberationSans-Regular.ttf"
SANS_B = "LiberationSans-Bold.ttf"
SANS_I = "LiberationSans-Italic.ttf"

MARGIN = 36
CW = W - 2 * MARGIN  # 952


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap; returns list of lines."""
    lines, cur = [], ""
    for word in text.split(" "):
        trial = word if not cur else cur + " " + word
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def text_block(draw, x, y, lines, fnt, fill=INK, leading=None):
    if leading is None:
        leading = int(fnt.size * 1.28)
    for ln in lines:
        draw.text((x, y), ln, font=fnt, fill=fill)
        y += leading
    return y


def draw_tagged_body(draw, x, y, body, src, fnt, max_w, leading, report, key):
    """v5: render a body with an italic grey source tag appended to its
    last line when it fits there, else on a new line. Returns new y.
    The tag is one size smaller than the body, italic, muted grey —
    the visual separation of claim from source that rank 1 uses."""
    tag = f" ({src})"
    f_tag = font(SANS_I, fnt.size - 1)
    lines = wrap(draw, body, fnt, max_w)
    last_w = draw.textlength(lines[-1], font=fnt) if lines else 0
    tag_w = draw.textlength(tag, font=f_tag)
    fits = (last_w + tag_w <= max_w)
    report.append((f"{key} body lines", len(lines)))
    report.append((f"{key} tag on last line", fits))
    y2 = text_block(draw, x, y, lines, fnt, INK, leading)
    if fits:
        draw.text((x + last_w, y2 - leading), tag, font=f_tag, fill=MUTED)
    else:
        draw.text((x, y2), tag, font=f_tag, fill=MUTED)
        y2 += leading
    return y2


def kicker(draw, x, y, text, color=CRIMSON, size=13):
    f = font(SANS_B, size)
    draw.text((x, y), text, font=f, fill=color)
    return y + size + 5


def rule(draw, x, y, w, color=INK, thick=2):
    draw.rectangle([x, y, x + w, y + thick - 1], fill=color)


def chip(draw, x, y, text, fill=CRIMSON, fg=(255, 255, 255), size=10):
    """Small label chip inside artwork (crisp PIL text, rank-1 style)."""
    f = font(SANS_B, size)
    tw = draw.textlength(text, font=f)
    pad = 5
    draw.rectangle([x, y, x + tw + 2 * pad, y + size + 6], fill=fill)
    draw.text((x + pad, y + 3), text, font=f, fill=fg)
    return tw + 2 * pad


def paste_art(img, fn, x, y, w, h):
    """Draw one illustration onto a temp image and paste it, so no art
    element can bleed outside its own box onto neighbouring text."""
    tmp = Image.new("RGB", (w, h), BG)
    td = ImageDraw.Draw(tmp)
    fn(td, 0, 0, w, h)
    img.paste(tmp, (x, y))


# ----------------------------------------------------------------------
# Lead illustrations (304 px wide, 100 tall)
# ----------------------------------------------------------------------
def art_akvan(draw, x, y, w, h):
    """Cyclone over the Bay of Bengal: dark teal sea, spiral rain bands,
    gold coast at the bottom, red landfall dot. Bottom band carries the
    landfall facts (IMD figures). No faces, no text except the band."""
    draw.rectangle([x, y, x + w, y + h], fill=(58, 96, 110))
    cx, cy = x + int(w * 0.62), y + int(h * 0.40)
    for r, a0, a1 in [(52, 200, 20), (42, 20, 200), (32, 200, 20),
                      (23, 20, 200), (14, 200, 20)]:
        draw.arc([cx - r, cy - r, cx + r, cy + r], a0, a1,
                 fill=(235, 240, 238), width=4)
    draw.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=(235, 240, 238))
    draw.arc([x - 10, y + 2, x + 120, y + 90], 300, 60, fill=(150, 190, 195), width=3)
    draw.arc([x + 150, y + 2, x + 320, y + 80], 120, 250, fill=(150, 190, 195), width=3)
    draw.polygon([(x, y + h), (x, y + int(h * 0.66)), (x + int(w * 0.42), y + int(h * 0.74)),
                  (x + int(w * 0.55), y + h)], fill=GOLD)
    draw.line([(x, y + int(h * 0.66)), (x + int(w * 0.42), y + int(h * 0.74)),
               (x + int(w * 0.55), y + h)], fill=INK, width=2)
    lx, ly = x + int(w * 0.44), y + int(h * 0.76)
    draw.ellipse([lx - 6, ly - 6, lx + 6, ly + 6], fill=CRIMSON, outline=(255, 255, 255), width=1)
    # in-art place labels (v5: taller art carries the geography)
    f_lab = font(SANS_B, 10)
    draw.text((lx + 9, ly - 5), "Gopalpur", font=f_lab, fill=(255, 255, 255))
    draw.text((x + 8, y + int(h * 0.52)), "BAY OF", font=f_lab, fill=(200, 225, 228))
    draw.text((x + 8, y + int(h * 0.52) + 12), "BENGAL", font=f_lab, fill=(200, 225, 228))
    # bottom facts band (dark teal, white text)
    by = y + h - 16
    draw.rectangle([x, by, x + w, y + h], fill=(30, 55, 66))
    f = font(SANS_B, 10)
    draw.text((x + 6, by + 3), "LANDFALL · GUSTS 90 KM/H", font=f, fill=(255, 255, 255))
    t = "CYCLONE AKVAN"
    draw.text((x + w - draw.textlength(t, font=f) - 6, by + 3), t, font=f,
              fill=(255, 220, 120))
    draw.rectangle([x, y, x + w, y + h], outline=INK, width=1)


def art_kyiv(draw, x, y, w, h):
    """Dnipro at dawn: gold sky, far-bank silhouettes, teal river,
    three arched bridges, smoke over two of them. Bottom band carries
    the time and the missile count. No faces."""
    draw.rectangle([x, y, x + w, y + h], fill=GOLD)
    draw.rectangle([x, y + int(h * 0.34), x + w, y + int(h * 0.52)], fill=(242, 227, 192))
    sx, sy, sr = x + int(w * 0.62), y + int(h * 0.38), 12
    draw.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(201, 106, 90))
    base = y + int(h * 0.52)
    bx = x + 6
    for bw, bh in [(26, 22), (18, 34), (30, 18), (16, 28), (34, 24), (20, 38),
                   (28, 16), (18, 30), (30, 22), (16, 26)]:
        draw.rectangle([bx, base - bh, bx + bw, base], fill=INK)
        bx += bw + 7
        if bx > x + w - 20:
            break
    draw.rectangle([x, base, x + w, y + h], fill=RIVER)
    draw.line([x + 10, y + h - 26, x + w - 60, y + h - 26], fill=(210, 228, 222), width=2)
    draw.line([x + 60, y + h - 21, x + w - 10, y + h - 21], fill=(210, 228, 222), width=2)
    for cx in (int(w * 0.20), int(w * 0.50), int(w * 0.80)):
        bw = 76
        bx0, bx1 = x + cx - bw // 2, x + cx + bw // 2
        deck = base + 11
        draw.line([bx0, deck, bx1, deck], fill=INK, width=3)
        draw.arc([bx0, deck, bx1, deck + 22], 0, 180, fill=INK, width=3)
        for px in (bx0 + 12, cx + x, bx1 - 12):
            draw.line([px, deck, px, y + h - 17], fill=INK, width=2)
    for cx in (int(w * 0.50), int(w * 0.80)):
        px, py = x + cx, y + int(h * 0.34)
        draw.ellipse([px - 20, py - 8, px + 2, py + 8], fill=SMOKE)
        draw.ellipse([px - 6, py - 16, px + 16, py + 2], fill=SMOKE)
        draw.ellipse([px - 2, py - 22, px + 12, py - 8], fill=(205, 199, 186))
    for bx, by in [(int(w * 0.14), int(h * 0.12)), (int(w * 0.24), int(h * 0.08))]:
        draw.line([x + bx - 6, y + by, x + bx, y + by - 5, x + bx + 6, y + by],
                  fill=INK, width=2)
    # v5: missile trails in the dawn sky (no count claimed — trails only)
    for (sx0, sy0, sx1, sy1) in [(0.10, 0.06, 0.20, 0.16), (0.42, 0.04, 0.52, 0.15),
                                 (0.68, 0.07, 0.78, 0.18)]:
        draw.line([x + int(w * sx0), y + int(h * sy0), x + int(w * sx1), y + int(h * sy1)],
                  fill=(200, 60, 40), width=3)
        draw.ellipse([x + int(w * sx1) - 3, y + int(h * sy1) - 3,
                      x + int(w * sx1) + 3, y + int(h * sy1) + 3], fill=(255, 220, 120))
    by = y + h - 16
    draw.rectangle([x, by, x + w, y + h], fill=(30, 30, 30))
    f = font(SANS_B, 10)
    draw.text((x + 6, by + 3), "01:25 LOCAL", font=f, fill=(255, 255, 255))
    t = "~30 MISSILES"
    draw.text((x + w - draw.textlength(t, font=f) - 6, by + 3), t, font=f,
              fill=(255, 220, 120))
    draw.rectangle([x, y, x + w, y + h], outline=INK, width=1)


def art_cop(draw, x, y, w, h):
    """COP31, rank-1 style: globe, thermometer, red COP31 box.
    No faces, no text except the red box label."""
    draw.rectangle([x, y, x + w, y + h], fill=(232, 226, 208))
    # globe
    gx, gy, gr = x + 48, y + h // 2 - 4, 28
    draw.ellipse([gx - gr, gy - gr, gx + gr, gy + gr], fill=(96, 150, 160), outline=INK, width=2)
    draw.ellipse([gx - 15, gy - 20, gx + 2, gy - 6], fill=(120, 168, 120))
    draw.ellipse([gx - 4, gy + 2, gx + 17, gy + 19], fill=(120, 168, 120))
    draw.ellipse([gx - 24, gy + 5, gx - 11, gy + 17], fill=(120, 168, 120))
    draw.arc([gx - gr, gy - gr, gx + gr, gy + gr], 300, 60, fill=(235, 240, 238), width=2)
    # thermometer
    tx, ty = x + 128, y + 12
    draw.rounded_rectangle([tx, ty, tx + 16, ty + 58], radius=8, fill=(250, 246, 238),
                           outline=INK, width=2)
    draw.rectangle([tx + 4, ty + 22, tx + 12, ty + 54], fill=CRIMSON)
    draw.ellipse([tx - 3, ty + 54, tx + 19, ty + 76], fill=CRIMSON, outline=INK, width=2)
    # red COP31 box
    bx0, by0, bx1, by1 = x + 168, y + 8, x + w - 6, y + h - 8
    draw.rectangle([bx0, by0, bx1, by1], fill=CRIMSON, outline=INK, width=1)
    draw.text((bx0 + 10, by0 + 8), "COP31", font=font(SERIF_B, 26), fill=(255, 255, 255))
    draw.text((bx0 + 10, by0 + 40), "FINAL DAY", font=font(SANS_B, 13), fill=(255, 255, 255))
    draw.text((bx0 + 10, by0 + 58), "DEADLOCK", font=font(SANS_B, 13), fill=(255, 220, 120))
    # v5: finance-gap line, visible now the art is taller
    draw.text((bx0 + 10, by0 + 80), "$120BN FINANCE GAP", font=font(SANS_B, 11),
              fill=(255, 220, 120))
    draw.rectangle([x, y, x + w, y + h], outline=INK, width=1)


# ----------------------------------------------------------------------
# Medium illustrations (182 px wide, 56 tall each), rank-1 style with
# a short label chip. All hand-drawn PIL shapes; chips are crisp text.
# ----------------------------------------------------------------------
def art_m_markets(draw, x, y, w, h):
    """v4: clearer falling chart — ink axes, four descending crimson
    bars, a crimson trend line falling across them with an arrowhead."""
    draw.rectangle([x, y, x + w, y + h], fill=(250, 246, 238))
    base = y + h - 8
    # axes: vertical at x+14, horizontal along the base
    draw.line([x + 14, y + 22, x + 14, base], fill=INK, width=2)
    draw.line([x + 14, base, x + w - 8, base], fill=INK, width=2)
    for i, bh in enumerate([18, 14, 10, 6]):
        bx = x + 26 + i * 36
        draw.rectangle([bx, base - bh, bx + 20, base], fill=CRIMSON)
    # descending trend line over the bars, arrowhead at the lower end
    draw.line([x + 30, y + 24, x + 158, y + 34], fill=CRIMSON, width=3)
    draw.polygon([(x + 162, y + 35), (x + 148, y + 30), (x + 152, y + 40)],
                 fill=CRIMSON)
    chip(draw, x + 6, y + 4, "ASIA −7% WK", CRIMSON)
    draw.rectangle([x, y, x + w, y + h], outline=INK, width=1)


def art_m_bepi(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(24, 34, 54))
    # stars
    for sx, sy in [(20, 10), (52, 22), (90, 8), (150, 14), (170, 30), (40, 40)]:
        draw.ellipse([x + sx - 1, y + sy - 1, x + sx + 1, y + sy + 1], fill=(255, 255, 255))
    # Mercury: grey cratered disc (v5: shrunk to fit the 44 px box — the
    # old r=20 disc was clipped flat at the bottom edge)
    mx, my, mr = x + 132, y + 26, 16
    draw.ellipse([mx - mr, my - mr, mx + mr, my + mr], fill=(180, 175, 165),
                 outline=(235, 240, 238), width=1)
    for cx, cy, cr in [(124, 20, 3), (138, 28, 2), (128, 32, 2)]:
        draw.ellipse([cx - cr, cy - cr, cx + cr, cy + cr], fill=(140, 135, 125))
    # probe + dotted trajectory
    draw.line([x + 14, y + h - 10, x + 100, y + 22], fill=(238, 217, 164), width=1)
    for t in range(0, 11):
        px = x + 14 + int(86 * t / 10)
        py = y + h - 10 - int(32 * t / 10)
        draw.ellipse([px - 1, py - 1, px + 1, py + 1], fill=(238, 217, 164))
    draw.rectangle([x + 8, y + h - 16, x + 24, y + h - 6], fill=GOLD, outline=INK, width=1)
    draw.line([x + 16, y + h - 6, x + 16, y + h - 2], fill=GOLD, width=2)
    chip(draw, x + 6, y + 4, "6BN MILES", (40, 60, 110))
    draw.rectangle([x, y, x + w, y + h], outline=INK, width=1)


def art_m_burnham(draw, x, y, w, h):
    # left: EU blue + ring of gold stars; right: UK flag (simplified)
    draw.rectangle([x, y, x + w // 2, y + h], fill=(0, 51, 153))
    cx, cy = x + w // 4, y + h // 2
    for k in range(12):
        import math
        a = math.pi * 2 * k / 12 - math.pi / 2
        sx, sy = cx + int(20 * math.cos(a)), cy + int(20 * math.sin(a))
        draw.ellipse([sx - 2, sy - 2, sx + 2, sy + 2], fill=(255, 204, 0))
    draw.rectangle([x + w // 2, y, x + w, y + h], fill=(1, 33, 105))
    draw.line([x + w // 2, y, x + w, y + h], fill=(255, 255, 255), width=8)
    draw.line([x + w, y, x + w // 2, y + h], fill=(255, 255, 255), width=8)
    draw.line([x + w // 2, y, x + w, y + h], fill=(200, 16, 46), width=3)
    draw.line([x + w, y, x + w // 2, y + h], fill=(200, 16, 46), width=3)
    draw.rectangle([x + w // 2 - 14, y, x + w // 2 + 14, y + h], fill=(255, 255, 255))
    draw.rectangle([x + w // 2 - 5, y, x + w // 2 + 5, y + h], fill=(200, 16, 46))
    draw.rectangle([x, y + h // 2 - 14, x + w, y + h // 2 + 14], fill=(255, 255, 255))
    draw.rectangle([x, y + h // 2 - 5, x + w, y + h // 2 + 5], fill=(200, 16, 46))
    chip(draw, x + 6, y + 4, "RESET TALKS", TEAL)
    draw.rectangle([x, y, x + w, y + h], outline=INK, width=1)


def art_m_cpi(draw, x, y, w, h):
    """v5: dark navy background like rank 1's — pale bars, red 2% target
    dashed line, red rising arrow."""
    draw.rectangle([x, y, x + w, y + h], fill=NAVY)
    base = y + h - 8
    for i, bh in enumerate([16, 22, 30]):
        bx = x + 26 + i * 34
        draw.rectangle([bx, base - bh, bx + 20, base], fill=TEAL_LT)
    draw.line([x + 10, y + 12, x + w - 10, y + 12], fill=CRIMSON, width=2)
    draw.line([x + 10, y + 12, x + 10, y + 18], fill=CRIMSON, width=2)
    draw.line([x + w - 10, y + 12, x + w - 10, y + 18], fill=CRIMSON, width=2)
    # rising arrow
    draw.line([x + 128, y + h - 12, x + 168, y + 14], fill=CRIMSON, width=3)
    draw.polygon([(x + 168, y + 14), (x + 156, y + 16), (x + 166, y + 28)], fill=CRIMSON)
    chip(draw, x + 6, y + 4, "2% TARGET", CRIMSON)
    draw.rectangle([x, y, x + w, y + h], outline=INK, width=1)


def art_m_rates(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(250, 246, 238))
    f = font(SANS_B, 11)
    # rows positioned to fit the 44 px box (v5 defect: the old fixed
    # y+38 1Y row fell off the bottom edge and "3.00%" was clipped)
    draw.text((x + 6, y + 20), "5Y", font=f, fill=INK)
    draw.rectangle([x + 28, y + 20, x + 132, y + 31], fill=TEAL)
    draw.text((x + 136, y + 20), "3.50%", font=f, fill=INK)
    draw.text((x + 6, y + 32), "1Y", font=f, fill=INK)
    draw.rectangle([x + 28, y + 32, x + 112, y + 43], fill=GOLD, outline=INK, width=1)
    draw.text((x + 116, y + 32), "3.00%", font=f, fill=INK)
    chip(draw, x + 6, y + 3, "18 MO UNCHANGED", TEAL)
    draw.rectangle([x, y, x + w, y + h], outline=INK, width=1)


def art_m_phillips(draw, x, y, w, h):
    """v5: dark green background like rank 1's — dark pitch, gold stumps,
    tan bat, red ball."""
    draw.rectangle([x, y, x + w, y + h], fill=(34, 66, 48))
    draw.rectangle([x, y + h - 12, x + w, y + h], fill=(24, 50, 36))
    sx = x + 28
    for dx in (0, 6, 12):
        draw.line([sx + dx, y + h - 34, sx + dx, y + h - 12], fill=GOLD, width=3)
    draw.line([sx, y + h - 36, sx + 12, y + h - 36], fill=GOLD, width=2)
    draw.polygon([(x + 78, y + 12), (x + 92, y + 16), (x + 108, y + 46),
                  (x + 96, y + 50)], fill=(190, 150, 90), outline=INK)
    draw.line([x + 84, y + 14, x + 74, y + 4], fill=INK, width=3)
    draw.ellipse([x + 138, y + 14, x + 156, y + 32], fill=CRIMSON, outline=INK, width=1)
    draw.arc([x + 138, y + 14, x + 156, y + 32], 200, 340, fill=(255, 255, 255), width=1)
    chip(draw, x + 6, y + 4, "118 · RECORD", CRIMSON)
    draw.rectangle([x, y, x + w, y + h], outline=INK, width=1)


def art_m_bukele(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(226, 233, 238))
    # El Salvador flag bands (blue-white-blue) as backdrop strip
    draw.rectangle([x, y + h - 18, x + w, y + h - 12], fill=(0, 74, 173))
    draw.rectangle([x, y + h - 12, x + w, y + h - 6], fill=(255, 255, 255))
    draw.rectangle([x, y + h - 6, x + w, y + h], fill=(0, 74, 173))
    # ballot box + slot — v5: deepened navy blue (dark-card consistency),
    # box sized relative to art height (the old fixed bottom y+h-20 left
    # an 8 px sliver in the 44 px box)
    draw.rectangle([x + 56, y + 14, x + 118, y + h - 14], fill=(24, 52, 96), outline=INK, width=1)
    draw.rectangle([x + 72, y + 16, x + 102, y + 20], fill=INK)
    draw.rectangle([x + 76, y + 4, x + 98, y + 16], fill=(250, 246, 238), outline=INK, width=1)
    draw.line([x + 126, y + 24, x + 138, y + 36, x + 162, y + 12], fill=CRIMSON, width=4)
    chip(draw, x + 6, y + 4, "2027 · THIRD TERM", (24, 52, 96))
    draw.rectangle([x, y, x + w, y + h], outline=INK, width=1)


def art_m_senegal(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(226, 233, 238))
    # sea waves
    for wy in (y + h - 16, y + h - 8):
        for wx in range(x + 4, x + w - 4, 18):
            draw.arc([wx, wy - 5, wx + 18, wy + 5], 180, 360, fill=TEAL, width=2)
    # small boat with outboard
    bx, by = x + 66, y + 22
    draw.polygon([(bx, by), (bx + 52, by), (bx + 44, by + 10), (bx + 8, by + 10)], fill=(146, 96, 58),
                 outline=INK)
    draw.line([bx + 26, by, bx + 26, by - 12], fill=INK, width=2)
    draw.polygon([(bx + 26, by - 12), (bx + 26, by - 2), (bx + 40, by - 2)], fill=CRIMSON)
    # sun
    draw.ellipse([x + 148, y + 6, x + 166, y + 24], fill=(238, 180, 90), outline=INK, width=1)
    chip(draw, x + 6, y + 4, "YENNE COAST", TEAL)
    draw.rectangle([x, y, x + w, y + h], outline=INK, width=1)


def art_m_italy(draw, x, y, w, h):
    """v4: clearer protest scene — five simple figures (head + shoulders,
    no faces) standing behind a banner. v5 fix: the banner carries NO text
    (the chip above already reads SCIOPERO · 100 SQUARES) — the 10 px
    banner text was clipped at the 44 px art box bottom edge."""
    draw.rectangle([x, y, x + w, y + h], fill=(250, 246, 238))
    cols = [TEAL, CRIMSON, (140, 120, 60), (40, 50, 90), (0, 120, 60)]
    for cx, col in zip((28, 58, 88, 118, 148), cols):
        # shoulders (partly hidden behind the banner below)
        draw.rectangle([x + cx - 8, y + 30, x + cx + 8, y + 42], fill=col)
        # head
        draw.ellipse([x + cx - 5, y + 21, x + cx + 5, y + 31], fill=col,
                     outline=INK, width=1)
    # banner held in front of the crowd (blank: label lives in the chip)
    draw.rectangle([x + 10, y + 32, x + w - 10, y + 43], fill=(250, 246, 238),
                   outline=CRIMSON, width=2)
    chip(draw, x + 6, y + 4, "SCIOPERO · 100 SQUARES", (0, 120, 60))
    draw.rectangle([x, y, x + w, y + h], outline=INK, width=1)


def art_m_darax(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(214, 228, 222))
    # capsule, diagonal: crimson half + white half
    cx, cy = x + 92, y + h // 2 + 4
    draw.rounded_rectangle([cx - 52, cy - 12, cx + 52, cy + 12], radius=12,
                           fill=(250, 246, 238), outline=INK, width=2)
    draw.rounded_rectangle([cx - 52, cy - 12, cx, cy + 12], radius=12, fill=CRIMSON,
                           outline=INK, width=1)
    draw.rectangle([cx - 52, cy - 12, cx, cy + 12], fill=CRIMSON)
    draw.ellipse([cx - 52, cy - 12, cx - 28, cy + 12], fill=CRIMSON)
    # small pills
    for px, py in [(30, 38), (150, 16)]:
        draw.ellipse([x + px - 5, y + py - 5, x + px + 5, y + py + 5], fill=GOLD,
                     outline=INK, width=1)
    chip(draw, x + 6, y + 4, "60.7% RESPONSE", CRIMSON)
    draw.rectangle([x, y, x + w, y + h], outline=INK, width=1)


# ----------------------------------------------------------------------
# World map (dark navy, rank-1 style; simplified recognisable continents)
# ----------------------------------------------------------------------
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

# pin number -> (lon, lat, dx, dy) for the numbered circle offset
# v4: crowded clusters are fanned outward with leader lines to a white
# dot at the true spot. Europe: 6 up-left, 2 up-right, 13 left, 12 down,
# 3 down-right — every circle >=28 px from its neighbours (r=7).
# East Asia (v3 defect: 8/4/7 sat on their true spots ~11 px apart and
# overlapped): 8 up-left, 4 straight up, 7 up-right.
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

LAT_TOP, LAT_BOT = 70.0, -55.0


def draw_map(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=NAVY, outline=INK, width=1)

    def proj(lon, lat):
        px = x + (lon + 180.0) / 360.0 * w
        py = y + (LAT_TOP - lat) / (LAT_TOP - LAT_BOT) * h
        # Clamp to the map box: continent data reaches lat 80 but LAT_TOP
        # is 70, so unclamped land spilled above the map and over the
        # "WHERE IT HAPPENED" title. Clipping here keeps the map inside
        # its own rectangle.
        px = max(x, min(x + w, px))
        py = max(y, min(y + h, py))
        return (px, py)

    for poly in CONTINENTS:
        draw.polygon([proj(lon, lat) for lon, lat in poly], fill=LAND,
                     outline=LAND_LINE)
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
        t = str(num)
        tw = draw.textlength(t, font=f_pin)
        draw.text((cx - tw / 2, cy - 5), t, font=f_pin, fill=(255, 255, 255))
    # SPACE inset, bottom-left (pin 5: BepiColombo / Mercury)
    ix, iy, iw, ih = x + 8, y + h - 26, 108, 20
    draw.rectangle([ix, iy, ix + iw, iy + ih], fill=(24, 34, 54), outline=(255, 255, 255), width=1)
    r = 7
    draw.ellipse([ix + 10 - r, iy + 10 - r, ix + 10 + r, iy + 10 + r], fill=CRIMSON,
                 outline=(255, 255, 255), width=1)
    draw.text((ix + 10 - 2, iy + 5), "5", font=f_pin, fill=(255, 255, 255))
    draw.text((ix + 22, iy + 5), "SPACE · MERCURY", font=font(SANS_B, 8),
              fill=(255, 255, 255))
    # v5: bottom legend, inside the map at the bottom-right (ocean strip)
    f_leg = font(SANS_B, 8)
    t_leg = "● 1–3 LEAD  ● 4–13 FEATURE"
    draw.text((x + w - 6 - draw.textlength(t_leg, font=f_leg), y + h - 10),
              t_leg, font=f_leg, fill=(255, 255, 255))


# ----------------------------------------------------------------------
# Page assembly
# ----------------------------------------------------------------------
def main():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    report = []

    # ---- Top line + huge date + strapline (rank-1 treatment) -----------
    y = 8
    f_top = font(SANS_B, 12)
    d.text((MARGIN, y), "FRIDAY'S LEDGER", font=f_top, fill=CRIMSON)
    t = "FRIDAY'S NEWS · ONE PAGE · 36 STORIES · 6 CONTINENTS"
    d.text((W - MARGIN - d.textlength(t, font=f_top), y), t, font=f_top, fill=INK)
    y += 16
    f_date = font(SERIF_B, 54)
    t = "Friday 20 November 2026"
    d.text(((W - d.textlength(t, font=f_date)) / 2, y), t, font=f_date, fill=INK)
    y += 60
    f_strap = font(SERIF_I, 15)
    t = ("Cyclone Akvan strikes India · Ballistic missiles hit Kyiv · "
         "COP31 deadlocked on final day · Asian AI sell-off")
    d.text(((W - d.textlength(t, font=f_strap)) / 2, y), t, font=f_strap, fill=CRIMSON)
    y += 18
    rule(d, MARGIN, y, CW, INK, 3)
    rule(d, MARGIN, y + 5, CW, INK, 1)
    y += 9
    report.append(("masthead/date ends", y))

    # ---- Numbers strip: 6 boxes (rank-1 numbers, all verified) ----------
    strip = [
        ("300,000+", "EVACUATED AHEAD OF CYCLONE AKVAN", CRIMSON),
        ("~30", "BALLISTIC MISSILES FIRED AT KYIV", CRIMSON),
        ("−7%", "ASIA SHARES' WORST WEEK SINCE 2020", CRIMSON),
        ("2.2%", "JAPAN OCT CORE CPI, BOJ EYED", INK),
        ("118", "PHILLIPS' HISTORIC CENTURY VS INDIA", INK),
        ("8 yrs", "BEPICOLOMBO REACHES MERCURY", INK),
    ]
    box_w = (CW - 5 * 8) // 6  # 152
    box_h = 56
    f_num = font(SERIF_B, 26)
    f_lab = font(SANS_B, 10)
    for i, (num, lab, col) in enumerate(strip):
        bx = MARGIN + i * (box_w + 8)
        d.rectangle([bx, y, bx + box_w, y + box_h], fill=CARD_BG, outline=RULE, width=1)
        d.rectangle([bx, y, bx + box_w, y + 3], fill=CRIMSON if i % 2 == 0 else TEAL)
        nw = d.textlength(num, font=f_num)
        d.text((bx + (box_w - nw) / 2, y + 5), num, font=f_num, fill=col)
        ll = wrap(d, lab, f_lab, box_w - 12)
        ly = y + 33
        for ln in ll[:2]:
            lw = d.textlength(ln, font=f_lab)
            d.text((bx + (box_w - lw) / 2, ly), ln, font=f_lab, fill=MUTED)
            ly += 12
        report.append((f"strip {i+1} label lines", len(ll)))
    y += box_h + 5
    report.append(("strip ends", y))

    # ---- Region bar: coloured chips + right text ------------------------
    regions = [  # (label, count, chip colour) — counts computed from the story list
        ("EUROPE", 8, TEAL),
        ("AMERICAS", 8, CRIMSON),
        ("ASIA-PACIFIC", 9, (150, 40, 40)),
        ("MIDEAST", 3, (140, 120, 60)),
        ("AFRICA", 3, (60, 110, 110)),
        ("OCEANIA", 4, (90, 70, 140)),
        ("WORLD", 1, (40, 50, 90)),
    ]
    f_chip = font(SANS_B, 11)
    cx = MARGIN
    for lab, cnt, col in regions:
        t = f"{lab} {cnt}"
        tw = d.textlength(t, font=f_chip)
        d.rectangle([cx, y, cx + tw + 12, y + 20], fill=col)
        d.text((cx + 6, y + 4), t, font=f_chip, fill=(255, 255, 255))
        cx += tw + 12 + 6
    t = "ALL STORIES: FRI 20 NOV 2026, ANY TIME ZONE"
    d.text((W - MARGIN - d.textlength(t, font=f_chip), y + 4), t, font=f_chip, fill=INK)
    y += 20 + 4
    report.append(("region bar ends", y))

    # ---- Leads: 3 big modules -------------------------------------------
    leads = [
        ("01", "ODISHA, INDIA — CYCLONE", "Cyclone Akvan makes landfall in eastern India",
         "Crosses near Gopalpur; 300,000+ evacuated, winds 70–80 kph gusting to 90.",
         "IMD", art_akvan),
        ("02", "KYIV, UKRAINE — WAR", "Russia fires wave of ~30 ballistic missiles at Kyiv",
         "Overnight attack hits energy and transport sites; three Dnipro bridges hit.",
         "Reuters", art_kyiv),
        ("03", "ANTALYA, TÜRKIYE — CLIMATE", "COP31 reaches its final day deadlocked",
         "Draft omits fossil fuels; $120bn finance unresolved; “35 by 35” pushed.",
         "AP", art_cop),
    ]
    lead_w = (CW - 2 * 20) // 3  # 304
    lead_art_h = 150  # v5: rank-1 leads are ~165 px; ours were ~90 px
    leads_bottom = y
    for i, (num, kick, head, body, src, art) in enumerate(leads):
        x = MARGIN + i * (lead_w + 20)
        cy = y
        paste_art(img, art, x, cy, lead_w, lead_art_h)
        cy += lead_art_h + 4
        cy = kicker(d, x, cy, f"{num} · {kick}", CRIMSON, 12)
        f_lh = font(SERIF_B, 23)
        hl = wrap(d, head, f_lh, lead_w)
        report.append((f"lead {num} headline lines", len(hl)))
        cy = text_block(d, x, cy, hl, f_lh, INK, 25)
        f_lb = font(SERIF, 14)
        cy = draw_tagged_body(d, x, cy, body, src, f_lb, lead_w, 15, report,
                               f"lead {num}")
        leads_bottom = max(leads_bottom, cy)
    y = leads_bottom + 3
    rule(d, MARGIN, y, CW, RULE, 1)
    y += 5
    report.append(("leads end", y))

    # ---- Medium modules: 5 cols x 2 rows --------------------------------
    mediums = [
        ("04", "SEOUL/TOKYO — MARKETS", "AI sell-off sinks Asia to worst week",
         "Worst week since 2020: Nikkei −4.85%; Kospi −5.16%.", "Reuters", art_m_markets),
        ("05", "MERCURY — SPACE", "BepiColombo reaches Mercury",
         "6bn-mile trip ends; orbit insertion set for Saturday.", "ESA", art_m_bepi),
        ("06", "BRUSSELS — EUROPE", "Burnham holds first EU–UK reset summit",
         "Food checks end; ETS linked; 100,000 youth visas.", "The Times", art_m_burnham),
        ("07", "TOKYO — ECONOMY", "Japan inflation hits 2.2%; BoJ hike eyed",
         "Oct core CPI up 2.2%, below 2.3% forecast.", "Reuters", art_m_cpi),
        ("08", "BEIJING — RATES", "China holds lending rates 18th month",
         "1-year LPR 3.00%, 5-year 3.50% as expected.", "Reuters", art_m_rates),
        ("09", "WELLINGTON — CRICKET", "Phillips makes history with 118",
         "118 off 216 balls; NZ post 368 in first Test.", "ICC", art_m_phillips),
        ("10", "SAN SALVADOR — POLITICS", "Bukele registers for third-term bid",
         "Files for Feb 2027 vote; rights groups object.", "Reuters", art_m_bukele),
        ("11", "SENEGAL — MIGRATION", "Migrant boat capsizes off Yenne; 4 dead",
         "4 dead; dozens missing from ~50–100 aboard.", "Al Jazeera", art_m_senegal),
        ("12", "ROME — LABOUR", "Italy's CGIL holds 24-hr general strike",
         "Unions rally in ~100 squares; transit hit.", "Reuters", art_m_italy),
        ("13", "BARCELONA — HEALTH", "Cancer pill shrinks tumours 60.7%",
         "Tumours shrank in 60.7% of 61 patients; early trial.", "BBC", art_m_darax),
    ]
    med_w = (CW - 4 * 10) // 5  # 182
    med_art_h = 44  # v5: tightened 48 -> 44 to pay for taller lead art
    f_mh = font(SERIF_B, 18)
    f_mb = font(SERIF, 13)
    for row in range(2):
        row_bottom = y
        for col in range(5):
            num, kick, head, body, src, art = mediums[row * 5 + col]
            x = MARGIN + col * (med_w + 10)
            cy = y
            paste_art(img, art, x, cy, med_w, med_art_h)
            cy += med_art_h + 4
            cy = kicker(d, x, cy, f"{num} · {kick}", CRIMSON, 11)
            hl = wrap(d, head, f_mh, med_w)
            report.append((f"med {num} headline lines", len(hl)))
            cy = text_block(d, x, cy, hl, f_mh, INK, 19)
            cy = draw_tagged_body(d, x, cy, body, src, f_mb, med_w, 13, report,
                                  f"med {num}")
            row_bottom = max(row_bottom, cy)
        y = row_bottom + 4
    report.append(("mediums end", y))

    # ---- Map + ALSO-list, side by side (rank-1 style) --------------------
    rule(d, MARGIN, y, CW, RULE, 1)
    y += 5
    f_sech = font(SANS_B, 12)
    d.text((MARGIN, y), "WHERE IT HAPPENED", font=f_sech, fill=INK)
    t = "ALSO ON FRIDAY 20 NOVEMBER — 23 MORE STORIES"
    map_w = 300  # v5: narrowed 340 -> 300 to widen the brief columns
    briefs_x = MARGIN + map_w + 16
    d.text((briefs_x, y), t, font=f_sech, fill=INK)
    # v5: map subhead (rank-1 style) in the gap between the two headers
    t_sub = "Pins 1–13 (Lead & Feature)"
    f_sub = font(SANS, 10)
    d.text((briefs_x - 6 - d.textlength(t_sub, font=f_sub), y + 2), t_sub,
           font=f_sub, fill=MUTED)
    t2 = "World Briefs (14–36)"
    d.text((W - MARGIN - d.textlength(t2, font=font(SANS, 11)), y + 1), t2,
           font=font(SANS, 11), fill=MUTED)
    y += 16
    sec_top = y

    # v5: 5 briefs swapped for the region rebalance (Europe 12 -> 8,
    # Mideast 1 -> 3, Oceania 3 -> 4, APAC 8 -> 9, Africa 4 -> 3).
    # Dropped: 21 EU methane delay, 26 EU summons envoy, 31 STOXX 600,
    # 22 Genoa drones, 17 Zimbabwe landmines. Added: 20-21 Mideast,
    # 34 Vegas FP2 (sport), 35 Modi SCO forum (culture), 36 NSW rain
    # (weather) — all verified 20 Nov with their reporting outlet.
    briefs = [
        ("14", "US", "US sanctions Comancheros, 'Ndrangheta", "Reuters"),
        ("15", "EU", "Commission cyberattack, AI-assisted", "Politico"),
        ("16", "EGYPT", "Egypt repays $38.2bn debt", "Egypt Independent"),
        ("17", "SPORT", "Las Vegas GP practice washed out", "Reuters"),
        ("18", "TECH", "Samsung names Choi to head mobile", "Reuters"),
        ("19", "TECH", "Google adds Mac control to Gemini", "Google"),
        ("20", "MIDEAST", "Hamas rebuilds Gaza rule", "Yedioth"),
        ("21", "MIDEAST", "IRGC: no missile limits", "IRNA"),
        ("22", "OCEANIA", "M5.6 quake off New Caledonia", "USGS"),
        ("23", "US", "CBO: AUKUS sale shrinks US fleet", "The Guardian"),
        ("24", "ASIA", "Hong Kong Open: Satwik-Chirag in semis", "IANS"),
        ("25", "AFRICA", "Kenya: judiciary report out", "Nation"),
        ("26", "POLAND", "Jets scrambled near Chmielek", "Reuters"),
        ("27", "SAUDI ARABIA", "Houthi missile downed south", "Reuters"),
        ("28", "UKRAINE", "Drone hits Kharkiv hospital; 4 hurt", "Ukrinform"),
        ("29", "ARGENTINA", "Senate backs disability law 71–0", "Senate"),
        ("30", "US", "Army delays 68-barrel blast to Monday", "Reuters"),
        ("31", "SEOUL", "Ruling party to impeach Justice Cho", "JoongAng"),
        ("32", "NEW DELHI", "Pakistan minister heads SCO team", "IANS"),
        ("33", "WELLINGTON", "Nicholls 175* in 216-run stand", "AFP"),
        ("34", "SPORT", "Russell tops wet Vegas FP2", "F1"),
        ("35", "ASIA", "Modi opens first SCO forum", "ANI"),
        ("36", "OCEANIA", "NSW outback rain floods stations", "ABC"),
    ]
    brief_w = (CW - map_w - 16 - 16) // 2  # 310
    # v5: single-line briefs, each ending in an italic grey source tag.
    # Trade-off (reported): to fit prefix + text + tag on one line at
    # 11px, brief texts are shortened to ~25-40 chars and the tag is
    # 10px italic; the tag is never dropped to save space.
    f_bb = font(SANS_B, 11)
    f_br = font(SANS, 11)
    f_bt = font(SANS_I, 10)
    line_h, gap = 12, 2
    cols = [briefs[:12], briefs[12:]]
    briefs_h = 12 * line_h + 11 * gap  # 166
    map_h = max(130, briefs_h)
    draw_map(d, MARGIN, sec_top, map_w, map_h)
    for c in range(2):
        bx = briefs_x + c * (brief_w + 16)
        by = sec_top
        for num, tag, txt, src in cols[c]:
            pre = f"{num} · {tag} — "
            tag_s = f" ({src})"
            pre_w = d.textlength(pre, font=f_bb)
            txt_w = d.textlength(txt, font=f_br)
            tag_w = d.textlength(tag_s, font=f_bt)
            total = pre_w + txt_w + tag_w
            report.append((f"brief {num} width", round(total)))
            report.append((f"brief {num} fits", total <= brief_w))
            d.text((bx, by), pre, font=f_bb, fill=CRIMSON)
            d.text((bx + pre_w, by), txt, font=f_br, fill=INK)
            d.text((bx + pre_w + txt_w, by), tag_s, font=f_bt, fill=MUTED)
            by += line_h + gap
    y = sec_top + max(map_h, briefs_h) + 6
    report.append(("map/also ends", y))

    # ---- DATE CHECK box (rank-1 wording) ---------------------------------
    rule(d, MARGIN, y, CW, INK, 2)
    y += 6
    f_dc = font(SANS, 11)
    f_dcb = font(SANS_B, 11)
    dc = ("First reported Thursday 19 Nov, so NOT shown as Friday's news: "
          "Trump–Xi–Putin Shenzhen summit · Anthropic's $83 IPO pricing · ICJ "
          "Myanmar Rohingya verdict · GTA VI midnight launch · $190.4m Van Gogh "
          "sale · Voyager 1 one light-day confirmation · Senate 51–48 Iran vote.")
    dcl = wrap(d, dc, f_dc, CW - 24)
    box_h = len(dcl) * 13 + 24  # 7 top pad + 13 label line + body + 4 bottom pad
    d.rectangle([MARGIN, y, MARGIN + CW, y + box_h], fill=CARD_BG,
                outline=CRIMSON, width=1)
    d.text((MARGIN + 10, y + 7), "DATE CHECK", font=f_dcb, fill=CRIMSON)
    dc_y = text_block(d, MARGIN + 10, y + 7 + 13, dcl, f_dc, INK, 13)
    report.append(("date check lines", len(dcl)))
    y = y + box_h + 6

    # ---- Footer ------------------------------------------------------------
    f_ft = font(SANS, 11)
    d.text((MARGIN, y),
           "Every story here happened, or was first reported, on Friday 20 November 2026 "
           "in at least one time zone. Claims are attributed, not stated as fact.",
           font=f_ft, fill=MUTED)
    y += 11
    # v5: footer lists every outlet actually tagged on the page
    f_fs = font(SANS, 10)
    src_line = ("Sources: Reuters, AP, AFP, BBC, IMD, UN News, Al Jazeera, ICC, ESA, "
                "The Times, Politico, Egypt Independent, Google, USGS, The Guardian, "
                "IANS, Ukrinform, JoongAng, ANI, ABC, Yedioth, IRNA, F1, Nation, "
                "Senate. Original vector drawings.")
    sl = wrap(d, src_line, f_fs, CW)
    report.append(("footer source lines", len(sl)))
    y = text_block(d, MARGIN, y, sl, f_fs, MUTED, 11)
    report.append(("bottom y", y))

    out = os.path.join(BASE, "entry.png")
    img.save(out, "PNG")
    print("saved", out, os.path.getsize(out), "bytes")
    for k, v in report:
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
