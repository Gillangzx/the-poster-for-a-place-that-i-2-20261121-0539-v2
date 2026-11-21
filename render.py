#!/usr/bin/env python3
"""QUARROW VALE — hand-drawn travel poster, rendered with Pillow.

A fog-drowned highland valley at dawn. The ruined Heron Span aqueduct
crosses the valley with a lantern burning in its broken arch; slate roofs,
chimney smoke and two herders sit below it; three ridges fade into mist
behind; a wet slate ledge with ferns, a goat and a rope post anchors the
foreground. Built back-to-front so every layer carries real depth.
"""

import math
import random
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

W = H = 1024
OUT = "entry.png"

GOLD = (247, 200, 106)
PALE_GOLD = (255, 243, 196)
ORANGE = (232, 137, 75)
BRICK = (156, 74, 60)
BRICK_DARK = (110, 52, 44)
SLATE = (74, 90, 107)
SLATE_DARK = (52, 64, 78)
LEDGE = (58, 62, 70)
SUN_GOLD = (255, 200, 92)
MIST = (185, 207, 214)
NEARBLACK = (42, 35, 32)
CREAM = (255, 248, 231)
WALL = (232, 214, 176)
FERN = (64, 92, 58)

rng = random.Random(20261121)


def mix(a, b, t):
    """Blend two colours; t=0 gives a, t=1 gives b. Extra channels of a
    (e.g. alpha) are carried through unchanged."""
    n = min(len(a), len(b))
    out = tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(n))
    return out + a[n:]


def vgrad(w, h, stops):
    """Vertical gradient. stops = [(pos 0..1, rgb), ...], sorted by pos."""
    mode = "RGBA" if len(stops[0][1]) == 4 else "RGB"
    col = Image.new(mode, (1, h))
    px = col.load()
    for y in range(h):
        p = y / max(1, h - 1)
        pick = stops[-1][1]
        for i in range(len(stops) - 1):
            p0, c0 = stops[i]
            p1, c1 = stops[i + 1]
            if p0 <= p <= p1:
                t = 0.0 if p1 == p0 else (p - p0) / (p1 - p0)
                pick = mix(c0, c1, t)
                break
        px[0, y] = pick
    return col.resize((w, h))


def glow(size, center, radius, color, peak):
    """Soft radial glow on a transparent layer."""
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    steps = 26
    for i in range(steps, 0, -1):
        r = radius * i / steps
        a = int(peak * (1 - i / steps) ** 2)
        d.ellipse([center[0] - r, center[1] - r,
                   center[0] + r, center[1] + r], fill=color + (a,))
    return layer


def ridge_points(x0, x1, base, amp, step):
    """Jagged ridge line, smoothed twice so peaks read as hills, not teeth."""
    xs = list(range(x0, x1 + 1, step))
    ys = []
    y = base - rng.uniform(0, amp * 0.4)
    for _ in xs:
        y += rng.uniform(-amp * 0.55, amp * 0.55)
        y = max(base - amp, min(base + amp * 0.25, y))
        ys.append(y)
    for _ in range(1):
        ys = [ys[0]] + [(ys[i - 1] + ys[i] + ys[i + 1]) / 3
                        for i in range(1, len(ys) - 1)] + [ys[-1]]
    pts = [(x, round(v)) for x, v in zip(xs, ys)]
    pts.append((x1, base + 170))
    pts.append((x0, base + 170))
    return pts


def ridge_layer(color, base, amp, blur):
    """One ridge line on its own layer, blurred for distance haze."""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.polygon(ridge_points(-20, W + 20, base, amp, 56), fill=color + (255,))
    return layer.filter(ImageFilter.GaussianBlur(blur))


