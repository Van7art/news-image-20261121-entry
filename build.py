#!/usr/bin/env python3
"""Build three 1024x1024 PNG variants summing up the world news of
Saturday 21 November 2026. All text is drawn with PIL (DejaVu) so it
stays crisp; all artwork is drawn with PIL primitives. No network,
no AI-generated imagery.

Stories (all verified by web search on 21 Nov 2026, see NOTES.md).
Time-zone note: the day's big events happened late on Friday 20 Nov
in Western time zones and were first reported across Asia on
Saturday 21 Nov (AP's Poland story went out 17:15 EST 20 Nov =
06:15 WITA 21 Nov; the US market close was reported Saturday
morning in Asia). The rules count events first reported on
21 November in any time zone. Items dated 21 Nov in UTC itself:
COP31 overtime (01:56 UTC), the Riyadh intercepts (Reuters, Nov 21),
the Wellington Test day three.
 1. Russian missiles land in Poland (AP / Reuters)
 2. Wall Street slides into correction (AP / Motley Fool)
 3. Claude 'proves' the Riemann Hypothesis - claim (Sci. American)
 4. COP31 runs into overtime, Antalya (AP / BNN Bloomberg)
 5. Saudi Arabia intercepts three Houthi missiles (Reuters, Nov 21)
 6. Cyclone Akvan crosses Odisha, no lives lost (IMD)
 7. KL Rahul's century in Wellington (AP / IANS)
 8. NSE becomes world's 5th-largest listed exchange (ANI)
"""
import math
import os
from PIL import Image, ImageDraw, ImageFont

W = H = 1024
OUT = os.path.dirname(os.path.abspath(__file__))

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

def F(path, size):
    return ImageFont.truetype(path, size)

def wrap(draw, text, font, max_w):
    """Greedy word wrap returning a list of lines that fit max_w."""
    lines, cur = [], ""
    for word in text.split(" "):
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=font) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines

def para(draw, xy, text, font, fill, max_w, leading=None):
    x, y = xy
    leading = leading or int(font.size * 1.28)
    for line in wrap(draw, text, font, max_w):
        draw.text((x, y), line, font=font, fill=fill)
        y += leading
    return y

def headline(draw, xy, text, font, fill, max_w, leading=None):
    return para(draw, xy, text, font, fill, max_w, leading)

def rule(draw, x0, y, x1, w=2, fill=(30, 30, 30)):
    draw.line([(x0, y), (x1, y)], fill=fill, width=w)

def badge(draw, cx, cy, r, num, fill, fg=(255, 255, 255)):
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=fill)
    f = F(SANS_B, int(r * 1.05))
    tw = draw.textlength(str(num), font=f)
    th = f.size
    draw.text((cx - tw / 2, cy - th / 2 - 1), str(num), font=f, fill=fg)

# ---------------------------------------------------------------- icons
def draw_cyclone(draw, cx, cy, R, col=(255, 255, 255), col2=(140, 200, 240)):
    """Spiral storm: concentric arcs rotating inward."""
    for i, r in enumerate(range(R, 8, -14)):
        a0 = i * 55
        a1 = a0 + 300
        draw.arc([cx - r, cy - r, cx + r, cy + r], a0, a1,
                 fill=col2 if i % 2 else col, width=9)
    draw.ellipse([cx - 12, cy - 12, cx + 12, cy + 12], fill=col)
    for k in range(10):
        ang = math.radians(k * 36 + 15)
        x0 = cx + int(math.cos(ang) * (R + 18))
        y0 = cy + int(math.sin(ang) * (R + 18))
        x1 = cx + int(math.cos(ang) * (R + 34))
        y1 = cy + int(math.sin(ang) * (R + 34))
        draw.line([(x0, y0), (x1, y1)], fill=col2, width=4)

