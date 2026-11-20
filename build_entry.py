#!/usr/bin/env python3
"""Build entry.png for make.fun news-image-20261120 (zech v2).

World map with story pins + side timeline rail, summarising the world news
of Friday 20 November 2026. Runs locally only; the graded entrypoint is
main.py, which simply copies the finished entry.png to /output/entry.png.

Layout (1024x1024): navy header with the date huge, world-map panel with
numbered pins on the left, chronological timeline rail on the right,
stats strip under the map, footer with the six cities + sources.
"""
import hashlib
import os
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
ASSET = ROOT / "assets" / "worldmap.png"
OUT = ROOT / "entry.png"

W, H = 1024, 1024
NAVY = (16, 35, 63)
NAVY_DARK = (11, 26, 48)
GOLD = (227, 185, 78)
PAPER = (246, 241, 230)
INK = (26, 36, 51)
MUTED = (51, 71, 94)
RAIL_TEXT = (201, 212, 227)
RED = (192, 57, 43)
WHITE = (255, 255, 255)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def font(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


FB = lambda s: font("DejaVuSans-Bold.ttf", s)   # noqa: E731
FR = lambda s: font("DejaVuSans.ttf", s)        # noqa: E731


def text_w(draw, text, fnt):
    return draw.textlength(text, font=fnt)


def wrap(draw, text, fnt, max_w, max_lines=2):
    """Greedy word wrap; returns list of lines (at most max_lines)."""
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines[:max_lines]


# Stories, in chronological (timeline) order. Pin coords are in the
# 1600x1420 cropped world-map space (Antarctica strip removed).
# label: side the map label sits on relative to the pin.
STORIES = [
    dict(num=1, tag="OVERNIGHT", city="RIYADH", pin=(955, 695),
         map_tag="Missile hits PIF Tower", label="right",
         head="Houthi missile hits PIF Tower",
         detail="Riyadh's tallest tower hit; no injuries."),
    dict(num=2, tag="MORNING", city="NEW YORK", pin=(458, 530),
         map_tag="Anthropic +17%", label="left",
         head="Anthropic lists on Nasdaq, +17%",
         detail="First pure-AI firm to list; shares near $97."),
    dict(num=3, tag="MORNING", city="TAIPEI", pin=(1405, 640),
         map_tag="Stocks -6.2%", label="above",
         head="Stocks plunge 6.2% in a day",
         detail="Taiex sheds 2,394 pts; worst week since 1991."),
    dict(num=4, tag="MIDDAY", city="BRUSSELS", pin=(775, 500),
         map_tag="Youth-mobility deal", label="below-left",
         head="UK-EU agree youth-mobility deal",
         detail="Youth-mobility: 100,000 a year, ages 18-31."),
    dict(num=5, tag="AFTERNOON", city="KYIV", pin=(900, 505),
         map_tag="Missiles hit again", label="above",
         head="Missiles strike Kyiv again",
         detail="UK pledges 1,000+ drones, £260m package."),
    dict(num=6, tag="EVENING", city="NAIROBI", pin=(950, 850),
         map_tag="Last Ebola patient home", label="left",
         head="Kenya's last Ebola patient goes home",
         detail="Discharged 37 days after the first case."),
]

MAP_X, MAP_Y, MAP_W, MAP_H = 24, 166, 666, 592
CROP_H = 1420  # worldmap.png cropped to 1600x1420 (Antarctica removed)


def map_point(pin):
    """World-map coords -> canvas coords inside the map panel."""
    return (MAP_X + pin[0] * MAP_W / 1600.0,
            MAP_Y + pin[1] * MAP_H / CROP_H)


def draw_pin(draw, cx, cy, num):
    draw.ellipse([cx - 17, cy - 17, cx + 17, cy + 17], fill=WHITE)
    draw.ellipse([cx - 14, cy - 14, cx + 14, cy + 14], fill=RED)
    label = str(num)
    fnt = FB(20)
    tw = draw.textlength(label, font=fnt)
    th = fnt.getbbox(label)[3]
    draw.text((cx - tw / 2, cy - th / 2 - 1), label, font=fnt, fill=WHITE)


def draw_map_label(draw, story, cx, cy):
    """City + short tag beside/above the pin, with a leader line."""
    city_f, tag_f = FB(20), FR(15)
    city, tag = story["city"], story["map_tag"]
    side = story["label"]
    cw = draw.textlength(city, font=city_f)
    tw = draw.textlength(tag, font=tag_f)
    if side == "left":
        lx = cx - 26 - max(cw, tw)
        ly = cy - 21
        draw.line([(cx - 18, cy), (lx + max(cw, tw) + 4, cy)], fill=NAVY, width=2)
    elif side == "below-left":
        # right-aligned under the pin, clear of neighbouring pins/labels
        lx = cx - 47 - max(cw, tw)
        ly = cy + 36
        draw.line([(cx - 12, cy + 12), (lx + max(cw, tw), ly - 2)],
                  fill=NAVY, width=2)
    elif side == "right":
        lx = cx + 26
        ly = cy - 21
        draw.line([(cx + 18, cy), (lx - 4, cy)], fill=NAVY, width=2)
    else:  # above, centred on the pin
        lx = cx - max(cw, tw) / 2
        ly = cy - 66
        draw.line([(cx, cy - 18), (cx, ly + 44)], fill=NAVY, width=2)
    for txt, fnt, yy in ((city, city_f, ly), (tag, tag_f, ly + 23)):
        draw.text((lx, yy), txt, font=fnt, fill=NAVY,
                  stroke_width=3, stroke_fill=PAPER)


def build():
    base = Image.open(ASSET).convert("RGB")
    world = base.crop((0, 0, 1600, CROP_H)).resize((MAP_W, MAP_H), Image.LANCZOS)
    # Self-check: every pin must sit on land (bright beige), not ocean.
    grey = base.convert("L")
    for s in STORIES:
        x, y = s["pin"]
        v = grey.getpixel((x, y))
        if v < 120:
            print(f"WARNING: pin {s['num']} {s['city']} on dark pixel ({v})",
                  file=sys.stderr)

    canvas = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(canvas)

    # ---- header ----
    draw.rectangle([0, 0, W, 150], fill=NAVY)
    draw.text((36, 20), "FRIDAY  ·  THE WORLD IN ONE DAY",
              font=FB(26), fill=GOLD)
    date = "20 NOVEMBER 2026"
    size = 88
    while text_w(draw, date, FB(size)) > 952 and size > 40:
        size -= 2
    draw.text((34, 52), date, font=FB(size), fill=WHITE)

    # ---- map panel ----
    canvas.paste(world, (MAP_X, MAP_Y))
    draw.rectangle([MAP_X, MAP_Y, MAP_X + MAP_W, MAP_Y + MAP_H],
                   outline=NAVY, width=3)
    for s in STORIES:
        cx, cy = map_point(s["pin"])
        draw_map_label(draw, s, cx, cy)
    for s in STORIES:
        cx, cy = map_point(s["pin"])
        draw_pin(draw, cx, cy, s["num"])

    # ---- stats strip under the map ----
    stats = [
        ("100,000", "youth visas a year,\nUK-EU deal"),
        ("-6.2%", "Taiwan stocks\nin one day"),
        ("+17%", "Anthropic's Nasdaq\ndebut"),
    ]
    sy = 774
    for i, (num, cap) in enumerate(stats):
        cx = 24 + 111 + i * 222
        draw.text((cx - text_w(draw, num, FB(34)) / 2, sy), num,
                  font=FB(34), fill=NAVY)
        for j, line in enumerate(cap.split("\n")):
            draw.text((cx - text_w(draw, line, FR(15)) / 2, sy + 44 + j * 19),
                      line, font=FR(15), fill=MUTED)
    for x in (246, 468):
        draw.line([(x, sy + 6), (x, sy + 76)], fill=(201, 191, 169), width=2)

    # ---- timeline rail ----
    draw.rectangle([706, 166, 1000, 856], fill=NAVY)
    draw.text((722, 174), "THE DAY IN ORDER", font=FB(25), fill=GOLD)
    draw.line([(722, 206), (984, 206)], fill=GOLD, width=2)
    row_y, row_h = 212, 107
    for i, s in enumerate(STORIES):
        y0 = row_y + i * row_h
        # number chip
        ccx, ccy = 739, y0 + 20
        draw.ellipse([ccx - 17, ccy - 17, ccx + 17, ccy + 17], fill=GOLD)
        n = str(s["num"])
        draw.text((ccx - text_w(draw, n, FB(20)) / 2, ccy - 11), n,
                  font=FB(20), fill=NAVY)
        # tag line
        draw.text((766, y0 + 1),
                  f"{s['num']:02d} · {s['tag']} — {s['city']}",
                  font=FB(13), fill=GOLD)
        # headline (max 2 lines)
        lines = wrap(draw, s["head"], FB(19), 218, 2)
        hy = y0 + 18
        for ln in lines:
            draw.text((766, hy), ln, font=FB(19), fill=WHITE)
            hy += 24
        # detail (max 2 lines)
        dlines = wrap(draw, s["detail"], FR(14), 218, 2)
        dy = hy + 2
        for ln in dlines:
            draw.text((766, dy), ln, font=FR(14), fill=RAIL_TEXT)
            dy += 18

    # ---- footer ----
    draw.rectangle([0, 872, W, H], fill=NAVY)
    ticker = "BRUSSELS · NEW YORK · TAIPEI · KYIV · RIYADH · NAIROBI"
    draw.text(((W - text_w(draw, ticker, FB(23))) / 2, 890), ticker,
              font=FB(23), fill=GOLD)
    motto = "SIX STORIES · FIVE CONTINENTS · ONE DAY"
    draw.text(((W - text_w(draw, motto, FB(19))) / 2, 924), motto,
              font=FB(19), fill=WHITE)
    src = ("Stories as reported on Friday 20 November 2026 · Sources: BBC · "
           "Reuters · The Wall Street Journal · Yonhap · OneTurn")
    draw.text(((W - text_w(draw, src, FR(14))) / 2, 956), src,
              font=FR(14), fill=RAIL_TEXT)

    # ---- save: PNG, JPEG fallback if over 1 MiB ----
    canvas.save(OUT, format="PNG", optimize=True)
    if OUT.stat().st_size > 1048576:
        canvas.save(OUT, format="JPEG", quality=88, optimize=True)
        print("saved as JPEG bytes (still named entry.png)")
    data = OUT.read_bytes()
    print(f"entry.png: {len(data)} bytes, {canvas.size}, "
          f"sha256={hashlib.sha256(data).hexdigest()}")


if __name__ == "__main__":
    build()