def arch_wall(d, x0, x1, deck_y, spring_y, crown_y, fill, gap=None):
    """Aqueduct wall between two piers with an arched opening.

    gap (pixels) leaves the crown open — the broken arch — and returns
    the gap's centre x so a lantern can hang there.
    """
    mid = (x0 + x1) / 2.0
    rx = (x1 - x0) / 2.0
    ry = spring_y - crown_y

    def y_at(x):
        q = max(-1.0, min(1.0, (x - mid) / rx))
        return spring_y - ry * math.sqrt(1 - q * q)

    def arc(a0, a1, n=22):
        return [(mid + rx * math.cos(a0 + (a1 - a0) * i / n),
                 spring_y - ry * math.sin(a0 + (a1 - a0) * i / n))
                for i in range(n + 1)]

    if gap is None:
        pts = [(x0, deck_y), (x1, deck_y), (x1, spring_y)]
        pts += arc(0, math.pi)
        pts.append((x0, spring_y))
        d.polygon(pts, fill=fill)
        d.arc([x0, crown_y - ry * 0.12, x1, spring_y + ry * 0.12],
              180, 360, fill=mix(fill, GOLD, 0.35), width=9)
        return None

    gl, gr = mid - gap / 2.0, mid + gap / 2.0
    a_gl = math.acos(max(-1.0, min(1.0, (gl - mid) / rx)))
    a_gr = math.acos(max(-1.0, min(1.0, (gr - mid) / rx)))
    left = [(x0, deck_y), (gl, deck_y), (gl, y_at(gl))]
    left += arc(a_gl, math.pi)
    left.append((x0, spring_y))
    d.polygon(left, fill=fill)
    right = [(gr, deck_y), (x1, deck_y), (x1, spring_y)]
    right += arc(0, a_gr)
    right.append((gr, y_at(gr)))
    d.polygon(right, fill=fill)
    # broken stone teeth at the gap edges
    d.polygon([(gl - 4, y_at(gl) - 6), (gl + 14, y_at(gl) + 2),
               (gl + 6, y_at(gl) + 16), (gl - 10, y_at(gl) + 10)],
              fill=BRICK_DARK)
    d.polygon([(gr + 4, y_at(gr) - 6), (gr - 12, y_at(gr) + 4),
               (gr - 2, y_at(gr) + 18), (gr + 12, y_at(gr) + 8)],
              fill=BRICK_DARK)
    return mid


def house(d, x, y, w, h):
    """Slate-roofed house; y is the base. Returns the chimney top."""
    d.rectangle([x, y - h, x + w, y], fill=WALL)
    d.polygon([(x - 6, y - h), (x + w + 6, y - h),
               (x + w * 0.72, y - h * 1.55), (x + w * 0.28, y - h * 1.55)],
              fill=SLATE_DARK)
    d.rectangle([x + w * 0.2, y - h * 0.62, x + w * 0.38, y - h * 0.3],
                fill=GOLD)
    d.rectangle([x + w * 0.62, y - h * 0.34, x + w * 0.76, y - h * 0.12],
                fill=GOLD)
    d.rectangle([x + w * 0.68, y - h * 1.5, x + w * 0.8, y - h * 1.05],
                fill=BRICK_DARK)
    return (x + w * 0.74, y - h * 1.5)


def smoke(layer, x, y_top, y_bot, drift):
    """Rising chimney smoke: stacked soft puffs, blurred by the caller."""
    d = ImageDraw.Draw(layer)
    n = 9
    for i in range(n):
        t = i / (n - 1)
        y = y_bot + (y_top - y_bot) * t
        xx = x + drift * t * t + rng.uniform(-4, 4)
        r = 7 + 16 * t
        a = int(52 * (1 - t * 0.55))
        d.ellipse([xx - r, y - r * 0.7, xx + r, y + r * 0.7],
                  fill=(240, 238, 230, a))


def herder(d, x, y, s):
    """Small walking figure; y is the feet."""
    d.ellipse([x - 3 * s, y - 15 * s, x + 3 * s, y - 8 * s], fill=NEARBLACK)
    d.polygon([(x - 4 * s, y - 8 * s), (x + 4 * s, y - 8 * s),
               (x + 3 * s, y), (x - 3 * s, y)], fill=NEARBLACK)
    d.line([x - 2 * s, y, x - 4 * s, y - 10 * s], fill=NEARBLACK, width=2)
    d.line([x + 2 * s, y, x + 5 * s, y - 9 * s], fill=NEARBLACK, width=2)
    d.line([x + 6 * s, y - 2 * s, x + 6 * s, y - 18 * s],
           fill=NEARBLACK, width=2)


