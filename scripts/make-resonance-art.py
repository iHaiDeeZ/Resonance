# Resonance's pictures from art/resonance-source.webp (the user's Sonic + Dreamcast picture):
#   sce_sys/icon0.png           512x512 app icon (art/icon.png, the purple swirl)
#   sce_sys/pic1.png            1920x1080 PS4 home screen background
#   launcher-assets/launcher/intro/
#     bg.jpg                    the arena without Sonic, blurred (depth of field)
#     sonic.png                 Sonic holding the Dreamcast (cut out)
#     console.png               the Dreamcast alone (the gloves over it filled in)
#     layout.txt                where each layer sits in the source picture
# The intro (shell/ps4/launcher/intro.cpp) spin-dashes Sonic in as a ball of his own fur and drops
# the Dreamcast into his hands.
# Windows python (Pillow, NumPy, OpenCV):  py scripts/make-resonance-art.py [--preview]
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "art" / "resonance-source.webp"
OUT = ROOT / "launcher-assets" / "launcher" / "intro"
SCALE = 2  # layers are stored at twice the source size (the screen shows them at ~1.9x)

# Outlines in source pixels (1024x559), traced on a grid
SONIC = [(400, 28), (470, 24), (505, 34), (552, 58), (580, 80), (640, 74), (645, 96), (620, 150),
         (613, 200), (604, 240), (594, 268), (587, 272), (717, 302), (729, 332), (731, 360), (727, 400),
         (719, 430), (706, 450), (692, 465), (670, 476), (643, 483), (605, 480), (600, 559), (432, 559),
         (428, 530), (420, 519), (396, 502), (372, 472), (360, 432), (386, 410), (377, 404), (358, 396), (326, 378),
         (300, 340), (285, 300), (266, 248), (290, 200), (296, 160), (300, 120), (326, 70), (360, 45)]
# certainly Sonic: face, quills' middle, body, gloves
SONIC_CORE = [(450, 70), (560, 90), (600, 150), (580, 260), (520, 300), (470, 330), (420, 350),
              (400, 300), (340, 260), (330, 180), (370, 110)]
CONSOLE = [(587, 275), (718, 303), (722, 352), (649, 471), (462, 439), (461, 384)]
# Sonic's gloves (and the VMU) where they cover the console
GLOVES = [
    [(676, 332), (728, 328), (731, 360), (727, 400), (719, 430), (706, 450), (692, 465), (670, 476),
     (657, 472), (670, 420), (674, 380)],
    [(425, 392), (470, 398), (503, 404), (522, 420), (527, 458), (470, 462), (425, 452)],
    [(536, 430), (577, 430), (580, 468), (538, 468)],
]


def poly_mask(shape, pts, value=255):
    m = np.zeros(shape[:2], np.uint8)
    cv2.fillPoly(m, [np.array(pts, np.int32)], value)
    return m


def cut_sonic(img):
    """Alpha of Sonic (with the console), inside his traced outline:
    - the picture draws him with a dark ink line: the arena is flooded from outside the outline
      and stops at that line, what it can't reach is Sonic;
    - his blue fur counts as Sonic (the soft quill tips have no ink line);
    - the arena's cream light doesn't (gloves, eyes and console are neutral white, skin is orange).
    Edges feathered by a pixel."""
    h, w = img.shape[:2]
    region = poly_mask(img.shape, SONIC)
    b, g, r = [c.astype(np.int16) for c in cv2.split(img)]
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    local = cv2.GaussianBlur(gray, (0, 0), 4).astype(np.int16)
    ink = ((gray.astype(np.int16) < local - 18) | (gray < 70)).astype(np.uint8) * 255
    ink = cv2.morphologyEx(ink, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))
    ink[region == 0] = 0
    open_ = np.where(ink == 0, 255, 0).astype(np.uint8)
    n, labels = cv2.connectedComponents(open_, connectivity=4)
    outside = set(np.unique(labels[(region == 0) & (open_ > 0)]))
    reached = np.isin(labels, list(outside)) & (open_ > 0)
    fg = (~reached & (region > 0))
    blue = (b > r + 20) & (b > 80)
    fg |= blue & (region > 0)
    keep = np.zeros((h, w), bool)
    for k in [SONIC_CORE, CONSOLE] + GLOVES:
        keep |= poly_mask(img.shape, k) > 0
    cream = (gray > 185) & (r - b >= 28) & (r - b <= 90) & (r - g < 45)
    fg &= ~(cream & ~keep)
    fg |= keep & (region > 0)
    fg = fg.astype(np.uint8) * 255
    fg = cv2.morphologyEx(fg, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    n, labels, stats, _ = cv2.connectedComponentsWithStats(fg)
    if n > 1:
        biggest = 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA]))
        fg = np.where(labels == biggest, 255, 0).astype(np.uint8)
    # holes inside him that aren't the arena showing through (ears, mouth, shading)
    n, labels, stats, _ = cv2.connectedComponentsWithStats(cv2.bitwise_not(fg), connectivity=4)
    for i in range(1, n):
        part = labels == i
        if part[0, :].any() or part[-1, :].any() or part[:, 0].any() or part[:, -1].any():
            continue
        if stats[i, cv2.CC_STAT_AREA] < 80 or cream[part].mean() < 0.5:
            fg[part] = 255
    fg = cv2.morphologyEx(fg, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))
    return cv2.GaussianBlur(fg, (3, 3), 0)


