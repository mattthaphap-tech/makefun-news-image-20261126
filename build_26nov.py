#!/usr/bin/env python3
"""Build the dense news front page for Thursday 26 November 2026.

35-story recipe (final-analysis band: 36 is the most common count in the
top 50; 35-36 is the centre of the winning band). Structure: 3 leads +
10 minis + 22 briefs, grouped under 7 explicit regions. Sizes: briefs
19px, lead headlines 22px, lead summaries 16px, mini headlines 16px.
No world map; dark ink on light paper; date prominent. Text neatness
(Matt's 25 Nov feedback): lead summaries and the date-check box are
JUSTIFIED, mini headlines are CENTRE-aligned, so column edges look tidy
instead of ragged. Every story drawn from the locked, verified research
list in research.md — no invented events, no wrong dates. Deterministic,
no network. Draws entry.png (1024x1024) with PIL only.
"""
import math
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 1024, 1024
PAPER = (246, 241, 229)
INK = (26, 26, 26)
RED = (179, 32, 42)
BLUE = (31, 78, 121)
GREEN = (30, 122, 52)
AMBER = (178, 106, 0)
GREY = (107, 107, 107)
RULE = (43, 43, 43)
LIGHT = (201, 194, 178)
WHITE = (255, 255, 255)

FDIR = "/usr/share/fonts/truetype/dejavu"


def font(name, size):
    return ImageFont.truetype(os.path.join(FDIR, name), size)


SERIF = "DejaVuSerif.ttf"
SERIFB = "DejaVuSerif-Bold.ttf"
SANS = "DejaVuSans.ttf"
SANSB = "DejaVuSans-Bold.ttf"

img = Image.new("RGB", (W, H), PAPER)
d = ImageDraw.Draw(img)
MX = 26  # side margin
CW = W - 2 * MX  # content width


# ---------- text helpers ----------
def wrap(text, fnt, max_w):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if fnt.getlength(t) <= max_w:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_wrapped(x, y, text, fnt, max_w, fill=INK, leading=None, max_lines=None):
    lines = wrap(text, fnt, max_w)
    if max_lines:
        lines = lines[:max_lines]
    lh = leading or int(fnt.size * 1.18)
    for ln in lines:
        d.text((x, y), ln, font=fnt, fill=fill)
        y += lh
    return y


def draw_justified(x, y, text, fnt, max_w, fill=INK, leading=None, max_lines=None):
    """Draw wrapped text fully justified (all lines except the last fill
    max_w by widening word gaps). Keeps column edges neat."""
    lines = wrap(text, fnt, max_w)
    if max_lines:
        lines = lines[:max_lines]
    lh = leading or int(fnt.size * 1.18)
    for i, ln in enumerate(lines):
        words = ln.split()
        if i < len(lines) - 1 and len(words) > 1:
            total = sum(fnt.getlength(w) for w in words)
            gap = (max_w - total) / (len(words) - 1)
            cx = x
            for w in words:
                d.text((cx, y), w, font=fnt, fill=fill)
                cx += fnt.getlength(w) + gap
        else:
            d.text((x, y), ln, font=fnt, fill=fill)
        y += lh
    return y


def fit_headline(x, y, text, max_w, max_lines, start_size, fill=INK, center=False):
    """Shrink headline until it fits in max_lines; return end y."""
    size = start_size
    while size > 10:
        fnt = font(SERIFB, size)
        lines = wrap(text, fnt, max_w)
        if len(lines) <= max_lines:
            break
        size -= 1
    lh = int(size * 1.12)
    for ln in lines[:max_lines]:
        if center:
            tw = fnt.getlength(ln)
            d.text((x + (max_w - tw) / 2, y), ln, font=fnt, fill=fill)
        else:
            d.text((x, y), ln, font=fnt, fill=fill)
        y += lh
    return y


def rule(y, w=2, x0=MX, x1=W - MX, fill=RULE):
    d.line([(x0, y), (x1, y)], fill=fill, width=w)


def chip(cx, cy, n, r=8, fill=RED):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=fill)
    t = str(n)
    f = font(SANSB, 10)
    tw = f.getlength(t)
    d.text((cx - tw / 2, cy - 7), t, font=f, fill=WHITE)


def tag(x, y, region, status, source, size=9):
    """Region tag + status tag on one line; returns width used."""
    f1 = font(SANSB, size)
    col = GREEN if status == "CONFIRMED" else (BLUE if status == "OFFICIALS" else AMBER)
    d.text((x, y), region, font=f1, fill=RED)
    w1 = f1.getlength(region)
    st = f"  {status} \u00b7 {source}"
    d.text((x + w1, y), st, font=f1, fill=col)
    return w1 + f1.getlength(st)


# ================= ILLUSTRATIONS (flat scenes, drawn in code) =================
def icon_base(w, h, bg):
    im = Image.new("RGB", (w, h), bg)
    return im, ImageDraw.Draw(im)


def _flame(dd, cx, base, s):
    """A small flame: outer orange, inner yellow."""
    dd.polygon([(cx, base - 2.2 * s), (cx + 0.9 * s, base - 0.6 * s),
                (cx + 0.7 * s, base), (cx - 0.7 * s, base),
                (cx - 0.9 * s, base - 0.6 * s)], fill=(230, 90, 20))
    dd.polygon([(cx, base - 1.2 * s), (cx + 0.5 * s, base - 0.2 * s),
                (cx + 0.35 * s, base), (cx - 0.35 * s, base),
                (cx - 0.5 * s, base - 0.2 * s)], fill=(255, 200, 40))


