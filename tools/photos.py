"""Client photos -> web-ready JPEGs.

    python tools/photos.py

Originals go in assets/img/slike/ (camera files, 6000 px, kept out of git).
Each one listed in PHOTOS is rotated by its EXIF orientation, resized to a
few widths and written as assets/img/foto/<slug>-<width>.jpg. Pages use them
through photo() in tools/site_lib/base.py (srcset + lazy loading).
"""
from pathlib import Path

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / 'assets' / 'img' / 'slike'
OUT = ROOT / 'assets' / 'img' / 'foto'
WIDTHS = (640, 1280)

# source file -> slug used in the templates
PHOTOS = {
    'montaza guma.jpeg': 'montaza-guma',
    'montaza guma 2.jpeg': 'montaza-guma-2',
    'reglaza 2.jpeg': 'reglaza',
    'masina za reglazu.jpeg': 'masina-za-reglazu',
    'montazerka.jpeg': 'montazerka',
    'demonterka.jpeg': 'demonterka',
    'balanserka.jpeg': 'balanserka',
    'balanserka 2.jpeg': 'balanserka-2',
    'DSC_4318.jpeg': 'mehanicari',
    'mehanicarske usluge.jpeg': 'mehanicarske-usluge',
    'perionica 2.jpeg': 'perionica',
    'perionica.jpeg': 'perionica-2',
    'guma servis.jpeg': 'konjevici-zgrada',
    'guma servis 2.jpeg': 'konjevici-ulaz',
    'guma servis dragise misovica.jpg': 'guma-servis-fasada',
}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    done = 0
    for name, slug in PHOTOS.items():
        src = SRC / name
        if not src.exists():
            print('missing', name)
            continue
        im = ImageOps.exif_transpose(Image.open(src)).convert('RGB')
        for w in WIDTHS:
            if w > im.width and w != WIDTHS[0]:
                continue
            k = min(1, w / im.width)
            out = im.resize((round(im.width * k), round(im.height * k)), Image.LANCZOS) if k < 1 else im
            out.save(OUT / f'{slug}-{w}.jpg', quality=78, optimize=True, progressive=True)
        done += 1
    print('photos', done, '->', OUT)


if __name__ == '__main__':
    main()
