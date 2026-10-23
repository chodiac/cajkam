"""Static site generator for the Čajka M redesign, concept "Trag".

    python tools/build.py

Reads data/*.json (produced by tools/import.py) and writes every page to the
project root, at the same addresses as the current cajkam.rs (kupi-gume/<slug>/,
guma-servis/, 2026/07/27/<post>/ …). All links are relative, so the output works
from a domain root or a sub-path (GitHub Pages). Python only, no Node.

Templates live in tools/site_lib/*.py; the SEO layer (addresses, canonical
URLs, structured data, sitemap) is tools/site_lib/seo.py.
"""
import datetime
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
ROOT = Path(__file__).resolve().parent.parent

# One stylesheet, authored in parts (assets/css/src/NN-*.css). Concatenate
# before site_lib is imported, because it hashes the assets for cache-busting.
_css = ROOT / 'assets' / 'css'
(_css / 'site.css').write_text('\n'.join(p.read_text(encoding='utf-8') for p in sorted((_css / 'src').glob('*.css'))),
                               encoding='utf-8')

from site_lib.base import POSTS, BIZ, CATS, TIRES, IN_STOCK, write_data, favicon, esc  # noqa: E402
from site_lib import seo, pages_home, pages_shop, pages_info, pages_catalog  # noqa: E402

KEEP = {'assets', 'data', 'media', 'tools', '.git', '.claude'}


def clean():
    """Remove everything a previous build wrote, so renamed pages leave nothing behind."""
    for p in ROOT.iterdir():
        if p.name in KEEP or p.name.startswith('.git') or p.name == 'README.md':
            continue
        if p.is_dir():
            shutil.rmtree(p)
        elif p.suffix in ('.html', '.xml', '.txt') or p.name in ('.htaccess', '.nojekyll'):
            p.unlink()


def legacy_stubs():
    """The preview used flat file names (gume.html, blog/<slug>.html). Keep those
    links working on GitHub Pages with tiny forwarding pages (noindex)."""
    olds = {k: v for k, v in seo.ROUTES.items() if k != 'index.html'} | seo.POST_PATH
    for old, new in olds.items():
        up = '../' * old.count('/')
        target = up + new
        (ROOT / old).parent.mkdir(parents=True, exist_ok=True)
        (ROOT / old).write_text(
            f'<!doctype html><html lang="sr-Latn"><head><meta charset="utf-8"><title>Čajka M</title>'
            f'<meta name="robots" content="noindex"><link rel="canonical" href="{esc(seo.canonical(new))}">'
            f'<meta http-equiv="refresh" content="0; url={target}"></head>'
            f'<body><p><a href="{target}">Stranica je premeštena.</a></p>'
            f'<script>location.replace({target!r}+location.search+location.hash)</script></body></html>', encoding='utf-8')
    return len(olds)


def llms():
    cats = '\n'.join(f'- [{t} gume]({seo.canonical(f"kategorija-proizvoda/{c}/")}): {d}' for c, t, d, _ in CATS)
    text = f'''# Čajka M

> Uvoznik i prodavac pneumatika iz Čačka, Srbija, od 1992. Online prodaja guma za putnička, poluteretna, teretna,
> industrijska i poljoprivredna vozila, Guma Servis (montaža,
> balansiranje, reglaža trapa) i hotel za gume. Ovlašćeni uvoznik brendova Speedways i Tourador. SRPS ISO 9001:2015 i 14001:2015.

## Prodavnica
- [Sve gume]({seo.canonical("kupi-gume/")}): katalog sa filterima po dimenziji, sezoni, proizvođaču i ceni
- [Akcije]({seo.canonical("akcije/")}): aktuelne akcije (trenutno nema guma na akciji)
- [Brendovi]({seo.canonical("brendovi/")})
{cats}

## Usluge
- [Guma Servis]({seo.canonical("guma-servis/")}): {BIZ["service_address"]}, Čačak - vulkanizerske usluge za putnička vozila i reglaža trapa; radnim danima 08-18h, subotom 08-16h; cenovnik i zakazivanje
- [Servis u Konjevićima]({seo.canonical("kontakt/")}): {BIZ["address"]}, Čačak - vulkanizerske usluge za putnička i teretna vozila, mehaničarske usluge; radnim danima 08-16h, subotom 08-14h
- [Hotel za gume]({seo.canonical("hotel-za-gume/")}): čuvanje guma, 600 RSD po komadu za jednu sezonu

## Kontakt
- [Kontakt i lokacije]({seo.canonical("kontakt/")}): {BIZ["address"]}, {BIZ["city"]}; tel. {BIZ["phone"]}, prodaja {BIZ["sales"]}, office@cajkam.rs
- [Česta pitanja]({seo.canonical("najcesce-postavljana-pitanja/")}): poručivanje, isporuka (1-3 radna dana), plaćanje pouzećem, garancija
'''
    (ROOT / 'llms.txt').write_text(text, encoding='utf-8')


def og_image():
    """1200×630 share image: the hero still with the white logo."""
    from PIL import Image, ImageDraw
    src = ROOT / 'media' / 'hero-poster.jpg'
    out = ROOT / 'assets' / 'img' / 'og-cajkam.jpg'
    if not src.exists():
        return
    im = Image.open(src).convert('RGB')
    w, h = im.size
    th = round(w * 630 / 1200)
    im = im.crop((0, max(0, (h - th) // 2), w, max(0, (h - th) // 2) + th)).resize((1200, 630), Image.LANCZOS)
    shade = Image.new('L', (1200, 630))
    ImageDraw.Draw(shade).rectangle((0, 0, 1200, 630), fill=0)
    for x in range(1200):
        ImageDraw.Draw(shade).line((x, 0, x, 630), fill=int(170 * max(0, 1 - x / 760)))
    im = Image.composite(Image.new('RGB', im.size, (12, 15, 17)), im, shade)
    logo = Image.open(ROOT / 'assets' / 'img' / 'logo-white.png').convert('RGBA')
    lw = 520
    logo = logo.resize((lw, round(logo.height * lw / logo.width)), Image.LANCZOS)
    im.paste(logo, (64, 630 - 64 - logo.height), logo)
    im.save(out, quality=82, optimize=True, progressive=True)


def main():
    clean()
    write_data()
    favicon()
    og_image()
    out = [pages_home.home(), *pages_shop.all_pages(), *pages_info.all_pages()]
    catalog = pages_catalog.all_pages()
    stubs = legacy_stubs()
    urls = seo.write_crawl_files(datetime.date.today().isoformat())
    llms()
    (ROOT / '.nojekyll').write_text('', encoding='utf-8')
    print(f'built {len(out) + len(POSTS)} pages + {catalog} catalogue pages, {stubs} forwarding stubs; sitemap {urls} urls')


if __name__ == '__main__':
    main()
