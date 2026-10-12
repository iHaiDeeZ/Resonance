#!/usr/bin/env python3
"""Resonance's logo: "RES", the Dreamcast swirl for the O, "NANCE", white Michroma letters in a blue
glow, and "SEGA DREAMCAST EMULATOR FOR PS4" below; transparent background, drawn at twice the size
it is shown at most. Writes launcher-assets/launcher/logo.png (the menus' top-left corner, the opening) and logo.txt
(its margin and the swirl's place), and with
--preview, out/logo-preview.png on a dark background.
Needs Pillow and numpy:  py scripts/make-logo.py [--preview]
"""
import math
import os
import sys

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.join(HERE, "..")
FONT = os.path.join(REPO, "launcher-assets", "launcher", "Michroma-Regular.ttf")
OUT = os.path.join(REPO, "launcher-assets", "launcher", "logo.png")

S = 2                       # supersampling of the drawing
SIZE = 150 * S              # letter size
TRACK = 14 * S              # extra space between letters
SUB_SIZE = 30 * S
SUB_TRACK = 15 * S
PAD = 84 * S                # room for the glow (it fades out before the edge)
WHITE = (255, 255, 255)
GLOW = (40, 140, 255)
ORANGE_IN = (255, 214, 92)
ORANGE_OUT = (255, 112, 10)


def text_width(font, text, track):
    return sum(font.getlength(c) for c in text) + track * (len(text) - 1)


def draw_text(draw, x, y, font, text, track, fill, stroke=0):
    for c in text:
        draw.text((x, y), c, font=font, fill=fill, stroke_width=stroke, stroke_fill=fill)
        x += font.getlength(c) + track
    return x


def swirl(size):
    """The Dreamcast swirl: a spiral from the middle out, a little under two turns, as a mask
    (round dabs along the path, drawn four times larger and scaled down, for clean edges)."""
    k = 4
    big = size * k
    img = Image.new("L", (big, big), 0)
    d = ImageDraw.Draw(img)
    c = big / 2
    width = big * 0.105
    turns = 1.65
    r_out = big / 2 - width / 2 - big * 0.01
    r_in = width * 0.35
    steps = 2400
    for i in range(steps + 1):
        t = i / steps
        a = -math.pi / 2 + t * turns * 2 * math.pi          # clockwise from the top
        r = r_in + (r_out - r_in) * t
        x, y = c + r * math.cos(a), c + r * math.sin(a)
        d.ellipse((x - width / 2, y - width / 2, x + width / 2, y + width / 2), fill=255)
    return img.resize((size, size), Image.LANCZOS)


def gradient(size, inner, outer):
    yy, xx = np.mgrid[0:size, 0:size].astype(np.float32)
    # light from the top left, deep orange toward the bottom right
    t = np.clip(((xx + yy) / (2 * size)) * 1.15, 0, 1)[..., None]
    rgb = (np.array(inner, np.float32) * (1 - t) + np.array(outer, np.float32) * t).astype(np.uint8)
    return Image.fromarray(rgb, "RGB")


def glow(mask, radius, color, strength):
    blur = mask.filter(ImageFilter.GaussianBlur(radius))
    a = np.clip(np.asarray(blur, np.float32) * strength, 0, 255).astype(np.uint8)
    layer = Image.new("RGBA", mask.size, color + (0,))
    layer.putalpha(Image.fromarray(a, "L"))
    return layer


def main():
    font = ImageFont.truetype(FONT, SIZE)
    sub = ImageFont.truetype(FONT, SUB_SIZE)
    left, right = "RES", "NANCE"
    asc, desc = font.getmetrics()
    cap = font.getbbox("E")[3] - font.getbbox("E")[1]
    top_off = font.getbbox("E")[1]
    swirl_size = int(cap * 1.32)
    gap = TRACK * 2.2
    w_main = text_width(font, left, TRACK) + gap + swirl_size + gap + text_width(font, right, TRACK)
    w_sub = text_width(sub, "SEGA DREAMCAST EMULATOR FOR PS4", SUB_TRACK)
    W = int(max(w_main, w_sub) + 2 * PAD)
    sub_gap = int(cap * 0.42)
    sub_cap = sub.getbbox("E")[3] - sub.getbbox("E")[1]
    H = int(PAD * 2 + cap + sub_gap + sub_cap)

    # the letters' mask, then the swirl's
    letters = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(letters)
    x = PAD + (W - 2 * PAD - w_main) / 2
    y = PAD - top_off
    x = draw_text(d, x, y, font, left, TRACK, 255, stroke=int(2.2 * S))
    sx = x - TRACK + gap
    sy = PAD + cap / 2 - swirl_size / 2
    x = sx + swirl_size + gap
    draw_text(d, x, y, font, right, TRACK, 255, stroke=int(2.2 * S))
    subtitle = Image.new("L", (W, H), 0)
    ds = ImageDraw.Draw(subtitle)
    sub_y = PAD + cap + sub_gap - sub.getbbox("E")[1]
    draw_text(ds, PAD + (W - 2 * PAD - w_sub) / 2, sub_y, sub, "SEGA DREAMCAST EMULATOR FOR PS4", SUB_TRACK, 255)
    sw = Image.new("L", (W, H), 0)
    sw.paste(swirl(swirl_size), (int(sx), int(sy)))

    logo = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    # blue light around the letters, orange around the swirl
    text_all = ImageChops.lighter(letters, subtitle)
    logo.alpha_composite(glow(text_all, 26 * S, GLOW, 1.15))
    logo.alpha_composite(glow(letters, 9 * S, (110, 190, 255), 1.0))
    logo.alpha_composite(glow(sw, 14 * S, (255, 120, 20), 0.55))
    white = Image.new("RGBA", (W, H), WHITE + (0,))
    white.putalpha(text_all)
    logo.alpha_composite(white)
    orange = gradient(swirl_size, ORANGE_IN, ORANGE_OUT).convert("RGBA")
    orange_full = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    orange_full.paste(orange, (int(sx), int(sy)))
    orange_full.putalpha(sw)
    logo.alpha_composite(orange_full)

    logo = logo.resize((W // S, H // S), Image.LANCZOS)
    logo.save(OUT, optimize=True)
    # for the app (launcher.cpp): the glow's margin and where the swirl is, as fractions of the height
    # (pad, swirl centre x, swirl centre y, swirl radius)
    with open(os.path.splitext(OUT)[0] + ".txt", "w", newline="\n") as f:
        f.write("%.4f %.4f %.4f %.4f\n" % (PAD / H, (sx + swirl_size / 2) / H, (sy + swirl_size / 2) / H, swirl_size / 2 / H))
    print(f"{OUT}: {logo.size[0]}x{logo.size[1]}")
    if "--preview" in sys.argv:
        bg = Image.new("RGBA", logo.size, (8, 14, 40, 255))
        g = np.linspace(0, 1, logo.size[1])[:, None]
        arr = np.asarray(bg).astype(np.float32)
        arr[..., 2] = 40 + 60 * g
        bg = Image.fromarray(arr.astype(np.uint8), "RGBA")
        bg.alpha_composite(logo)
        os.makedirs(os.path.join(REPO, "out"), exist_ok=True)
        bg.save(os.path.join(REPO, "out", "logo-preview.png"))


if __name__ == "__main__":
    main()