def goat(d, x, y, s):
    """Goat in side profile, facing right; y is the feet. Body horizontal,
    neck rising at the front, head small, four separated legs."""
    for lx in (-14, -6, 4, 12):
        d.line([x + lx * s, y - 12 * s, x + lx * s, y],
               fill=NEARBLACK, width=max(2, int(2.5 * s)))
    d.ellipse([x - 18 * s, y - 26 * s, x + 14 * s, y - 10 * s], fill=NEARBLACK)
    d.polygon([(x + 8 * s, y - 24 * s), (x + 16 * s, y - 24 * s),
               (x + 20 * s, y - 40 * s), (x + 12 * s, y - 40 * s)],
              fill=NEARBLACK)
    d.ellipse([x + 12 * s, y - 46 * s, x + 26 * s, y - 36 * s], fill=NEARBLACK)
    d.line([x + 14 * s, y - 38 * s, x + 12 * s, y - 33 * s],
           fill=NEARBLACK, width=2)
    d.line([x + 16 * s, y - 45 * s, x + 10 * s, y - 52 * s],
           fill=NEARBLACK, width=2)
    d.line([x + 21 * s, y - 45 * s, x + 21 * s, y - 53 * s],
           fill=NEARBLACK, width=2)
    d.line([x - 18 * s, y - 22 * s, x - 24 * s, y - 27 * s],
           fill=NEARBLACK, width=2)


def frond(d, x, y, length, bend):
    """One fern frond: curved spine with short leaflets."""
    pts = []
    for i in range(13):
        t = i / 12
        pts.append((x + bend * length * t * t + rng.uniform(-1, 1),
                    y - length * t))
    d.line(pts, fill=FERN, width=5)
    for px, py in pts[1:-1:2]:
        d.line([px, py, px - 10, py + 5], fill=FERN, width=3)
        d.line([px, py, px + 10, py + 5], fill=FERN, width=3)


