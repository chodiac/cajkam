"""SEO layer: public addresses, URL structure, canonical URLs, structured data,
sitemap / robots / redirects.

Addresses
---------
SITE_URL        where the site is served today (GitHub Pages project site)
CANONICAL_BASE  the final domain
SWITCHED        False while the WordPress shop still runs on cajkam.rs.

URL structure mirrors the current WordPress shop (kupi-gume/<slug>/,
kategorija-proizvoda/<x>/, proizvodjac/<x>/, guma-servis/, 2026/07/27/<post>/ ...),
so moving to cajkam.rs needs almost no redirects.

Canonical rule while SWITCHED is False: a page that already exists on cajkam.rs
(listed in data/live-urls.txt, or any product page) points its canonical at
that cajkam.rs address, so the preview never competes with the live shop.
A page that only exists in the redesign points at itself on SITE_URL.
When SWITCHED is True everything points at CANONICAL_BASE.
"""
import json
import re
from pathlib import Path
from urllib.parse import urljoin

SITE_URL = 'https://chodiac.github.io/cajkam/'
CANONICAL_BASE = 'https://cajkam.rs/'
SWITCHED = False

ROOT = Path(__file__).resolve().parent.parent.parent
_live = ROOT / 'data' / 'live-urls.txt'
LIVE = set(_live.read_text(encoding='utf-8').split()) if _live.exists() else set()

# template file name -> public path (written as <path>index.html)
ROUTES = {
    'index.html': '', 'gume.html': 'kupi-gume/', 'akcije.html': 'akcije/',
    'korpa.html': 'cart/', 'kasa.html': 'checkout/', 'nalog.html': 'my-account/', 'uporedi.html': 'uporedi/',
    'servis.html': 'guma-servis/', 'hotel-za-gume.html': 'hotel-za-gume/', 'brendovi.html': 'brendovi/',
    'blog.html': 'blog/', 'o-nama.html': 'o-nama/', 'kontakt.html': 'kontakt/',
    'cesta-pitanja.html': 'najcesce-postavljana-pitanja/', 'reklamacije.html': 'reklamacije/',
    'uslovi-isporuke.html': 'uslovi-isporuke/', 'zastita-potrosaca.html': 'zastita-potrosaca/',
    'uslovi-koriscenja.html': 'uslovi-koriscenja/', 'politika-privatnosti.html': 'politika-privatnosti/',
}
POST_PATH = {}   # 'blog/<slug>.html' -> 'YYYY/MM/DD/<slug>/', filled by base.py
NOINDEX = {'cart/', 'checkout/', 'my-account/', 'uporedi/', 'guma.html', '404.html'}

# Old addresses on cajkam.rs that change in the redesign (301, written to .htaccess).
REDIRECTS = {
    'akcije-2/': 'akcije/', 'kako-do-nas/': 'kontakt/#kako-do-nas', 'shop/': 'kupi-gume/',
    'search-strana/': 'kupi-gume/', 'wishlist/': 'uporedi/', 'refund_returns-2/': 'reklamacije/',
    'uslovi-koriscenjasssssssssssssssss/': 'uslovi-koriscenja/', 'cart-2/': 'cart/', 'checkout-2/': 'checkout/',
    'my-account-2/': 'my-account/', 'kategorija-proizvoda/uncategorized/': 'kupi-gume/',
}


def out_file(path):
    """Template path -> file written on disk."""
    if path in ROUTES:
        p = ROUTES[path]
        return p + 'index.html'
    if path in POST_PATH:
        return POST_PATH[path] + 'index.html'
    return path


def clean(file_path):
    """File on disk -> public path ('x/index.html' -> 'x/', 'index.html' -> '')."""
    return file_path[:-len('index.html')] if file_path.endswith('index.html') else file_path


def is_live(path):
    if SWITCHED:
        return True
    return path == '' or path in LIVE or bool(re.fullmatch(r'kupi-gume/[^/]+/', path))


def canonical(path):
    return (CANONICAL_BASE if is_live(path) else public_base()) + path


def public_base():
    return CANONICAL_BASE if SWITCHED else SITE_URL


def public(path):
    return public_base() + path


