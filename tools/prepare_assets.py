"""Build web assets from the source brand JPEG and the extracted deck media.
Run from repo root:  python tools/prepare_assets.py
"""
import os, glob
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_LOGO = os.path.join(ROOT, "source/brand/img_c.jpeg")
CAT = os.path.join(ROOT, "source/extract/cat_media")
PES = os.path.join(ROOT, "source/extract/pes_media")
OUT_BRAND = os.path.join(ROOT, "assets/brand")
OUT_ICON = os.path.join(ROOT, "assets/icons")
OUT_IMG = os.path.join(ROOT, "assets/img")
for d in (OUT_BRAND, OUT_ICON, OUT_IMG):
    os.makedirs(d, exist_ok=True)

NAVY, BLUE, SILVER = (6, 42, 74), (1, 163, 232), (123, 129, 137)   # native logo colours
BRAND_NAVY = (0, 62, 126)   # #003E7E Deep Engineering Blue (site palette)


# ---------------------------------------------------------------- logo
def build_logo():
    im = np.array(Image.open(SRC_LOGO).convert("RGB")).astype(int)
    r, g, b = im[..., 0], im[..., 1], im[..., 2]
    mx, mn = im.max(2), im.min(2)
    sat = mx - mn
    ink = (mn < 215) | (sat > 35)
    alpha = np.clip((255 - mn) * 1.6, 0, 255)
    alpha[~ink] = 0
    alpha[(mn < 150) | (sat > 80)] = 255
    is_blue = (sat > 90) & (b > 150) & (r < 120)
    is_silver = (sat < 45) & (mn > 60) & (mx < 215)
    cls = np.zeros(im.shape[:2], dtype=np.uint8)   # 0 navy, 1 blue, 2 silver
    cls[is_silver] = 2
    cls[is_blue] = 1

    def compose(navy_rgb, blue_rgb, silver_rgb):
        rgb = np.zeros(im.shape, dtype=np.uint8)
        rgb[cls == 0] = navy_rgb
        rgb[cls == 1] = blue_rgb
        rgb[cls == 2] = silver_rgb
        return Image.fromarray(np.dstack([rgb, alpha.astype(np.uint8)]), "RGBA")

    full = compose(NAVY, BLUE, SILVER)
    rev = compose((255, 255, 255), BLUE, (196, 200, 206))
    pad = 24
    x0, y0, x1, y1 = 123 - pad, 294 - pad, 1330 + pad, 816 + pad
    full.crop((x0, y0, x1, y1)).save(os.path.join(OUT_BRAND, "ims-logo.png"), optimize=True)
    rev.crop((x0, y0, x1, y1)).save(os.path.join(OUT_BRAND, "ims-logo-white.png"), optimize=True)
    wy0, wy1 = 294 - pad, 616 + pad
    full.crop((x0, wy0, x1, wy1)).save(os.path.join(OUT_BRAND, "ims-wordmark.png"), optimize=True)
    rev.crop((x0, wy0, x1, wy1)).save(os.path.join(OUT_BRAND, "ims-wordmark-white.png"), optimize=True)
    # chevrons only -> mark / favicon (blue chevron bbox, extended right to the end of the silver one)
    sel = (cls == 1) & (alpha > 0)
    sel[:294, :] = False
    sel[616:, :] = False
    ys, xs = np.where(sel)
    cx0, cy0, cy1 = xs.min(), ys.min(), ys.max()
    mark = full.crop((cx0 - 8, cy0 - 8, 1330 + 8, cy1 + 8))
    mark.save(os.path.join(OUT_BRAND, "ims-mark.png"), optimize=True)
    side = max(mark.size) + 16
    fav = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    fav.paste(mark, ((side - mark.width) // 2, (side - mark.height) // 2), mark)
    fav.resize((64, 64), Image.LANCZOS).save(os.path.join(OUT_BRAND, "favicon-64.png"))
    fav.resize((180, 180), Image.LANCZOS).save(os.path.join(OUT_BRAND, "apple-touch-icon.png"))
    fav.resize((32, 32), Image.LANCZOS).save(os.path.join(OUT_BRAND, "favicon-32.png"))
    print("logo:", (x1 - x0, y1 - y0), "wordmark:", (x1 - x0, wy1 - wy0), "mark:", mark.size)


# ---------------------------------------------------------------- icons
def referenced_icons():
    """Only icons named in content.json are emitted, so no stray artwork (e.g. corporate logos) lands in assets/."""
    import json
    with open(os.path.join(ROOT, "content.json"), encoding="utf-8") as f:
        c = json.load(f)
    keep = set()
    for s in c["services"]:
        keep.add(s["card_icon"])
        for x in s.get("inputs", []) + s.get("deliverables", []):
            keep.add(x["icon"])
    return keep


def recolor_icons():
    n = 0
    keep = referenced_icons()
    for f in sorted(glob.glob(os.path.join(CAT, "*.png")) + glob.glob(os.path.join(PES, "*.png"))):
        if os.path.basename(f)[:-4] not in keep:
            continue
        im = Image.open(f)
        if im.mode != "RGBA":
            continue
        a = np.array(im).astype(int)
        alpha = a[..., 3]
        if (alpha > 0).mean() > 0.6:
            continue
        px = a[alpha > 40][:, :3]
        if len(px) < 50:
            continue
        mx, mn = px.max(1), px.min(1)
        sat = mx - mn
        white = (mn > 200).mean() > 0.9
        red = ((px[:, 0] > 150) & (px[:, 1] < 90) & (px[:, 2] < 90)).mean() > 0.85
        black = (mx < 60).mean() > 0.9
        grey = ((sat < 20).mean() > 0.95) and not white and not black
        if not (white or red or black or grey):
            continue
        # trim to content, then emit a navy and a white variant at web size
        ys, xs = np.where(alpha > 8)
        im = im.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))
        side = max(im.size)
        sq = Image.new("RGBA", (side, side), (0, 0, 0, 0))
        sq.paste(im, ((side - im.width) // 2, (side - im.height) // 2))
        if side > 256:
            sq = sq.resize((256, 256), Image.LANCZOS)
        a2 = np.array(sq).astype(np.uint8)
        h = os.path.basename(f)[:-4]
        for tag, rgb in (("n", BRAND_NAVY), ("w", (255, 255, 255))):
            out = a2.copy()
            out[..., :3] = rgb
            Image.fromarray(out, "RGBA").save(os.path.join(OUT_ICON, f"{h}-{tag}.png"), optimize=True)
        n += 1
    print("icons recoloured:", n)


# ---------------------------------------------------------------- photos
PHOTOS = {  # hash -> (output name, max width)
    "73a0193063": ("hero-robot-arm", 1400), "385d9174a7": ("hero-robot-arms-pair", 1400),
    "4848db2dd1": ("hero-agv", 1400), "9aa177d4f5": ("hero-ergonomics-worker", 1200),
    "002356c983": ("hero-press-robots", 1400), "c7bf02069a": ("hero-body-in-white", 1400),
    "9dcf5e13d3": ("hero-truck", 1200), "76fe86e9be": ("conveyor", 1200),
    "a2bfc847fe": ("bg-sky", 1800), "9190c4fc05": ("bg-meeting", 1800),
    "96170e674e": ("ame-3d-line", 1400), "d13ba804e6": ("tbo-layout-sim", 1600),
    "c3b550c2b5": ("lmf-sim-1", 1000), "59abdb4815": ("lmf-sim-2", 1000),
    "0f348dcbe8": ("lmf-sim-3", 1000), "fadf9b85c2": ("lmf-sim-4", 1000),
    "cded5c9a17": ("ergo-before-1", 900), "59d4748d12": ("ergo-before-2", 900),
    "2da2806128": ("ergo-after-1", 900), "de352c8c03": ("ergo-after-2", 900),
    "753ba247da": ("cip-layout-before", 1200), "5554091d60": ("cip-layout-before-b", 1200),
    "7bbd858956": ("cip-layout-after", 1200), "3779d782fc": ("cip-layout-after-b", 1200),
    "c8ec6e87d1": ("mto-press-3d", 1200), "e3039f1f16": ("mto-olp-screen", 1000),
    "78ed9cbc81": ("mto-transfer-sim", 1000),
    "4e3bce413a": ("ame-cell-3d", 1400), "2da28d9367": ("efmea-1", 700), "21f1695bfc": ("efmea-2", 700),
    "a07485fdb1": ("efmea-3", 700), "80e0066cd7": ("efmea-4", 700), "91724e8da3": ("gdt-detail", 900),
    "f5b5253655": ("gdt-3d", 900),
}


def find(h):
    for d in (CAT, PES):
        m = glob.glob(os.path.join(d, h + ".*"))
        if m:
            return m[0]
    raise FileNotFoundError(h)


def photos():
    for h, (name, maxw) in PHOTOS.items():
        im = Image.open(find(h))
        if h == "78ed9cbc81":   # crop the corporate watermark strip off the bottom-right corner
            im = im.crop((0, 0, im.width, im.height - 52))
        has_alpha = im.mode in ("RGBA", "LA", "P") and np.array(im.convert("RGBA"))[..., 3].min() < 250
        if im.width > maxw:
            im = im.resize((maxw, round(im.height * maxw / im.width)), Image.LANCZOS)
        if has_alpha:
            im.convert("RGBA").save(os.path.join(OUT_IMG, name + ".png"), optimize=True)
        else:
            im.convert("RGB").save(os.path.join(OUT_IMG, name + ".jpg"), quality=86, optimize=True, progressive=True)
    # dashboard hero: hue-shift the red screen to IMS blue
    im = Image.open(find("218686a820")).convert("RGBA")
    hsv = np.array(im.convert("RGB").convert("HSV")).astype(int)
    a = np.array(im)[..., 3]
    hue, s = hsv[..., 0], hsv[..., 1]
    redish = ((hue < 12) | (hue > 240)) & (s > 90)
    hue2 = hue.copy()
    hue2[redish] = 148
    hsv[..., 0] = hue2
    rgb = Image.fromarray(hsv.astype(np.uint8), "HSV").convert("RGB")
    Image.fromarray(np.dstack([np.array(rgb), a]).astype(np.uint8), "RGBA").save(
        os.path.join(OUT_IMG, "hero-dashboard.png"), optimize=True)
    print("photos:", len(PHOTOS) + 1)


if __name__ == "__main__":
    build_logo()
    recolor_icons()
    photos()