# ----- LEAD 1: missile rising at night, red glow, radiation trefoil -----
def lead_missile(w, h):
    im, dd = icon_base(w, h, (14, 20, 38))
    for sx, sy in [(12, 8), (44, 12), (76, 5), (250, 9), (292, 7), (205, 13), (150, 6)]:
        dd.ellipse([sx - 1, sy - 1, sx + 1, sy + 1], fill=WHITE)
    dd.polygon([(0, h), (0, h - 12), (90, h - 20), (180, h - 10), (w, h - 16), (w, h)],
               fill=(24, 34, 54))
    # dashed launch trajectory curving up to the missile nose
    import math
    for t in range(0, 21):
        u = t / 20
        tx = 40 + (160 - 40) * u
        ty = 8 + (30 - 8) * u * u
        dd.ellipse([tx - 2, ty - 2, tx + 2, ty + 2], fill=(255, 90, 60))
    # bigger missile: red nose cone, white body, fins, flame
    dd.polygon([(152, 30), (160, 14), (168, 30)], fill=(179, 32, 42))
    dd.polygon([(152, 30), (168, 30), (168, 68), (152, 68)], fill=(220, 220, 215))
    dd.rectangle([152, 44, 168, 48], fill=(179, 32, 42))
    dd.polygon([(152, 68), (142, 80), (152, 74)], fill=(179, 32, 42))
    dd.polygon([(168, 68), (178, 80), (168, 74)], fill=(179, 32, 42))
    _flame(dd, 160, 80, 7)
    for sx, sy, sr in [(150, 82, 6), (170, 84, 5), (160, 78, 4)]:
        dd.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(120, 118, 112))
    cx, cy, r = 272, 66, 12
    dd.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 215, 0))
    for a in (90, 210, 330):
        dd.pieslice([cx - r, cy - r, cx + r, cy + r], a - 28, a + 28,
                    fill=(14, 20, 38))
    dd.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=(255, 215, 0))
    return im


# ----- LEAD 2: Asian markets bounce — skyline, rising green line, +1.9% tag -----
def lead_bounce(w, h):
    im, dd = icon_base(w, h, (24, 34, 54))
    for x0, bw, bh in [(6, 18, 20), (28, 14, 28), (46, 20, 16), (70, 16, 26),
                       (90, 18, 18), (112, 14, 30), (130, 20, 14), (154, 18, 24),
                       (236, 18, 20), (258, 16, 26), (278, 20, 16)]:
        dd.rectangle([x0, h - bh, x0 + bw, h], fill=(48, 58, 78))
        for wy in range(h - bh + 4, h - 4, 6):
            for wx in range(x0 + 3, x0 + bw - 2, 6):
                dd.point((wx, wy), fill=(255, 210, 90))
    pts = [(8, 72), (40, 68), (72, 70), (104, 54), (136, 58), (168, 40),
           (200, 44), (232, 24), (264, 28), (296, 8)]
    dd.line(pts, fill=(90, 220, 120), width=4, joint="curve")
    dd.polygon([(296, 8), (282, 6), (292, 20)], fill=(90, 220, 120))
    for x, y in [(72, 70), (136, 58), (200, 44)]:
        dd.ellipse([x - 3, y - 3, x + 3, y + 3], fill=(90, 220, 120))
    f = font(SANSB, 15)
    t = "+1.9%"
    tw = f.getlength(t)
    dd.rectangle([w - tw - 18, 8, w - 8, 30], fill=(30, 122, 52))
    dd.text((w - tw - 13, 10), t, font=f, fill=WHITE)
    return im