# ----------------------------------------------------------------- link rewriting
_ATTR = re.compile(r'(href|action)="((?:\.\./)*)([^"#?]*)(\?[^"#]*)?(#[^"]*)?"')


def route_links(doc):
    """Rewrite template links (gume.html, guma.html?p=slug, blog/x.html) to public paths."""
    def sub(m):
        attr, up, path, query, frag = m.group(1), m.group(2), m.group(3), m.group(4) or '', m.group(5) or ''
        if path == 'guma.html':
            slug = re.search(r'[?&](?:amp;)?p=([^&]+)', query)
            if slug:
                return f'{attr}="{up}kupi-gume/{slug.group(1)}/{frag}"'
        if path in ROUTES:
            new = up + ROUTES[path]
        elif path in POST_PATH:
            new = up + POST_PATH[path]
        else:
            return m.group(0)
        new = new or './'
        return f'{attr}="{new}{query}{frag}"'
    return _ATTR.sub(sub, doc)


# ----------------------------------------------------------------- structured data
HQ_GEO = (43.888479, 20.382897)        # from the cajkam.rs "kontakt" map embed
SERVICE_GEO = (43.885325, 20.355351)   # from the Guma Servis map embed


def _hours(spec):
    out = []
    for days, h in spec:
        a, b = re.findall(r'\d\d', h)[:2]
        dow = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'] if 'Radnim' in days else ['Saturday']
        out.append({'@type': 'OpeningHoursSpecification', 'dayOfWeek': dow, 'opens': f'{a}:00', 'closes': f'{b}:00'})
    return out


def _address(street, city):
    m = re.match(r'(\d{5})\s+(.+?),', city + ',')
    return {'@type': 'PostalAddress', 'streetAddress': street, 'postalCode': m.group(1) if m else '',
            'addressLocality': 'Čačak', 'addressCountry': 'RS'}


def org_graph(biz):
    """Organization + WebSite: on every page."""
    org = {
        '@type': 'Organization', '@id': CANONICAL_BASE + '#org', 'name': 'Čajka M', 'legalName': biz['name'],
        'url': CANONICAL_BASE, 'logo': public('assets/img/logo.png'), 'foundingDate': '1992',
        'email': 'office@cajkam.rs', 'telephone': biz['phone'],
        'sameAs': [u for _, u, _ in biz['social']],
        'contactPoint': [
            {'@type': 'ContactPoint', 'telephone': biz['phone'], 'contactType': 'customer service', 'areaServed': 'RS', 'availableLanguage': 'sr'},
            {'@type': 'ContactPoint', 'telephone': biz['sales'], 'contactType': 'sales', 'areaServed': 'RS', 'availableLanguage': 'sr'},
        ],
    }
    site = {'@type': 'WebSite', '@id': CANONICAL_BASE + '#site', 'url': CANONICAL_BASE, 'name': 'Čajka M',
            'inLanguage': 'sr-Latn', 'publisher': {'@id': CANONICAL_BASE + '#org'},
            'potentialAction': {'@type': 'SearchAction', 'target': CANONICAL_BASE + 'kupi-gume/?q={search_term_string}',
                                'query-input': 'required name=search_term_string'}}
    return [org, site]


def local_graph(biz):
    """The two locations: the shop (tyre sales) and Guma Servis (fitting, alignment)."""
    shop = {
        '@type': ['TireShop', 'AutoRepair'], '@id': CANONICAL_BASE + '#prodaja', 'name': biz['hq_name'],
        'description': biz['hq_services'],
        'parentOrganization': {'@id': CANONICAL_BASE + '#org'}, 'url': CANONICAL_BASE,
        'image': public('assets/img/og-cajkam.jpg'), 'telephone': biz['phone'], 'email': 'prodaja@cajkam.rs',
        'address': _address(biz['address'], biz['city']),
        'geo': {'@type': 'GeoCoordinates', 'latitude': HQ_GEO[0], 'longitude': HQ_GEO[1]},
        'openingHoursSpecification': _hours(biz['hours']), 'priceRange': 'RSD', 'hasMap': biz['maps_hq'],
    }
    service = {
        '@type': 'AutoRepair', '@id': CANONICAL_BASE + '#guma-servis', 'name': 'Guma Servis - Čajka M',
        'description': biz['service_services'],
        'parentOrganization': {'@id': CANONICAL_BASE + '#org'}, 'url': canonical('guma-servis/'),
        'image': public('assets/img/og-cajkam.jpg'), 'telephone': biz['phone'],
        'address': _address(biz['service_address'], biz['service_city']),
        'geo': {'@type': 'GeoCoordinates', 'latitude': SERVICE_GEO[0], 'longitude': SERVICE_GEO[1]},
        'openingHoursSpecification': _hours(biz['service_hours']), 'priceRange': 'RSD', 'hasMap': biz['maps_service'],
    }
    return [shop, service]