def draw_missile(draw, cx, cy, s):
    """Streaking missile on a night sky: body, fins, flame, trail."""
    # trail
    for i in range(5):
        x0 = cx - s - i * 26
        draw.line([(x0, cy), (x0 - 18, cy)], fill=(255, 180, 60), width=10 - i)
    # body (angled up-right)
    draw.polygon([(cx - s, cy - 14), (cx + s - 30, cy - 14),
                  (cx + s, cy), (cx + s - 30, cy + 14),
                  (cx - s, cy + 14)], fill=(220, 225, 230))
    draw.polygon([(cx + s, cy), (cx + s + 26, cy - 8),
                  (cx + s + 26, cy + 8)], fill=(255, 214, 90))
    # fins
    draw.polygon([(cx - s + 8, cy - 14), (cx - s - 22, cy - 44),
                  (cx - s + 26, cy - 14)], fill=(178, 34, 34))
    draw.polygon([(cx - s + 8, cy + 14), (cx - s - 22, cy + 44),
                  (cx - s + 26, cy + 14)], fill=(178, 34, 34))
    # flame
    draw.polygon([(cx - s, cy - 8), (cx - s - 46, cy),
                  (cx - s, cy + 8)], fill=(255, 120, 40))
    # burst star at the nose
    for ang in range(0, 360, 45):
        a = math.radians(ang)
        x1 = cx + s + 40 + int(math.cos(a) * 26)
        y1 = cy - 40 + int(math.sin(a) * 26)
        draw.line([(cx + s + 40, cy - 40), (x1, y1)], fill=(255, 214, 90),
                  width=4)

def draw_chart(draw, x, y, w, h, col=(255, 255, 255), down_col=(255, 90, 70)):
    """Falling market line with axes and arrow."""
    draw.line([(x, y), (x, y + h)], fill=col, width=3)
    draw.line([(x, y + h), (x + w, y + h)], fill=col, width=3)
    pts = [(x + 8, y + 12), (x + w * 0.3, y + h * 0.35),
           (x + w * 0.55, y + h * 0.3), (x + w * 0.8, y + h * 0.72),
           (x + w - 8, y + h - 6)]
    draw.line(pts, fill=down_col, width=6, joint="curve")
    # arrow head at the end
    ex, ey = pts[-1]
    draw.polygon([(ex, ey), (ex - 16, ey - 2), (ex - 2, ey - 16)],
                 fill=down_col)

def draw_zeta(draw, cx, cy, R):
    """The Riemann zeta: big Greek zeta in a ring."""
    draw.ellipse([cx - R, cy - R, cx + R, cy + R], outline=(255, 214, 90),
                 width=5)
    f = F(SERIF_B, int(R * 1.5))
    draw.text((cx, cy - 6), "\u03b6", font=f, fill=(255, 255, 255),
              anchor="mm")
    d2 = draw
    f2 = F(SANS_B, 18)
    d2.text((cx, cy + R + 12), "Re(s) = \u00bd", font=f2,
            fill=(255, 214, 90), anchor="ma")

def draw_shield(draw, cx, cy, s, col=(255, 255, 255)):
    """Defence shield with a check mark."""
    draw.polygon([(cx, cy - s), (cx + s, cy - s * 0.55),
                  (cx + s, cy + s * 0.2), (cx, cy + s),
                  (cx - s, cy + s * 0.2), (cx - s, cy - s * 0.55)],
                 outline=col, width=5)
    draw.line([(cx - s * 0.45, cy - s * 0.05), (cx - s * 0.1, cy + s * 0.35),
               (cx + s * 0.5, cy - s * 0.4)], fill=(120, 220, 120), width=7,
              joint="curve")