# ----- LEAD 3: Thanksgiving nor'easter — dark clouds, rain, waves, bent tree -----
def lead_storm(w, h):
    im, dd = icon_base(w, h, (40, 52, 70))
    for cx, cy, r in [(60, 18, 22), (110, 12, 26), (170, 18, 22), (230, 14, 24), (280, 20, 20)]:
        dd.ellipse([cx - r, cy - r // 2, cx + r, cy + r // 2], fill=(70, 78, 92))
    for rx in range(10, w - 6, 18):
        dd.line([(rx, 34), (rx - 5, 52)], fill=(150, 180, 210), width=2)
    dd.rectangle([0, 56, w, h], fill=(36, 84, 122))
    for yy in (62, 72, 82):
        for xx in range(6, w - 8, 34):
            dd.line([(xx, yy), (xx + 14, yy - 2), (xx + 28, yy)], fill=(110, 165, 200), width=2)
    dd.rectangle([0, 52, w, 56], fill=(24, 34, 54))
    dd.polygon([(46, 56), (52, 30), (58, 56)], fill=(90, 70, 40))
    dd.polygon([(38, 44), (60, 44), (52, 26)], fill=(30, 90, 50))
    dd.polygon([(40, 36), (58, 36), (51, 20)], fill=(36, 110, 60))
    for gy in (30, 40, 50):
        dd.line([(200, gy), (260, gy - 4)], fill=(220, 230, 240), width=2)
        dd.line([(260, gy - 4), (250, gy - 8)], fill=(220, 230, 240), width=2)
    f = font(SANSB, 13)
    t = "70 mph"
    tw = f.getlength(t)
    dd.rectangle([w - tw - 16, 4, w - 6, 24], fill=(179, 32, 42))
    dd.text((w - tw - 11, 6), t, font=f, fill=WHITE)
    return im


# ----- MINI icons (186 x 36 flat scenes) -----
def icon_breach(w, h):
    """Cyber breach: dark screen, broken padlock, red alert triangle."""
    im, dd = icon_base(w, h, (24, 34, 54))
    dd.rectangle([18, 6, 118, h - 8], fill=(16, 22, 34), outline=(120, 140, 160), width=2)
    dd.rectangle([58, h - 8, 78, h - 4], fill=(120, 140, 160))
    dd.rounded_rectangle([56, 14, 80, 28], radius=3, fill=(255, 215, 0))
    dd.arc([60, 4, 76, 18], 180, 360, fill=(255, 215, 0), width=3)
    dd.line([(76, 6), (84, 2)], fill=(255, 215, 0), width=3)
    dd.ellipse([65, 18, 71, 24], fill=(24, 34, 54))
    ax, ay = 150, h // 2 + 1
    dd.polygon([(ax, ay - 14), (ax + 16, ay + 10), (ax - 16, ay + 10)], fill=(235, 60, 60))
    dd.text((ax - 2, ay - 9), "!", font=font(SANSB, 13), fill=WHITE)
    return im


def icon_shield(w, h):
    """NATO: blue shield with compass star beside a Polish flag."""
    im, dd = icon_base(w, h, (18, 40, 80))
    for i in range(14):
        a = math.pi * 2 * i / 14
        dd.ellipse([18 + 60 * math.cos(a) - 1, 12 + 8 * math.sin(a) - 1,
                    18 + 60 * math.cos(a) + 1, 12 + 8 * math.sin(a) + 1], fill=(255, 215, 0))
    cx, cy = 62, h // 2 + 1
    dd.polygon([(cx - 22, cy - 17), (cx + 22, cy - 17), (cx + 22, cy + 1),
                (cx, cy + 21), (cx - 22, cy + 1)], fill=(31, 78, 121),
               outline=(255, 215, 0))
    dd.polygon([(cx, cy - 13), (cx + 3, cy - 3), (cx + 13, cy), (cx + 3, cy + 3),
                (cx, cy + 13), (cx - 3, cy + 3), (cx - 13, cy), (cx - 3, cy - 3)],
               fill=WHITE)
    dd.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=(31, 78, 121))
    dd.line([(128, 6), (128, h - 6)], fill=(230, 230, 230), width=2)
    dd.rectangle([128, 8, 168, 20], fill=WHITE)
    dd.rectangle([128, 20, 168, 32], fill=(200, 30, 30))
    return im


def icon_gavel(w, h):
    """Courthouse columns + gavel."""
    im, dd = icon_base(w, h, (24, 44, 84))
    dd.polygon([(18, 8), (58, 2), (98, 8)], fill=(230, 230, 225))
    for cx in (26, 44, 62, 80):
        dd.rectangle([cx - 3, 10, cx + 3, h - 6], fill=(230, 230, 225))
    dd.rectangle([14, h - 6, 102, h - 2], fill=(230, 230, 225))
    dd.line([(128, 26), (158, 8)], fill=(150, 110, 60), width=4)
    dd.rectangle([150, 4, 172, 14], fill=(120, 80, 40))
    dd.rectangle([124, h - 12, 168, h - 8], fill=(150, 110, 60))
    return im


def icon_server(w, h):
    """AI server racks with a rising green line."""
    im, dd = icon_base(w, h, (16, 28, 44))
    for rx in (14, 52, 90):
        dd.rectangle([rx, 5, rx + 30, h - 5], fill=(40, 56, 76), outline=(120, 140, 160))
        for ry in range(9, h - 8, 7):
            dd.line([(rx + 4, ry), (rx + 18, ry)], fill=(90, 220, 120), width=2)
            dd.ellipse([rx + 23, ry - 1, rx + 26, ry + 2], fill=(255, 210, 90))
    pts = [(128, h - 8), (146, h - 18), (160, h - 14), (176, h - 26)]
    dd.line(pts, fill=(90, 220, 120), width=3, joint="curve")
    dd.polygon([(176, h - 26), (166, h - 24), (174, h - 16)], fill=(90, 220, 120))
    return im


def icon_chipfall(w, h):
    """Green chip + plunging red line."""
    im, dd = icon_base(w, h, (16, 40, 26))
    dd.rounded_rectangle([16, 6, 76, h - 6], radius=4, fill=(20, 110, 60))
    for px in (28, 40, 52, 64):
        dd.line([(px, 2), (px, 6)], fill=(180, 220, 190), width=2)
        dd.line([(px, h - 6), (px, h - 2)], fill=(180, 220, 190), width=2)
    dd.rectangle([30, 12, 62, h - 12], fill=(10, 70, 40), outline=(255, 215, 0))
    dd.text((37, 15), "AI", font=font(SANSB, 10), fill=(255, 215, 0))
    pts = [(92, 6), (112, 12), (132, 10), (152, 22), (172, 20), (182, 30)]
    dd.line(pts, fill=(235, 60, 60), width=3, joint="curve")
    dd.polygon([(182, 30), (172, 26), (178, 36)], fill=(235, 60, 60))
    return im


def icon_gaza(w, h):
    """Damaged block at dusk, smoke column, small UN flag."""
    im, dd = icon_base(w, h, (70, 52, 44))
    dd.rectangle([0, 0, w, 12], fill=(120, 70, 50))
    dd.ellipse([w - 28, 2, w - 12, 18], fill=(255, 210, 140))
    dd.rectangle([14, 12, 84, h], fill=(150, 148, 140))
    dd.polygon([(14, 12), (34, 20), (14, 24)], fill=(90, 88, 84))
    for wx in range(22, 78, 12):
        dd.rectangle([wx, 18, wx + 6, 24], fill=(255, 210, 90))
    for sx, sy, sr in [(96, 10, 5), (104, 4, 4), (90, 4, 3)]:
        dd.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(200, 195, 185))
    dd.line([(128, 8), (128, h - 4)], fill=(230, 230, 230), width=2)
    dd.rectangle([128, 8, 168, 20], fill=(40, 90, 180))
    dd.ellipse([142, 11, 154, 17], outline=WHITE, width=1)
    return im