def breadcrumb_graph(doc, page_url):
    nav = re.search(r'<nav class="crumbs"[^>]*>(.*?)</nav>', doc, re.S)
    if not nav:
        return []
    items = []
    for li in re.findall(r'<li[^>]*>(.*?)</li>', nav.group(1), re.S):
        a = re.search(r'href="([^"]+)"[^>]*>(.*?)</a>', li, re.S)
        name = re.sub(r'<[^>]+>', '', a.group(2) if a else li).strip()
        if a:
            absu = urljoin(page_url, a.group(1))
            path = absu[len(public_base()):] if absu.startswith(public_base()) else None
            url = canonical(path) if path is not None else absu
        else:
            url = None
        it = {'@type': 'ListItem', 'position': len(items) + 1, 'name': name}
        if url:
            it['item'] = url
        items.append(it)
    return [{'@type': 'BreadcrumbList', 'itemListElement': items}] if len(items) > 1 else []


def ld_script(graph):
    data = {'@context': 'https://schema.org', '@graph': graph}
    return ('<script type="application/ld+json">' + json.dumps(data, ensure_ascii=False, separators=(',', ':'))
            .replace('</', '<\\/') + '</script>')


# ----------------------------------------------------------------- sitemap etc.
SITEMAP = []   # (path, kind, [image urls]) collected by page()


def write_crawl_files(today):
    """sitemap.xml (index) + parts, robots.txt and .htaccess, all for CANONICAL_BASE:
    they only matter once the site runs on cajkam.rs; the preview cannot use them."""
    from xml.sax.saxutils import escape as x
    parts = {'strane': [], 'proizvodi': [], 'clanci': []}
    for path, kind, images in SITEMAP:
        parts[kind].append((path, images))
    names = []
    for kind, rows in parts.items():
        if not rows:
            continue
        body = []
        for path, images in sorted(rows):
            img = ''.join(f'<image:image><image:loc>{x(i)}</image:loc></image:image>' for i in images[:1])
            body.append(f'<url><loc>{x(CANONICAL_BASE + path)}</loc><lastmod>{today}</lastmod>{img}</url>')
        name = f'sitemap-{kind}.xml'
        (ROOT / name).write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
                                 'xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">\n' + '\n'.join(body) + '\n</urlset>\n', encoding='utf-8')
        names.append(name)
    (ROOT / 'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
                                      ''.join(f'<sitemap><loc>{CANONICAL_BASE}{n}</loc><lastmod>{today}</lastmod></sitemap>\n' for n in names) +
                                      '</sitemapindex>\n', encoding='utf-8')
    (ROOT / 'robots.txt').write_text(
        'User-agent: *\nAllow: /\nDisallow: /cart/\nDisallow: /checkout/\nDisallow: /my-account/\nDisallow: /data/raw/\n'
        f'\nSitemap: {CANONICAL_BASE}sitemap.xml\n', encoding='utf-8')
    # mod_rewrite with NE so the #fragment in a target survives (LiteSpeed reads .htaccess)
    rules = '\n'.join(f'RewriteRule ^{re.escape(old.rstrip("/"))}/?$ /{new} [R=301,L,NE]' for old, new in sorted(REDIRECTS.items()))
    (ROOT / '.htaccess').write_text(
        '# 301s from old cajkam.rs (WordPress) addresses that change in the redesign.\n'
        '# Generated by tools/build.py - edit REDIRECTS in tools/site_lib/seo.py.\n'
        'ErrorDocument 404 /404.html\nRewriteEngine On\n' + rules + '\n', encoding='utf-8')
    return len(SITEMAP)
