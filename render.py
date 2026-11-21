#!/usr/bin/env python3
"""Composite the SABLEMERE poster from the realistic base scene.

Loads base.png, scales it to poster width, sets the place name across the top,
then unifies scene and title with a vignette and a whisper of film grain.
Writes entry.png, guaranteed to fit the 1 MiB entry cap.
"""

import os
import random

from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
BASE_PATH = os.path.join(HERE, "base.png")
OUT_PATH = os.path.join(HERE, "entry.png")

TARGET_WIDTH = 1024
BYTE_CAP = 1_048_576
TITLE = "SABLEMERE"
SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
TITLE_SIZE = 104
TRACKING = 20
TITLE_INK = (238, 242, 240)
TITLE_SHADOW = (10, 14, 22)
RULE_GOLD = (201, 162, 75)
VIGNETTE_TINT = (8, 10, 18)


def fit_to_width(img, width):
    ratio = width / img.width
    height = max(1, round(img.height * ratio))
    return img.resize((width, height), Image.LANCZOS)


def draw_spaced_title(canvas, text, font, top):
    """Draw one letter-spaced line, centred, with a soft offset shadow."""
    pen = ImageDraw.Draw(canvas)
    glyphs = [pen.textlength(ch, font=font) for ch in text]
    span = sum(glyphs) + TRACKING * (len(text) - 1)
    left = (canvas.width - span) // 2
    for shift, ink in ((3, TITLE_SHADOW), (0, TITLE_INK)):
        x = left + shift
        y = top + shift
        for ch, gw in zip(text, glyphs):
            pen.text((x, y), ch, font=font, fill=ink)
            x += gw + TRACKING
    return left, left + span


def draw_gold_rule(canvas, left, right, y):
    pen = ImageDraw.Draw(canvas)
    pen.line([(left, y), (right, y)], fill=RULE_GOLD, width=3)
    mid = (left + right) // 2
    pen.ellipse([mid - 4, y - 4, mid + 4, y + 4], fill=RULE_GOLD)


def add_title_band(img, height=180, top_alpha=110):
    """Dark gradient behind the title, fading to nothing, so the name stays
    crisp even where the moon sits behind the middle letters."""
    w, _ = img.size
    ramp = Image.new("L", (1, height))
    ramp.putdata([round(top_alpha * (1 - y / height)) for y in range(height)])
    ramp = ramp.resize((w, height))
    tint = Image.new("RGBA", (w, height), (8, 10, 18, 255))
    img.paste(tint, (0, 0), ramp)
    return img


def soften_edges(img):
    """Darken the corners gently so the eye stays on the road and the moon."""
    w, h = img.size
    mask = Image.new("L", (w, h), 110)
    pen = ImageDraw.Draw(mask)
    pen.ellipse((-int(w * 0.15), -int(h * 0.25),
                 int(w * 1.15), int(h * 1.25)), fill=0)
    mask = mask.filter(ImageFilter.GaussianBlur(120))
    tint = Image.new("RGBA", (w, h), VIGNETTE_TINT + (255,))
    img.paste(tint, (0, 0), mask)
    return img


def add_grain(img, strength=0.05, seed=20261121):
    """Half-resolution noise, blurred and blended in at a low opacity."""
    random.seed(seed)
    w, h = img.size
    noise = Image.effect_noise((w // 2, h // 2), 30)
    noise = noise.resize((w, h), Image.BILINEAR)
    noise = noise.filter(ImageFilter.GaussianBlur(0.6))
    grey = Image.merge("RGB", (noise, noise, noise))
    return Image.blend(img, grey, strength)


def save_under_cap(img, path):
    """Optimised PNG first; palette-quantise (with dithering) only if needed."""
    img.save(path, format="PNG", optimize=True)
    if os.path.getsize(path) <= BYTE_CAP:
        return os.path.getsize(path)
    for colours in (256, 192, 128):
        pal = img.convert("P", palette=Image.ADAPTIVE, colors=colours,
                          dither=Image.FLOYDSTEINBERG)
        pal.save(path, format="PNG", optimize=True)
        if os.path.getsize(path) <= BYTE_CAP:
            return os.path.getsize(path)
    raise SystemExit(f"entry.png still over {BYTE_CAP} bytes after quantising")


def main():
    scene = Image.open(BASE_PATH).convert("RGB")
    poster = fit_to_width(scene, TARGET_WIDTH)
    poster = poster.convert("RGBA")
    poster = add_title_band(poster)

    font = ImageFont.truetype(SERIF, TITLE_SIZE)
    left, right = draw_spaced_title(poster, TITLE, font, top=36)
    draw_gold_rule(poster, left, right, y=36 + TITLE_SIZE + 18)

    poster = soften_edges(poster)
    poster = add_grain(poster.convert("RGB"), strength=0.07)

    size = save_under_cap(poster, OUT_PATH)
    print(f"wrote {OUT_PATH}: {poster.size[0]}x{poster.size[1]}, {size} bytes")


if __name__ == "__main__":
    main()