def upscale(rgba):
    """2x with a light sharpen so the cut-outs hold up at ~1.9x on screen."""
    big = cv2.resize(rgba, None, fx=SCALE, fy=SCALE, interpolation=cv2.INTER_LANCZOS4)
    rgb = big[:, :, :3].astype(np.float32)
    soft = cv2.GaussianBlur(rgb, (0, 0), 1.2)
    big[:, :, :3] = np.clip(rgb * 1.35 - soft * 0.35, 0, 255).astype(np.uint8)
    return big


def save_layer(name, rgb, alpha, layout):
    ys, xs = np.nonzero(alpha > 2)
    x0, y0, x1, y1 = xs.min(), ys.min(), xs.max() + 1, ys.max() + 1
    rgba = np.dstack([rgb, alpha])[y0:y1, x0:x1]
    big = upscale(rgba)
    Image.fromarray(cv2.cvtColor(big, cv2.COLOR_BGRA2RGBA)).save(OUT / name, optimize=True)
    layout.append(f"{name} {x0} {y0} {x1 - x0} {y1 - y0}")
    return rgba


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    pil = Image.open(SRC).convert("RGB")
    img = cv2.cvtColor(np.array(pil), cv2.COLOR_RGB2BGR)
    h, w = img.shape[:2]
    layout = [f"# source {w} {h}; <file> <x> <y> <w> <h> in source pixels (the files are {SCALE}x)"]

    alpha = cut_sonic(img)
    console = poly_mask(img.shape, CONSOLE)
    gloves = np.zeros((h, w), np.uint8)
    for g in GLOVES:
        gloves |= poly_mask(img.shape, g)

    # Sonic holding the Dreamcast, as in the picture
    save_layer("sonic.png", img, alpha, layout)

    # the Dreamcast alone: its outline, the gloves over it painted over with console
    hole = cv2.bitwise_and(console, gloves)
    console_img = cv2.inpaint(img, cv2.dilate(hole, np.ones((5, 5), np.uint8)), 9, cv2.INPAINT_TELEA)
    console_alpha = cv2.GaussianBlur(console, (3, 3), 0)
    save_layer("console.png", console_img, console_alpha, layout)

    # the arena without Sonic, blurred like a shallow depth of field
    gone = cv2.dilate(alpha, np.ones((21, 21), np.uint8))
    small = cv2.resize(img, (w // 2, h // 2), interpolation=cv2.INTER_AREA)
    filled = cv2.inpaint(small, cv2.resize(gone, (w // 2, h // 2)), 25, cv2.INPAINT_TELEA)
    filled = cv2.resize(filled, (w, h), interpolation=cv2.INTER_CUBIC)
    bg = np.where(gone[:, :, None] > 0, filled, img)
    bg = cv2.GaussianBlur(bg, (0, 0), 7)
    # 16:9 at 1920x1080: fit the height, trim the sides
    sh = 1080 / h
    bg = cv2.resize(bg, (round(w * sh), 1080), interpolation=cv2.INTER_CUBIC)
    trim = (bg.shape[1] - 1920) // 2
    bg = bg[:, trim:trim + 1920]
    Image.fromarray(cv2.cvtColor(bg, cv2.COLOR_BGR2RGB)).save(OUT / "bg.jpg", quality=90)
    layout.append(f"bg.jpg {trim / sh:.2f} 0 {1920 / sh:.2f} {h}")
    (OUT / "layout.txt").write_text("\n".join(layout) + "\n", newline="\n")

    # PS4 home screen: the picture itself at 1920x1080, and the icon cropped square around Sonic
    full = pil.resize((round(w * sh), 1080), Image.LANCZOS)
    full.crop((trim, 0, trim + 1920, 1080)).save(ROOT / "sce_sys" / "pic1.png", optimize=True)
    # the app icon is its own picture (art/icon.png: the swirl), not cut from the illustration
    Image.open(ROOT / "art" / "icon.png").convert("RGB").resize((512, 512), Image.LANCZOS).save(
        ROOT / "sce_sys" / "icon0.png", optimize=True)

    if "--preview" in sys.argv:
        prev = ROOT / "art" / "preview"
        prev.mkdir(exist_ok=True)
        for name in ("sonic.png", "console.png"):
            layer = Image.open(OUT / name)
            board = Image.new("RGBA", layer.size, (255, 0, 255, 255))
            board.alpha_composite(layer)
            board.convert("RGB").save(prev / name)
    print("\n".join(layout))


if __name__ == "__main__":
    main()