def icon_medal(w, h):
    """Gold medal on a red-white-blue ribbon."""
    im, dd = icon_base(w, h, (24, 44, 84))
    dd.polygon([(78, 2), (92, 2), (88, 16), (82, 16)], fill=(200, 30, 30))
    dd.polygon([(92, 2), (106, 2), (102, 16), (96, 16)], fill=WHITE)
    dd.polygon([(106, 2), (120, 2), (116, 16), (110, 16)], fill=(31, 78, 121))
    cx, cy = 96, h // 2 + 6
    dd.ellipse([cx - 13, cy - 13, cx + 13, cy + 13], fill=(255, 215, 0),
               outline=(178, 140, 0), width=2)
    dd.polygon([(cx, cy - 8), (cx + 2, cy - 2), (cx + 8, cy - 2), (cx + 3, cy + 2),
                (cx + 5, cy + 8), (cx, cy + 4), (cx - 5, cy + 8), (cx - 3, cy + 2),
                (cx - 8, cy - 2), (cx - 2, cy - 2)], fill=(179, 32, 42))
    for sx in (24, 158):
        dd.polygon([(sx, 8), (sx + 2, 13), (sx + 7, 13), (sx + 3, 16),
                    (sx + 5, 21), (sx, 18), (sx - 5, 21), (sx - 3, 16),
                    (sx - 7, 13), (sx - 2, 13)], fill=(255, 215, 0))
    return im


def icon_eu(w, h):
    """EU circle of stars + red ban slash over a Russian flag."""
    im, dd = icon_base(w, h, (20, 60, 140))
    cx, cy = 48, h // 2
    for i in range(12):
        a = math.pi * 2 * i / 12 - math.pi / 2
        dd.ellipse([cx + 26 * math.cos(a) - 2, cy + 12 * math.sin(a) - 2,
                    cx + 26 * math.cos(a) + 2, cy + 12 * math.sin(a) + 2],
                   fill=(255, 215, 0))
    fx, fy = 108, 8
    dd.rectangle([fx, fy, fx + 52, fy + 8], fill=WHITE)
    dd.rectangle([fx, fy + 8, fx + 52, fy + 16], fill=(20, 60, 140))
    dd.rectangle([fx, fy + 16, fx + 52, fy + 24], fill=(200, 30, 30))
    dd.line([(fx - 4, fy + 28), (fx + 56, fy - 4)], fill=(230, 40, 40), width=4)
    return im


def icon_bank(w, h):
    """Central bank: columns + % sign + rising arrow (rate hike)."""
    im, dd = icon_base(w, h, (24, 44, 84))
    dd.polygon([(14, 10), (58, 4), (102, 10)], fill=(230, 230, 225))
    for cx in (24, 44, 64, 84):
        dd.rectangle([cx - 3, 12, cx + 3, h - 6], fill=(230, 230, 225))
    dd.rectangle([10, h - 6, 106, h - 2], fill=(230, 230, 225))
    f = font(SANSB, 15)
    dd.text((126, 4), "%", font=f, fill=(255, 215, 0))
    pts = [(124, h - 8), (140, h - 16), (154, h - 12), (170, h - 24)]
    dd.line(pts, fill=(90, 220, 120), width=3, joint="curve")
    dd.polygon([(170, h - 24), (160, h - 22), (168, h - 14)], fill=(90, 220, 120))
    return im


def icon_summit(w, h):
    """EU summit: circle of stars + round table."""
    im, dd = icon_base(w, h, (20, 60, 140))
    cx, cy = 44, h // 2
    for i in range(12):
        a = math.pi * 2 * i / 12 - math.pi / 2
        dd.ellipse([cx + 22 * math.cos(a) - 2, cy + 11 * math.sin(a) - 2,
                    cx + 22 * math.cos(a) + 2, cy + 11 * math.sin(a) + 2],
                   fill=(255, 215, 0))
    dd.ellipse([96, 16, 176, 32], fill=(120, 90, 60))
    dd.rectangle([100, 24, 172, 28], fill=(90, 66, 44))
    for fx in (108, 130, 152):
        dd.ellipse([fx - 4, 6, fx + 4, 14], fill=(255, 215, 0))
    return im