def draw_name(img):
    """QUARROW VALE, giant and letterspaced across the top."""
    d = ImageDraw.Draw(img, "RGBA")
    text = "QUARROW VALE"
    size = 150
    font = ImageFont.truetype(
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf", size)
    track = 16
    width = sum(d.textlength(ch, font=font) for ch in text) + track * (len(text) - 1)
    while width > 920 and size > 40:
        size -= 6
        font = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf", size)
        width = sum(d.textlength(ch, font=font) for ch in text) + track * (len(text) - 1)
    x = (W - width) / 2
    y = 42
    for ox, oy, col in ((4, 5, NEARBLACK + (200,)), (0, 0, CREAM + (255,))):
        cx = x + ox
        for ch in text:
            d.text((cx, y + oy), ch, font=font, fill=col)
            cx += d.textlength(ch, font=font) + track
    d.line([x, y + size + 16, x + width, y + size + 16],
           fill=GOLD + (255,), width=4)


def main():
    # --- sky: bright dawn wash, pale mist top to near-white horizon ---
    img = vgrad(W, H, [(0.0, (216, 226, 224)),
                       (0.32, (242, 221, 166)),
                       (0.48, (255, 246, 218)),
                       (1.0, (255, 246, 218))]).convert("RGBA")
    # low sun glow, camera-left
    img.alpha_composite(glow((W, H), (170, 420), 320, PALE_GOLD, 195))
    # visible dawn sun disc, low on the left, plus soft cloud streaks.
    # Warm gold disc with a soft halo so it reads clearly against the
    # pale sky — the disc itself must not wash out.
    img.alpha_composite(glow((W, H), (170, 350), 175, (255, 198, 95), 165))
    sun = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sun).ellipse([130, 310, 210, 390], fill=SUN_GOLD + (255,))
    img.alpha_composite(sun)
    clouds = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    cd = ImageDraw.Draw(clouds)
    for cx, cy, ln in [(620, 210, 260), (760, 262, 190), (330, 300, 170)]:
        cd.ellipse([cx, cy, cx + ln, cy + 16], fill=(255, 250, 235, 70))
    img.alpha_composite(clouds.filter(ImageFilter.GaussianBlur(6)))

    # --- three ridges, each paler and softer with distance ---
    img.alpha_composite(ridge_layer(mix(SLATE, MIST, 0.55), 470, 120, 7))
    img.alpha_composite(ridge_layer(mix(SLATE, MIST, 0.32), 522, 130, 4))
    img.alpha_composite(ridge_layer(mix(SLATE, MIST, 0.08), 582, 140, 1))

    # --- valley mist band, unifies the distance ---
    mist_band = vgrad(W, H, [(0.36, (185, 207, 214, 0)),
                             (0.48, (185, 207, 214, 30)),
                             (0.62, (185, 207, 214, 0))]).convert("RGBA")
    img.alpha_composite(mist_band)

    # --- the Heron Span, on its own layer so the ledge can reflect it ---
    span = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(span)
    deck_y, spring_y, crown_y = 430, 522, 448
    piers = [130, 380, 640, 880]
    sd.rectangle([100, deck_y - 16, 924, deck_y + 6], fill=BRICK + (255,))
    sd.rectangle([100, deck_y - 16, 924, deck_y - 9],
                 fill=mix(BRICK, GOLD, 0.45) + (255,))
    for px in piers:
        sd.rectangle([px - 24, deck_y, px + 24, 720], fill=BRICK_DARK + (255,))
        sd.rectangle([px - 24, deck_y, px - 14, 720],
                     fill=mix(BRICK_DARK, MIST, 0.28) + (255,))
    bays = [(154, 356), (404, 616), (664, 856)]
    gap_x = None
    for i, (x0, x1) in enumerate(bays):
        if i == 1:
            gap_x = arch_wall(sd, x0, x1, deck_y, spring_y, crown_y,
                              BRICK + (255,), gap=120)
        else:
            arch_wall(sd, x0, x1, deck_y, spring_y, crown_y, BRICK + (255,))
    # lantern hanging in the broken gap
    sd.line([gap_x, crown_y + 4, gap_x, crown_y + 52],
            fill=NEARBLACK + (255,), width=3)
    sd.rounded_rectangle([gap_x - 9, crown_y + 52, gap_x + 9, crown_y + 76],
                         radius=4, fill=NEARBLACK + (255,))
    sd.rectangle([gap_x - 5, crown_y + 58, gap_x + 5, crown_y + 70],
                 fill=(255, 210, 122, 255))
    img.alpha_composite(span)
    img.alpha_composite(glow((W, H), (gap_x, crown_y + 64), 95,
                             (255, 205, 110), 150))

    # --- light shafts raking through the arches, camera-left sun ---
    shafts = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    shd = ImageDraw.Draw(shafts)
    for x0 in (150, 430, 690):
        shd.polygon([(x0, 452), (x0 + 95, 452), (x0 + 300, 790),
                     (x0 + 150, 790)], fill=(255, 196, 90, 88))
    shafts = shafts.filter(ImageFilter.GaussianBlur(9))
    img.alpha_composite(shafts)
    dust = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dd = ImageDraw.Draw(dust)
    for _ in range(46):
        x = rng.uniform(170, 880)
        y = rng.uniform(460, 780)
        r = rng.uniform(1.4, 3.0)
        dd.ellipse([x - r, y - r, x + r, y + r],
                   fill=PALE_GOLD + (rng.randint(115, 180),))
    img.alpha_composite(dust)

    # --- village: winding path, slate roofs, smoke, herders ---
    vd = ImageDraw.Draw(img)
    path_pts = [(40, 806), (220, 792), (430, 800), (640, 786),
                (830, 796), (1000, 784)]
    vd.line(path_pts, fill=mix(WALL, ORANGE, 0.25), width=16)
    vd.line(path_pts, fill=mix(WALL, ORANGE, 0.45), width=7)
    chimneys = []
    for x, y, w, h in [(88, 792, 108, 58), (216, 778, 74, 40),
                       (306, 794, 122, 62), (452, 780, 80, 42),
                       (566, 796, 112, 58), (700, 778, 70, 38),
                       (800, 792, 104, 54), (905, 784, 66, 36)]:
        chimneys.append(house(vd, x, y, w, h))
    smoke_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    for cx, cy in chimneys[:3]:
        smoke(smoke_layer, cx, cy - 95, cy, 20)
    smoke_layer = smoke_layer.filter(ImageFilter.GaussianBlur(4))
    img.alpha_composite(smoke_layer)
    vd = ImageDraw.Draw(img)
    herder(vd, 300, 812, 1.0)
    herder(vd, 352, 818, 0.92)
    # long dawn shadows stretching right from the herders
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    shd2 = ImageDraw.Draw(sh)
    shd2.ellipse([312, 810, 392, 820], fill=NEARBLACK + (52,))
    shd2.ellipse([362, 816, 428, 824], fill=NEARBLACK + (46,))
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(3)))

    # --- foreground: wet slate ledge, darkest and sharpest ---
    ledge = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(ledge)
    top = [(0, 828), (140, 812), (320, 824), (520, 810),
           (700, 822), (880, 812), (W, 826), (W, H), (0, H)]
    ld.polygon(top, fill=LEDGE + (255,))
    ld.line(top[:-2], fill=mix(LEDGE, GOLD, 0.38) + (255,), width=3)
    for _ in range(26):
        x = rng.uniform(30, 990)
        y = rng.uniform(850, 1000)
        ln = rng.uniform(30, 130)
        ld.line([x, y, x + ln, y], fill=mix(LEDGE, MIST, 0.38) + (150,),
                width=3)
    img.alpha_composite(ledge)

    # --- puddle reflection of the Span on the wet slate ---
    # Bigger, brighter, clearly mirroring the arches — no black void.
    refl = ImageOps.flip(span)
    refl_canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    refl_canvas.paste(refl, (0, 360))
    mask = Image.new("L", (W, H), 0)
    md = ImageDraw.Draw(mask)
    md.ellipse([110, 836, 950, 1004], fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(6))
    a = refl_canvas.split()[3]
    a = Image.composite(a, Image.new("L", (W, H), 0),
                        mask.point(lambda v: int(v * 0.72)))
    refl_canvas.putalpha(a)
    img.alpha_composite(refl_canvas.filter(ImageFilter.GaussianBlur(2)))

    # --- ferns, goat, rope post on the ledge ---
    fd = ImageDraw.Draw(img)
    for bx, ln, bend in [(16, 110, 24), (52, 135, 32),
                         (928, 115, -26), (962, 100, -20)]:
        frond(fd, bx, 1024, ln, bend)
    # reed tufts on the ledge top: few, thick, clustered blades
    for gx in (300, 560, 860):
        for k in range(7):
            tip_x = gx + (k - 3) * 7 + rng.uniform(-2, 2)
            tip_y = 794 + abs(k - 3) * 3 + rng.uniform(0, 4)
            fd.line([gx, 824, tip_x, tip_y], fill=FERN, width=4)
    goat(fd, 700, 800, 1.6)
    fd.rectangle([146, 776, 156, 830], fill=(58, 46, 38, 255))
    fd.ellipse([140, 770, 162, 780], fill=(58, 46, 38, 255))
    fd.arc([156, 780, 260, 850], 200, 340, fill=(58, 46, 38, 255), width=3)

    # --- film grain, low opacity, slightly blurred ---
    noise = Image.effect_noise((W, H), 16).convert("L")
    noise = noise.filter(ImageFilter.GaussianBlur(0.6))
    noise_rgb = Image.merge("RGB", (noise, noise, noise))
    img = Image.blend(img.convert("RGB"), noise_rgb, 0.045)

    # --- name last, on top of the sky ---
    draw_name(img)
    img.save(OUT, "PNG")
    print("saved", OUT, img.size)


if __name__ == "__main__":
    main()
