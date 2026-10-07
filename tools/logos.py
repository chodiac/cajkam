"""Brand logos: download the shop's own logo files once and make web-ready copies.

    python tools/logos.py

The originals on cajkam.rs are 521×459 white canvases with the logo in a thin
band across the middle. For the brand belt they are trimmed to the logo, the
white background becomes transparent, and the result goes to
assets/img/brands/<file>.png as a single-colour silhouette (a logo's own
solid band, e.g. Barum's yellow, is treated as background as well). build.py uses a local copy when one exists and
falls back to the hot-linked original otherwise.
"""
import json
from collections import Counter
import urllib.request
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageChops

ROOT = Path(__file__).resolve().parent.parent
UPLOADS = 'https://cajkam.rs/wp-content/uploads/'
OUT = ROOT / 'assets' / 'img' / 'brands'


INK = (34, 40, 44)


def silhouette(rgb, bgs):
    """Alpha = distance to the nearest background colour; colour = ink."""
    px = rgb.load()
    w, h = rgb.size
    a = Image.new('L', (w, h))
    ap = a.load()
    for y in range(h):
        for x in range(w):
            r, g, b = px[x, y]
            d = min(max(abs(r - c[0]), abs(g - c[1]), abs(b - c[2])) for c in bgs)
            ap[x, y] = 0 if d < 28 else min(255, (d - 28) * 4)
    out = Image.new('RGBA', (w, h), INK + (0,))
    out.putalpha(a)
    return out


def pixels(im):
    return list(im.get_flattened_data() if hasattr(im, 'get_flattened_data') else im.getdata())


def near(c, ref, tol):
    return max(abs(c[0] - ref[0]), abs(c[1] - ref[1]), abs(c[2] - ref[2])) < tol


def band_colour(rgb):
    """Most common colour along the edge of the logo's own box, if it is a solid band."""
    w, h = rgb.size
    edge = [rgb.getpixel((x, y)) for x in range(0, w, 3) for y in (1, h - 2)] +            [rgb.getpixel((x, y)) for y in range(0, h, 3) for x in (1, w - 2)]
    q = Counter((r // 16, g // 16, b // 16) for r, g, b in edge)
    (key, n), = q.most_common(1)
    if n < len(edge) * .6:
        return None
    pick = [c for c in edge if (c[0] // 16, c[1] // 16, c[2] // 16) == key]
    return tuple(sorted(ch)[len(ch) // 2] for ch in zip(*pick))


def clean(im):
    im = im.convert('RGBA')
    rgb = Image.alpha_composite(Image.new('RGBA', im.size, (255, 255, 255, 255)), im).convert('RGB')
    # 1. trim the white canvas down to the logo
    box = ImageChops.invert(rgb.convert('L')).point(lambda v: 255 if v > 18 else 0).getbbox()
    if box:
        rgb = rgb.crop(box)
    # 2. some logos sit on their own solid band (Barum yellow, BOTO grey…):
    #    treat that band as background too, so no logo reads as a box
    band = band_colour(rgb)
    if band and not near(band, (255, 255, 255), 24):
        # crop just inside the band so its anti-aliased edge can't leave an outline
        m = rgb.point(lambda v: v).convert('RGB')
        mask = Image.new('L', m.size)
        mask.putdata([255 if near(c, band, 48) else 0 for c in pixels(m)])
        bb = mask.getbbox()
        if bb:
            rgb = rgb.crop((bb[0] + 3, bb[1] + 3, bb[2] - 3, bb[3] - 3))
        # letters drawn with dark outlines (Annaite): white is a knock-out, so drop it too;
        # white letters on their own (BOTO, Sava): white *is* the logo, keep it as ink
        rest = [c for c in pixels(rgb) if not near(c, band, 48)]
        dark = sum(1 for c in rest if sum(c) < 210)
        bgs = [band, (255, 255, 255)] if rest and dark / len(rest) > .25 else [band]
    else:
        bgs = [(255, 255, 255)]
    out = silhouette(rgb, bgs)
    box = out.getchannel('A').point(lambda v: 255 if v > 40 else 0).getbbox()
    if box:
        out = out.crop((max(0, box[0] - 3), max(0, box[1] - 3), min(out.width, box[2] + 3), min(out.height, box[3] + 3)))
    # shown at most ~170×40 CSS px, so 2x of that is plenty
    k = min(1, 340 / out.width, 80 / out.height)
    if k < 1:
        out = out.resize((round(out.width * k), round(out.height * k)), Image.LANCZOS)
    return out


def main():
    brands = json.loads((ROOT / 'data' / 'brands.json').read_text(encoding='utf-8'))
    OUT.mkdir(parents=True, exist_ok=True)
    done = 0
    for lg in brands['logos']:
        name = Path(lg['logo']).stem + '.png'
        with urllib.request.urlopen(UPLOADS + lg['logo']) as r:
            im = Image.open(BytesIO(r.read()))
        # one ink colour + alpha: a 16-colour palette is visually lossless and tiny
        clean(im).quantize(colors=16, method=Image.Quantize.FASTOCTREE).save(OUT / name, optimize=True)
        done += 1
    print('logos', done, '->', OUT)


if __name__ == '__main__':
    main()