def icon_chess(w, h):
    """Chess board + king piece + pawn."""
    im, dd = icon_base(w, h, (250, 247, 238))
    for r in range(4):
        for c in range(8):
            if (r + c) % 2 == 0:
                dd.rectangle([10 + c * 8, 4 + r * 8, 18 + c * 8, 12 + r * 8],
                             fill=(26, 26, 26))
    kx = 108
    dd.rectangle([kx, 8, kx + 16, 12], fill=(26, 26, 26))
    dd.polygon([(kx + 8, 2), (kx + 11, 8), (kx + 5, 8)], fill=(26, 26, 26))
    dd.rectangle([kx + 2, 12, kx + 14, 26], fill=(26, 26, 26))
    dd.rectangle([kx - 2, 26, kx + 18, 30], fill=(26, 26, 26))
    px = 150
    dd.ellipse([px, 16, px + 10, 26], fill=(255, 255, 255), outline=(26, 26, 26))
    dd.rectangle([px - 2, 26, px + 12, 30], fill=(255, 255, 255), outline=(26, 26, 26))
    return im


def icon_rocket(w, h):
    """Rocket launching, flame below, stars."""
    im, dd = icon_base(w, h, (14, 20, 38))
    for sx, sy in [(14, 6), (60, 10), (170, 6), (150, 12)]:
        dd.ellipse([sx - 1, sy - 1, sx + 1, sy + 1], fill=WHITE)
    dd.polygon([(86, 6), (94, 6), (96, 22), (84, 22)], fill=(220, 220, 215))
    dd.polygon([(90, 6), (86, 12), (94, 12)], fill=(179, 32, 42))
    dd.polygon([(84, 22), (78, 30), (84, 26)], fill=(179, 32, 42))
    dd.polygon([(96, 22), (102, 30), (96, 26)], fill=(179, 32, 42))
    _flame(dd, 90, 30, 6)
    for sx, sy, sr in [(82, 32, 4), (98, 33, 4)]:
        dd.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(120, 118, 112))
    return im