def draw_cricket(draw, x, y, s):
    draw.ellipse([x, y, x + s, y + s], fill=(178, 34, 34),
                 outline=(120, 10, 10), width=3)
    draw.arc([x + 8, y + s * 0.28, x + s - 8, y + s * 0.72], 300, 60,
             fill=(255, 255, 255), width=3)
    draw.arc([x + 8, y + s * 0.28, x + s - 8, y + s * 0.72], 120, 240,
             fill=(255, 255, 255), width=3)
    bx = x + s + 14
    for k in range(3):
        draw.rectangle([bx + k * 12, y + 6, bx + k * 12 + 7, y + s - 6],
                       fill=(222, 184, 120))
    draw.rectangle([bx, y, bx + 32, y + 6], fill=(222, 184, 120))

def draw_exchange(draw, x, y, s):
    """Stock-exchange building: pediment, columns, base."""
    draw.polygon([(x, y), (x + s, y), (x + s // 2, y - 22)],
                 fill=(255, 214, 90))
    for k in range(4):
        cx = x + 12 + k * int((s - 24) / 3)
        draw.rectangle([cx - 6, y + 6, cx + 6, y + s - 14], fill=(255, 255, 255))
    draw.rectangle([x, y + s - 12, x + s, y + s], fill=(255, 255, 255))

# ---------------------------------------------------------------- stories
STORIES = [
    # (tag, headline, deck)
    ("POLAND · CONFLICT", "Russian missiles land in Poland",
     "Two Russian missiles and a suspected drone came down in south-east Poland during a huge overnight attack on Ukraine. PM Donald Tusk calls it a deliberate provocation; NATO chief Mark Rutte calls it a grave violation."),
    ("USA · MARKETS", "Wall Street slides into correction",
     "The S&P 500 fell 3.7% on Friday, more than 10% below its October record. The Nasdaq sank 5.3% as AI shares sold off; Nvidia fell 14% on a reported SEC probe."),
    ("SCIENCE · MATHS", "Claude 'proves' maths' greatest riddle",
     "Anthropic mathematician Levent Alp\u00f6ge says he proved the Riemann Hypothesis working with Claude, releasing the proof in Lean. Independent checks are under way; a second, human-only claim appeared the same day."),
    ("TURKIYE · CLIMATE", "COP31 runs into overtime",
     "The UN climate talks in Antalya missed their Friday finish. The draft drops fossil-fuel language and a $120bn adaptation target; a new draft is due this morning."),
    ("SAUDI ARABIA · SECURITY", "Riyadh intercepts three Houthi missiles",
     "The Saudi-led coalition says it destroyed three ballistic missiles fired towards Riyadh on Saturday \u2014 the second attack on the capital in days."),
    ("INDIA · WEATHER", "Akvan crosses Odisha",
     "The cyclone came ashore near Gopalpur with winds of 70\u201380 km/h. Some 370,000 people were evacuated; officials report no major damage."),
    ("SPORT · CRICKET", "Rahul's century steadies India",
     "KL Rahul reached 100 on day three in Wellington, his first Test century in New Zealand, as India reached 239-1 chasing the hosts' 368."),
    ("INDIA · BUSINESS", "NSE becomes 5th-largest exchange",
     "India's National Stock Exchange passed Nasdaq and Hong Kong's HKEX by market value, at about $59.7bn, two months after listing."),
]

SHORT_DECKS = [
    "Two missiles and a drone down in the south-east; Tusk calls it a provocation.",
    "S&P -3.7%, Nasdaq -5.3%; AI shares lead the sell-off.",
    "Anthropic's Alp\u00f6ge claims a proof in Lean; checks under way.",
    "Antalya talks miss their finish; fossil-fuel text dropped.",
    "Coalition destroys three ballistic missiles aimed at Riyadh.",
    "Landfall near Gopalpur; 370,000 evacuated.",
    "Rahul 100 in Wellington; India 239-1, chasing NZ's 368.",
    "NSE passes Nasdaq and HKEX at $59.7bn.",
]

NAVY = (13, 32, 61)
PAPER = (250, 246, 235)
INK = (22, 22, 22)
RED = (178, 34, 34)
TEAL = (10, 90, 110)
GOLD = (255, 214, 90)
FOOTER_SRC = ("Sources: AP  \u00b7  Reuters  \u00b7  Scientific American  \u00b7  "
               "IMD  \u00b7  ANI  \u00b7  IANS")

# ================================================================ VARIANT 1
# Newspaper front page: masthead + lead story + "also today" list.
def variant_v1():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    # masthead band
    d.rectangle([0, 0, W, 148], fill=NAVY)
    d.text((512, 18), "THE WORLD", font=F(SERIF_B, 74),
           fill=(255, 255, 255), anchor="ma")
    d.text((512, 104), "SATURDAY 21 NOVEMBER 2026",
           font=F(SANS_B, 34), fill=GOLD, anchor="ma")
    d.text((40, 152), "ONE DAY  \u00b7  ONE PAGE  \u00b7  THE WORLD'S NEWS",
           font=F(SANS_B, 19), fill=RED)
    rule(d, 40, 182, 984, 3)

    # ---- lead story (left, top)
    lx, ly, lw = 40, 204, 560
    d.text((lx, ly), "POLAND  \u00b7  CONFLICT", font=F(SANS_B, 22), fill=RED)
    y = headline(d, (lx, ly + 34), "Russian missiles land in Poland",
                 F(SERIF_B, 58), INK, lw, leading=62)
    y += 6
    y = para(d, (lx, y), "Two Russian missiles and a suspected drone came "
             "down in south-east Poland during a huge overnight attack on "
             "Ukraine. Prime Minister Donald Tusk calls it a deliberate "
             "provocation; NATO chief Mark Rutte calls it a grave violation "
             "of allied airspace.", F(SANS, 24), INK, lw, leading=31)
    # missile illustration panel
    py = y + 16
    d.rectangle([lx, py, lx + lw, py + 170], fill=(16, 60, 96))
    # stars (left side only, clear of the text block)
    for sx, sy in [(lx + 40, py + 26), (lx + 90, py + 140),
                   (lx + 210, py + 20)]:
        d.ellipse([sx - 3, sy - 3, sx + 3, sy + 3], fill=(255, 255, 255))
    draw_missile(d, lx + 120, py + 88, 44)
    d.text((lx + 240, py + 34), "KH-101 CRUISE MISSILE",
           font=F(SANS_B, 23), fill=(255, 255, 255))
    d.text((lx + 240, py + 68), "NO INJURIES REPORTED",
           font=F(SANS_B, 23), fill=GOLD)
    d.text((lx + 240, py + 102), "RUTTE DUE IN WARSAW TODAY",
           font=F(SANS, 20), fill=(220, 235, 245))
    d.text((lx + 240, py + 132), "POLAND ASKS NATO FOR MORE",
           font=F(SANS, 20), fill=(220, 235, 245))
    lead_bottom = py + 170

    # ---- right column: the day at a glance (stories 2..5)
    rx, rw = 640, 344
    d.text((rx, ly), "THE DAY AT A GLANCE", font=F(SANS_B, 22), fill=NAVY)
    rule(d, rx, ly + 32, 984, 2, fill=NAVY)
    yy = ly + 48
    for i, (tag, head, _deck) in enumerate(STORIES[1:5], start=2):
        deck = SHORT_DECKS[i - 1]
        badge(d, rx + 18, yy + 16, 17, i, NAVY)
        d.text((rx + 46, yy - 2), tag, font=F(SANS_B, 17), fill=RED)
        yy = headline(d, (rx + 46, yy + 20), head, F(SERIF_B, 24),
                      INK, rw - 46, leading=28)
        yy = para(d, (rx + 46, yy + 2), deck, F(SANS, 17), (60, 60, 60),
                  rw - 46, leading=21) + 8
    glance_bottom = yy

    # ---- bottom band: remaining stories (6..8) in three columns
    by = max(lead_bottom, glance_bottom) + 12
    rule(d, 40, by, 984, 3)
    by += 14
    d.text((40, by), "ALSO TODAY", font=F(SANS_B, 21), fill=NAVY)
    by += 36
    col_w = 304
    for k, (tag, head, _deck) in enumerate(STORIES[5:8]):
        deck = SHORT_DECKS[5 + k]
        cx = 40 + k * (col_w + 16)
        badge(d, cx + 18, by + 16, 17, 6 + k, RED)
        d.text((cx + 46, by - 2), tag, font=F(SANS_B, 16), fill=RED)
        yy = headline(d, (cx + 46, by + 20), head, F(SERIF_B, 22),
                      INK, col_w - 46, leading=26)
        para(d, (cx + 46, yy + 2), deck, F(SANS, 17), (60, 60, 60),
             col_w - 46, leading=21)
    # footer
    fy = H - 38
    rule(d, 40, fy - 10, 984, 2)
    d.text((40, fy), FOOTER_SRC, font=F(SANS, 17), fill=(90, 90, 90))
    d.text((984, fy), "21 NOV 2026", font=F(SANS_B, 17), fill=(90, 90, 90),
           anchor="ra")
    img.save(os.path.join(OUT, "variant-v1.png"), optimize=True)
    return img

# ================================================================ VARIANT 2
# Magazine cover: big lead visual + cover lines + story strip.
def variant_v2():
    img = Image.new("RGB", (W, H), (10, 70, 80))
    d = ImageDraw.Draw(img)
    # masthead
    d.text((512, 22), "SATURDAY", font=F(SERIF_B, 84),
           fill=(255, 255, 255), anchor="ma")
    d.rectangle([212, 122, 812, 168], fill=GOLD)
    d.text((512, 130), "21 NOVEMBER 2026", font=F(SANS_B, 30),
           fill=NAVY, anchor="ma")
    d.text((512, 178), "THE WORLD'S NEWS IN ONE IMAGE",
           font=F(SANS_B, 20), fill=(200, 225, 235), anchor="ma")
    # lead visual: night sky, stars, big streaking missile
    for sx, sy in [(80, 250), (180, 330), (300, 240), (700, 260),
                   (860, 330), (940, 240), (420, 360), (620, 380)]:
        d.ellipse([sx - 3, sy - 3, sx + 3, sy + 3], fill=(255, 255, 255))
    draw_missile(d, 400, 420, 150)
    # ground line + alert
    d.rectangle([0, 560, W, 566], fill=(255, 214, 90))
    d.text((512, 576), "MISSILES LAND IN POLAND",
           font=F(SERIF_B, 40), fill=(255, 255, 255), anchor="ma")
    d.text((512, 626), "Tusk calls it a deliberate provocation  \u00b7  "
           "NATO: a grave violation  \u00b7  Rutte due in Warsaw today",
           font=F(SANS, 20), fill=(200, 225, 235), anchor="ma")
    # cover lines
    yy = 676
    d.text((40, yy), "INSIDE TODAY", font=F(SANS_B, 22), fill=GOLD)
    yy += 36
    lines = [
        ("Wall Street slides into correction",
         "S&P -3.7%, Nasdaq -5.3% as AI shares sell off; Nvidia -14%"),
        ("Claude 'proves' maths' greatest riddle",
         "Anthropic's Alp\u00f6ge claims a Riemann proof in Lean; checks under way"),
        ("COP31 runs into overtime",
         "Antalya talks miss their finish; fossil-fuel text dropped"),
        ("Riyadh intercepts three Houthi missiles",
         "Second attack on the Saudi capital in days"),
    ]
    for head, deck in lines:
        d.text((40, yy), "\u25b8  " + head, font=F(SERIF_B, 26),
               fill=(255, 255, 255))
        yy += 32
        d.text((72, yy), deck, font=F(SANS, 19), fill=(200, 225, 235))
        yy += 28
    # also strip
    d.text((40, yy + 2), "ALSO:  Akvan crosses Odisha  \u00b7  "
           "Rahul's century  \u00b7  NSE passes Nasdaq",
           font=F(SANS_B, 20), fill=GOLD)
    # footer
    rule(d, 40, H - 46, 984, 2, fill=(120, 170, 180))
    d.text((40, H - 36), FOOTER_SRC, font=F(SANS, 17),
           fill=(170, 205, 215))
    d.text((984, H - 36), "21 NOV 2026", font=F(SANS_B, 17),
           fill=(170, 205, 215), anchor="ra")
    img.save(os.path.join(OUT, "variant-v2.png"), optimize=True)
    return img

# ================================================================ VARIANT 3
# Editorial ledger: numbered rows for all 8 stories + a numbers strip.
def variant_v3():
    img = Image.new("RGB", (W, H), (255, 255, 255))
    d = ImageDraw.Draw(img)
    # header
    d.rectangle([0, 0, W, 132], fill=NAVY)
    d.text((40, 22), "THE WORLD IN NUMBERS", font=F(SERIF_B, 46),
           fill=(255, 255, 255))
    d.text((40, 82), "SATURDAY 21 NOVEMBER 2026  \u00b7  EIGHT STORIES, ONE DAY",
           font=F(SANS_B, 24), fill=GOLD)
    d.text((984, 30), "No. 21", font=F(SERIF_B, 40), fill=(255, 255, 255),
           anchor="ra")
    # story rows
    yy = 152
    row_h = 84
    for i, (tag, head, _deck) in enumerate(STORIES, start=1):
        deck = SHORT_DECKS[i - 1]
        # number block
        d.rectangle([40, yy, 96, yy + 64], fill=RED if i == 1 else NAVY)
        fnum = F(SERIF_B, 34)
        d.text((68, yy + 30), str(i), font=fnum, fill=(255, 255, 255),
               anchor="mm")
        d.text((116, yy + 2), tag, font=F(SANS_B, 16), fill=RED)
        d.text((116, yy + 22), head, font=F(SERIF_B, 25), fill=INK)
        d.text((116, yy + 52), deck, font=F(SANS, 18), fill=(70, 70, 70))
        yy += row_h
        if i < 8:
            rule(d, 40, yy - 8, 984, 1, fill=(210, 210, 210))
    # numbers strip
    ny = yy + 2
    d.rectangle([0, ny, W, ny + 108], fill=(16, 60, 96))
    d.text((40, ny + 12), "BY THE NUMBERS", font=F(SANS_B, 20), fill=GOLD)
    nums = [
        ("-3.7%", "S&P 500, Friday"),
        ("-5.3%", "Nasdaq, Friday"),
        ("400+", "drones at Ukraine"),
        ("3", "missiles at Riyadh"),
        ("370,000", "evacuated, Odisha"),
        ("$59.7bn", "NSE passes Nasdaq"),
    ]
    cw = (W - 80) // len(nums)
    for k, (big, small) in enumerate(nums):
        cx = 40 + k * cw
        d.text((cx, ny + 40), big, font=F(SERIF_B, 30),
               fill=(255, 255, 255))
        d.text((cx, ny + 76), small, font=F(SANS, 15),
               fill=(200, 225, 235))
    # footer
    fy = H - 34
    d.text((40, fy), FOOTER_SRC, font=F(SANS, 16), fill=(110, 110, 110))
    d.text((984, fy), "21 NOV 2026", font=F(SANS_B, 16),
           fill=(110, 110, 110), anchor="ra")
    img.save(os.path.join(OUT, "variant-v3.png"), optimize=True)
    return img

if __name__ == "__main__":
    for fn in (variant_v1, variant_v2, variant_v3):
        im = fn()
        print(fn.__name__, im.size)
    for name in ("variant-v1.png", "variant-v2.png", "variant-v3.png"):
        p = os.path.join(OUT, name)
        print(name, os.path.getsize(p), "bytes")