def icon_storm_mini(w, h):
    """Storm cloud + rain + lightning bolt."""
    im, dd = icon_base(w, h, (40, 52, 70))
    for cx, cy, r in [(60, 14, 18), (100, 10, 22), (140, 14, 18)]:
        dd.ellipse([cx - r, cy - r // 2, cx + r, cy + r // 2], fill=(70, 78, 92))
    for rx in range(16, 120, 16):
        dd.line([(rx, 26), (rx - 4, 34)], fill=(150, 180, 210), width=2)
    dd.polygon([(150, 8), (138, 24), (148, 24), (140, 34), (158, 18), (148, 18)],
               fill=(255, 215, 0))
    return im


def icon_ship(w, h):
    """Container ship + 15% tariff tag (trade)."""
    im, dd = icon_base(w, h, (214, 226, 232))
    dd.rectangle([0, 26, w, h], fill=(36, 84, 122))
    for yy in (30, 36):
        for xx in range(6, w - 8, 30):
            dd.line([(xx, yy), (xx + 12, yy - 2), (xx + 24, yy)], fill=(110, 165, 200), width=2)
    dd.polygon([(30, 22), (150, 22), (142, 32), (38, 32)], fill=(40, 40, 46))
    for cx0, col in [(44, (179, 32, 42)), (70, (31, 78, 121)), (96, (178, 106, 0))]:
        dd.rectangle([cx0, 12, cx0 + 22, 22], fill=col)
    dd.rectangle([126, 10, 148, 22], fill=(240, 240, 235))
    f = font(SANSB, 11)
    dd.text((158, 12), "15%", font=f, fill=(179, 32, 42))
    return im


def icon_parade(w, h):
    """Parade balloons over a street (Macy's 100th)."""
    im, dd = icon_base(w, h, (178, 214, 232))
    for cx, cy, col in [(52, 14, (179, 32, 42)), (96, 10, (255, 215, 0)), (140, 15, (31, 78, 121))]:
        dd.ellipse([cx - 12, cy - 9, cx + 12, cy + 9], fill=col, outline=(26, 26, 26))
        dd.line([(cx, cy + 9), (cx - 3, cy + 20), (cx + 3, cy + 26)], fill=(26, 26, 26), width=1)
    dd.rectangle([0, h - 6, w, h], fill=(90, 90, 90))
    f = font(SANSB, 10)
    dd.text((8, 2), "100th", font=f, fill=(179, 32, 42))
    return im


def icon_station(w, h):
    """Space station: central module + solar wings, stars."""
    im, dd = icon_base(w, h, (14, 20, 38))
    for sx, sy in [(12, 6), (44, 10), (168, 8), (150, 14)]:
        dd.ellipse([sx - 1, sy - 1, sx + 1, sy + 1], fill=WHITE)
    dd.rectangle([18, 15, 62, 23], fill=(31, 78, 121))
    for xx in range(20, 60, 8):
        dd.line([(xx, 15), (xx, 23)], fill=(120, 170, 210), width=1)
    dd.rectangle([86, 12, 100, 26], fill=(220, 220, 215))
    dd.rectangle([124, 15, 168, 23], fill=(31, 78, 121))
    for xx in range(126, 166, 8):
        dd.line([(xx, 15), (xx, 23)], fill=(120, 170, 210), width=1)
    dd.ellipse([70, 4, 78, 12], fill=(255, 215, 0))
    return im


def icon_india_ballot(w, h):
    """Indian tricolour + ballot box with two papers."""
    im, dd = icon_base(w, h, (250, 247, 238))
    dd.line([(14, 6), (14, h - 8)], fill=(120, 110, 90), width=2)
    dd.polygon([(14, 8), (28, 6), (42, 9), (56, 7), (56, 30), (42, 32),
                (28, 29), (14, 31)], fill=(255, 153, 51))
    dd.polygon([(14, 16), (28, 14), (42, 17), (56, 15), (56, 23), (42, 25),
                (28, 22), (14, 24)], fill=WHITE)
    dd.polygon([(14, 24), (28, 22), (42, 25), (56, 23), (56, 30), (42, 32),
                (28, 29), (14, 31)], fill=(19, 136, 8))
    dd.ellipse([31, 16, 39, 24], outline=(31, 78, 121), width=1)
    dd.rectangle([104, h - 18, 148, h - 4], fill=(179, 32, 42))
    dd.rectangle([104, h - 20, 148, h - 17], fill=(140, 24, 32))
    dd.polygon([(114, h - 32), (126, h - 32), (124, h - 19), (116, h - 19)], fill=WHITE)
    dd.polygon([(132, h - 30), (144, h - 30), (142, h - 19), (134, h - 19)], fill=(255, 215, 0))
    return im


def icon_flags_us_il(w, h):
    """US flag + Israeli flag side by side."""
    im, dd = icon_base(w, h, (250, 247, 238))
    dd.rectangle([10, 8, 78, 28], fill=WHITE, outline=(26, 26, 26))
    for i in range(7):
        dd.rectangle([10, 8 + i * 3, 78, 10 + i * 3], fill=(179, 32, 42))
    dd.rectangle([10, 8, 34, 18], fill=(31, 78, 121))
    for sx in (15, 22, 29):
        for sy in (11, 15):
            dd.ellipse([sx - 1, sy - 1, sx + 1, sy + 1], fill=WHITE)
    dd.rectangle([108, 8, 176, 28], fill=WHITE, outline=(26, 26, 26))
    dd.rectangle([108, 8, 176, 12], fill=(31, 78, 121))
    dd.rectangle([108, 24, 176, 28], fill=(31, 78, 121))
    cx, cy = 142, 18
    dd.polygon([(cx, cy - 6), (cx + 5, cy + 4), (cx - 5, cy + 4)], outline=(31, 78, 121))
    dd.polygon([(cx, cy + 6), (cx + 5, cy - 4), (cx - 5, cy - 4)], outline=(31, 78, 121))
    return im


ICONS = {
    "breach": icon_breach, "shield": icon_shield, "gavel": icon_gavel,
    "server": icon_server, "chipfall": icon_chipfall, "gaza": icon_gaza,
    "medal": icon_medal, "eu": icon_eu, "india_ballot": icon_india_ballot,
    "flags_us_il": icon_flags_us_il, "bank": icon_bank, "summit": icon_summit,
    "chess": icon_chess, "rocket": icon_rocket, "storm": icon_storm_mini,
    "ship": icon_ship, "parade": icon_parade, "station": icon_station,
}
LEAD_DRAW = {"missile": lead_missile, "bounce": lead_bounce, "storm": lead_storm}

# ================= DATA (locked research list, research.md) =================
LEADS = [
    dict(n=1, region="ASIA \u00b7 N. KOREA", status="CONFIRMED", source="KCNA",
         img="missile",
         headline="Kim orders wider deployment of tactical nuclear arms",
         summary="North Korea will spread tactical nuclear weapons across "
                 "more domains and expand nuclear material output, KCNA says."),
    dict(n=2, region="MARKETS \u00b7 ASIA", status="CONFIRMED", source="REUTERS",
         img="bounce",
         headline="Asian shares bounce back after tariff rout",
         summary="Nikkei +1.6%, Korea +1.9% as Wall Street fights back from "
                 "deep lows; Brent holds $94.81, gold $3,566."),
    dict(n=3, region="USA \u00b7 WEATHER", status="CONFIRMED", source="NJ.GOV",
         img="storm",
         headline="Thanksgiving nor'easter slams New Jersey",
         summary="State of emergency in all 21 counties; gusts to 70 mph, "
                 "severe tidal flooding at its worst on Thanksgiving Day."),
]

MINIS = [
    dict(n=4, region="ASIA \u00b7 KOREA", status="CONFIRMED", source="REUTERS", icon="bank",
         headline="Bank of Korea hikes rate to 3.25%"),
    dict(n=5, region="ASIA \u00b7 TAIWAN", status="CONFIRMED", source="REUTERS", icon="ship",
         headline="Taiwan to keep 15% US tariff rate"),
    dict(n=6, region="UKRAINE WAR \u00b7 EU", status="CONFIRMED", source="CONSILIUM", icon="summit",
         headline="EU leaders open summit on budget, Ukraine"),
    dict(n=7, region="ASIA \u00b7 INDIA", status="CONFIRMED", source="REUTERS", icon="rocket",
         headline="Uber names Rakesh Ranjan India chief"),
    dict(n=8, region="ASIA \u00b7 JAPAN", status="CONFIRMED", source="REUTERS", icon="server",
         headline="China firms press Japanese rivals, survey"),
    dict(n=9, region="EUROPE \u00b7 CHESS", status="CONFIRMED", source="FIDE", icon="chess",
         headline="Chess title game 3 today, scores level 1-1"),
    dict(n=10, region="EUROPE \u00b7 UK", status="CONFIRMED", source="BBC", icon="gavel",
         headline="UK to publish new EU treaties this afternoon"),
    dict(n=11, region="EUROPE \u00b7 UK", status="CONFIRMED", source="THE TIMES", icon="shield",
         headline="MoD writes to 100,000 reservists: be ready"),
    dict(n=12, region="USA \u00b7 THANKSGIVING", status="CONFIRMED", source="USA TODAY", icon="parade",
         headline="Macy's 100th parade postponed to Saturday"),
    dict(n=13, region="WORLD \u00b7 SPACE", status="CONFIRMED", source="NASA", icon="station",
         headline="Progress 97 cargo ship docks at ISS today"),
]

BRIEFS = [
    ("USA", "NFL Thanksgiving tripleheader today"),
    ("EUROPE", "Europa League matchday 5: 18 games"),
    ("USA", "Salmonella in 43% of Butterball turkey"),
    ("USA", "Philly parade loses its balloons"),
    ("MARKETS", "US markets shut for Thanksgiving"),
    ("EUROPE", "London Tube strike begins today"),
    ("EUROPE", "BBC faces antisemitism inquiry"),
    ("EUROPE", "Steinmeier ends Africa tour in Kenya"),
    ("MIDDLE EAST", "Saudis hold two Nigerians over drugs"),
    ("WORLD", "Nigeria FX turnover crashes 82% in a day"),
    ("WORLD", "Malema defamation bid fails in court"),
    ("WORLD", "13 remanded for impersonating officers"),
    ("ASIA", "Vietnam racing to finalise US trade deal"),
    ("WORLD", "DRC launches EKOKI anti-violence drive"),
    ("WORLD", "Sheinbaum pledges gambling-law reform"),
    ("WORLD", "Betting yields R$12bn in Brazil tax"),
    ("UKRAINE WAR", "Ukrainians await residency pathways"),
    ("USA", "National Day of Mourning in Plymouth"),
    ("ASIA", "SC notice on UAPA bail pleas in Delhi"),
    ("ASIA", "Tamil Nadu lines up 70 investment MoUs"),
    ("ASIA", "46,000 police for Andhra polls today"),
    ("ASIA", "US: tariff figures are ceilings, not duties"),
]

NUMBERS = [
    ("+1.6%", "Nikkei bounce"),
    ("+1.9%", "Korean shares"),
    ("3.25%", "Bank of Korea rate"),
    ("70 mph", "NJ storm gusts"),
    ("$94.81", "Brent crude"),
    ("43%", "Butterball salmonella"),
]

DATE_CHECK = ("Left out on purpose \u2014 earlier news: Cairo tanker fire, Sudan "
              "strikes, Melania's 9 children, US tariff plan, Shenzhou-24, turkey "
              "pardon, Hera images \u2014 all 24\u201325 Nov, not today.")

SOURCES = ("Sources: Reuters \u00b7 KCNA \u00b7 NJ.gov \u00b7 BBC \u00b7 The Times \u00b7 "
           "Consilium \u00b7 FIDE \u00b7 NASA \u00b7 The Guardian \u00b7 The Hindu \u00b7 "
           "CNA \u00b7 UEFA \u00b7 Punch \u00b7 News24.")

# Region strip counts, filled from the final story list (must sum to 35).
REGION_COUNTS = [
    ("UKRAINE WAR", 2), ("MIDDLE EAST", 1), ("ASIA", 10), ("EUROPE", 7),
    ("USA", 6), ("MARKETS", 2), ("WORLD", 7),
]

# ================= LAYOUT (v5: legibility-first) =================
y = 12
# eyebrow
f_eye = font(SANSB, 13)
d.text((MX, y), "THE WORLD'S NEWS OF ONE DAY", font=f_eye, fill=RED)
right = "35 STORIES \u00b7 7 REGIONS \u00b7 ALL FROM THIS THURSDAY"
d.text((W - MX - f_eye.getlength(right), y), right, font=f_eye, fill=INK)
y += 20
# masthead
d.text((MX, y), "Thursday 26 November 2026", font=font(SERIFB, 46), fill=INK)
y += 54
rule(y, 3)
rule(y + 5, 1)
y += 8
# region strip: the 7 regions with story counts, explicit in the layout
f_reg = font(SANSB, 12)
rx = MX
d.text((rx, y), "7 REGIONS:", font=f_reg, fill=RED)
rx += f_reg.getlength("7 REGIONS:  ")
for idx, (name, cnt) in enumerate(REGION_COUNTS):
    t = f"{name} {cnt}"
    d.text((rx, y), t, font=f_reg, fill=INK)
    rx += f_reg.getlength(t)
    if idx < len(REGION_COUNTS) - 1:
        d.text((rx, y), "  \u00b7  ", font=f_reg, fill=GREY)
        rx += f_reg.getlength("  \u00b7  ")
y += 17
rule(y, 1)
y += 6
# numbers strip
d.text((MX, y), "THE DAY IN NUMBERS", font=font(SANSB, 12), fill=RED)
y += 15
col_w = CW / 6
for i, (num, lab) in enumerate(NUMBERS):
    x = MX + i * col_w
    if i:
        d.line([(x - 6, y), (x - 6, y + 40)], fill=LIGHT, width=1)
    d.text((x, y), num, font=font(SERIFB, 22), fill=INK)
    draw_wrapped(x, y + 25, lab, font(SANS, 13), col_w - 14, fill=GREY, max_lines=2)
y += 44
rule(y, 1)
y += 6
# ---- leads ----
lead_w = (CW - 2 * 12) // 3
lead_img_h = 88
lead_end = y
for i, L in enumerate(LEADS):
    x = MX + i * (lead_w + 12)
    im = LEAD_DRAW[L["img"]](lead_w, lead_img_h)
    img.paste(im, (x, y))
    d.rectangle([x, y, x + lead_w - 1, y + lead_img_h - 1], outline=RULE, width=1)
    yy = y + lead_img_h + 5
    chip(x + 9, yy + 7, L["n"], r=9)
    tag(x + 22, yy, L["region"], L["status"], L["source"], size=12)
    yy += 17
    yy = fit_headline(x, yy, L["headline"], lead_w, 3, 22)
    yy += 2
    yy = draw_justified(x, yy, L["summary"], font(SANS, 16), lead_w, max_lines=3, leading=19)
    lead_end = max(lead_end, yy)
y = lead_end + 4
rule(y, 1)
y += 6
# ---- minis: 2 rows x 5 cols ----
mini_w = (CW - 4 * 10) // 5
mini_h = 106
mini_img_h = 36
for row in range(2):
    row_top = y + row * (mini_h + 8)
    for col in range(5):
        M = MINIS[row * 5 + col]
        x = MX + col * (mini_w + 10)
        im = ICONS[M["icon"]](mini_w, mini_img_h)
        img.paste(im, (x, row_top))
        d.rectangle([x, row_top, x + mini_w - 1, row_top + mini_img_h - 1], outline=RULE, width=1)
        yy = row_top + mini_img_h + 4
        chip(x + 7, yy + 6, M["n"], r=7)
        d.text((x + 17, yy), M["region"], font=font(SANSB, 11), fill=RED)
        yy += 14
        yy = fit_headline(x, yy, M["headline"], mini_w, 2, 16, center=True)
        yy += 1
        tag(x, yy, "", M["status"], M["source"], size=11)
y = y + 2 * mini_h + 8
rule(y, 1)
y += 6
# ---- briefs: full width, 2 cols x 11 rows, 19px ----
def trunc(text, fnt, max_w):
    if fnt.getlength(text) <= max_w:
        return text
    while text and fnt.getlength(text + "\u2026") > max_w:
        text = text[:-1]
    return text + "\u2026"

d.text((MX, y), "ALSO ON THURSDAY 26 NOVEMBER", font=font(SANSB, 13), fill=RED)
by = y + 18
bcol_w = (CW - 16) // 2
f_brief = font(SANS, 19)
f_btag = font(SANSB, 11)
chip_colors = [RED, (31, 78, 121), (30, 122, 52), (178, 106, 0), (110, 60, 140), (0, 130, 130)]
truncated = []
for i, (rtag, b) in enumerate(BRIEFS):
    col = i // 11
    rowi = i % 11
    x = MX + col * (bcol_w + 16)
    yy = by + rowi * 23
    chip(x + 9, yy + 9, 14 + i, r=9, fill=chip_colors[i % 6])
    tw = f_btag.getlength(rtag)
    d.text((x + 22, yy + 3), rtag, font=f_btag, fill=RED)
    t = trunc(b, f_brief, bcol_w - 24 - tw - 6)
    if t != b:
        truncated.append(b)
        print("TRUNCATED brief:", b)
    d.text((x + 22 + tw + 6, yy), t, font=f_brief, fill=INK)
y = by + 11 * 23 + 4
rule(y, 2)
y += 6
# date check box
d.rectangle([MX, y, W - MX - 1, y + 44], outline=RED, width=1)
lab = "DATE CHECK"
lab_w = font(SANSB, 13).getlength(lab)
d.text((MX + 8, y + 5), lab, font=font(SANSB, 13), fill=RED)
draw_justified(MX + 8 + lab_w + 10, y + 5, DATE_CHECK, font(SANS, 14), W - 2 * MX - 8 - lab_w - 10 - 8, max_lines=2, leading=17)
y += 50
# footer
d.text((MX, y), "Every story here happened, or was first reported, on Thursday 26 November 2026; claims are attributed.",
       font=font(SANS, 12), fill=GREY)
y += 15
d.text((MX, y), SOURCES, font=font(SANS, 12), fill=GREY)
y += 15

img.save(os.path.join(HERE, "entry.png"))
print("saved entry.png", img.size, "final y:", y)
if y > H:
    print("WARNING: content overflows the 1024px frame by", y - H, "px")
if truncated:
    print("TRUNCATED briefs:", len(truncated))
else:
    print("all briefs fit without truncation")
