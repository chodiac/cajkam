"""Shared data, helpers and page layout (header, menus, footer)."""
import hashlib
import html
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path

from . import seo

ROOT = Path(__file__).resolve().parent.parent.parent
DATA = ROOT / 'data'
UPLOADS = 'https://cajkam.rs/wp-content/uploads/'

PRODUCTS = json.loads((DATA / 'products.json').read_text(encoding='utf-8'))
POSTS = json.loads((DATA / 'posts.json').read_text(encoding='utf-8'))
PAGES = json.loads((DATA / 'pages.json').read_text(encoding='utf-8'))
BRANDS = json.loads((DATA / 'brands.json').read_text(encoding='utf-8'))
for _p in POSTS:
    seo.POST_PATH[f"blog/{_p['slug']}.html"] = _p['date'].replace('-', '/') + f"/{_p['slug']}/"

esc = html.escape
R = '{R}'  # replaced per page with the relative path to the site root

# --------------------------------------------------------------- business facts
# Every value below is copied from cajkam.rs (kontakt, kako-do-nas, footer,
# guma-servis, o-nama, hotel-za-gume, FAQ). Keep it that way.
BIZ = {
    'name': 'Čajka M d.o.o.',
    'address': 'Bulevar oslobodilaca Čačka 84', 'city': '32103 Čačak, Srbija',
    'hours': [('Radnim danima', '08–16h'), ('Subotom', '08–14h')],
    'phone': '+381 32 5461 011', 'phone_href': '+381325461011',
    'sales': '+381 63 640 655', 'sales_href': '+38163640655',
    'emails': [('office@cajkam.rs', 'Opšte'), ('prodaja@cajkam.rs', 'Prodaja'), ('finansije@cajkam.rs', 'Finansije')],
    'service_address': 'Dr. Dragiše Mišovića 100', 'service_city': '32000 Čačak, Srbija',
    # kontakt says Sat 08-16h, kako-do-nas says Sat 09-16h: flagged in README, kontakt used.
    'service_hours': [('Radnim danima', '08–18h'), ('Subotom', '08–16h')],
    # Two service locations (client, 2026-10-20):
    #  - head office in Konjevići: sales + tyre service for cars and trucks + mechanics
    #  - Guma Servis: tyre service for cars + wheel alignment
    'hq_name': 'Čajka M - prodaja i servis', 'hq_area': 'Konjevići',
    'hq_services': 'Prodaja guma, vulkanizerske usluge za putnička i teretna vozila i mehaničarske usluge.',
    'service_services': 'Vulkanizerske usluge za putnička vozila i reglaža trapa.',
    'b2b': 'https://b2b.cajkam.rs/login',
    'maps_hq': 'https://maps.google.com/maps/dir//%C4%8Cajka+M+D.O.O.+Bulevar+oslobodilaca+84+%C4%8Ca%C4%8Dak+320000/@43.8885993,20.383495,18z/data=!4m5!4m4!1m0!1m2!1m1!1s0x475772459823a2bb:0x2a1cf7abe2db7278',
    'maps_service': 'https://maps.google.com/maps/dir//Guma+servis+Dr.+Dragi%C5%A1e+Mi%C5%A1ovic%CC%81a+96+%C4%8Ca%C4%8Dak+32000/@43.8855441,20.355595,17z/data=!4m5!4m4!1m0!1m2!1m1!1s0x4757730d194668ad:0x4ca53a5e60b1878d',
    'embed_hq': 'https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d987.1368794293229!2d20.382897300117286!3d43.88847917410851!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x475772459823a2bb%3A0x2a1cf7abe2db7278!2s%C4%8Cajka%20M%20D.O.O.!5e0!3m2!1ssr!2srs!4v1696416069135!5m2!1ssr!2srs',
    'embed_service': 'https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d2033.3396417668248!2d20.355350542808466!3d43.88532543866783!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x4757730d194668ad%3A0x4ca53a5e60b1878d!2sGuma%20servis!5e0!3m2!1ssr!2srs!4v1706785800682!5m2!1ssr!2srs',
    'social': [('Facebook', 'https://www.facebook.com/profile.php?id=61566053828408', 'facebook'),
               ('Instagram', 'https://www.instagram.com/gumaservis/', 'instagram'),
               ('LinkedIn', 'https://www.linkedin.com/company/-ajkam-doo/', 'linkedin')],
}

CATS = [
    ('putnicke', 'Putničke', 'Automobili, SUV i 4x4 vozila', 'car'),
    ('poluteretne', 'Poluteretne', 'Kombi i laka dostavna vozila', 'van'),
    ('teretne', 'Teretne', 'Kamioni, autobusi i prikolice', 'truck'),
    ('industrijske', 'Industrijske', 'Viljuškari i radne mašine', 'forklift'),
    ('poljoprivredne', 'Poljoprivredne', 'Traktori i priključne mašine', 'tractor'),
]
SEASONS = [('letnja', 'Letnje'), ('zimska', 'Zimske'), ('sve', 'Sve sezone')]

# "Naša preporuka" on the current homepage, in the shop's own order.
RECOMMENDED = [
    '165-70-r14-westlake-sw608-81t', '285-30r19-pilot-alpin-pa4-98w-xl', '275-45r20-pilot-alpin-5-suv-110v-xl-n0-fp',
    '255-50r19-pilot-alpin-5-suv-107v-xl-fp', '255-35r19-pilot-alpin-pa4-96v-xl', '245-35r20-pilot-alpin-pa4-91v-n1',
    '325-40r22-pilot-alpin-5-suv-114v-mo-fp', '225-50r19-alpin-7-100h-xl', '215-60r17-alpin-7-96h',
    '195-55r16-alpin-7-87h', '175-80r14-polaris-5-88t', '235-55r20-pilot-alpin-5-suv-105v-xl-ne0',
]

# Guma Servis price list, verbatim from cajkam.rs/guma-servis (RSD).
SERVICE_PRICES = [
    ('Demontaža i montaža', [
        ('Putničko vozilo, felna do 16"', 400), ('Putničko vozilo, felna od 17"', 450),
        ('Putničko vozilo, felna od 18"', 500), ('Džip', 500), ('Poluteretni program', 600),
        ('Poljoprivreda, felna 12–16"', 800), ('Guma za viljuškar sa rasklapajućom felnom', 1000),
        ('Prebacivanje točka sa jedne na drugu osovinu', 250)]),
    ('Vulkanizerske usluge', [
        ('Krpljenje tubeles pneumatika za putničko vozilo (čepom)', 500),
        ('Krpljenje tubeles pneumatika za putničko vozilo flekom', 800), ('Krpljenje pneumatika (komplet)', 1000),
        ('Zamena tubeles ventila bez gume', 300), ('Zamena tubeles ventila sa gumom', 400),
        ('Hotel za gume (po komadu)', 600), ('Prelepljivanje', 500)]),
    ('Balansiranje', [
        ('Do 16"', 400), ('Od 17"', 450), ('Od 18"', 500), ('Džip', 500), ('Poluteretni program', 600),
        ('Alu felna do 16", samolepljivi teg', 400), ('Alu felna od 17", samolepljivi teg', 450),
        ('Alu felna od 18", samolepljivi teg', 500), ('Alu felna za džip', 500),
        ('Aluminijumske felne, francuski teg', 1000)]),
    ('Reglaža', [
        ('Pregled mehaničke ispravnosti trapa', 1000), ('Kontrola geometrije i korekcija trapa — putničko vozilo', 2500),
        ('Kontrola geometrije i korekcija trapa — džip', 2800), ('Kontrola geometrije i korekcija trapa — kombi', 3000),
        ('Zamena krajeva spona', 100), ('Zamena jabučica', 1200), ('Rad mehaničara 1h', 2000),
        ('Rad mehaničara ½h', 1000)]),
    ('Brzi servis', [
        ('Zamena ulja i filtera ulja', 'rad mehaničara'), ('Poliranje farova', 2000),
        ('Zamena filtera vazduha', 'rad mehaničara'), ('Zamena polen filtera', 'rad mehaničara'),
        ('Zamena disk kočnica', 'rad mehaničara')]),
]

# Service descriptions, condensed from cajkam.rs/guma-servis.
SERVICES = [
    ('montaza', 'Montaža i balansiranje', 'od 400 RSD',
     'Skidanje stare i postavljanje nove gume na felnu, pa balansiranje tegovima — da volan i vozilo ne podrhtavaju.',
     'Montažna mašina i balanser u radionici Guma Servisa', 'wrench'),
    ('reglaza', 'Reglaža trapa', '2.500 RSD',
     'Podešavanje uglova točkova tako da budu normalni na podlogu i međusobno paralelni. Guma traje duže, vozilo drži pravac. U Guma Servisu, Dr. Dragiše Mišovića 100.',
     'Uređaj za kontrolu geometrije, vozilo na dizalici', 'align'),
    ('vulkanizer', 'Vulkanizerske usluge', 'od 300 RSD',
     'Krpljenje tubeles guma čepom ili flekom, zamena ventila i prelepljivanje. Za putnička vozila u oba servisa, za teretna u Konjevićima.',
     'Krpljenje gume flekom, detalj unutrašnjosti pneumatika', 'patch'),
    ('brzi', 'Brzi servis', 'rad mehaničara',
     'Mehaničarske usluge: zamena ulja i filtera, filtera vazduha i polen filtera, disk kočnica i poliranje farova. U servisu u Konjevićima, Bulevar oslobodilaca Čačka 84.',
     'Mehaničar menja filter ulja', 'oil'),
    ('perionica', 'Samouslužna perionica', 'u servisu',
     'Oprema za samouslužno pranje vozila nemačkog brenda Ehrle, na istoj adresi.',
     'Samouslužna perionica Ehrle ispred servisa', 'drop'),
]

POLICY = [
    ('cesta-pitanja.html', 'Česta pitanja'), ('reklamacije.html', 'Reklamacije'),
    ('uslovi-isporuke.html', 'Uslovi isporuke'), ('zastita-potrosaca.html', 'Zaštita potrošača'),
    ('uslovi-koriscenja.html', 'Uslovi korišćenja'), ('politika-privatnosti.html', 'Politika privatnosti'),
]

NAV = [
    ('gume.html', 'Gume', 'gume'), ('akcije.html', 'Akcije', 'akcije'), ('servis.html', 'Servis', 'servis'),
    ('hotel-za-gume.html', 'Hotel za gume', 'hotel'), ('brendovi.html', 'Brendovi', 'brendovi'),
    ('blog.html', 'Saveti', 'blog'), ('o-nama.html', 'O nama', 'o-nama'), ('kontakt.html', 'Kontakt', 'kontakt'),
]


def numkey(v):
    m = re.match(r'[\d.]+', v)
    return (float(m.group()) if m else 9e9, v)


def fmt(v):
    if isinstance(v, str):
        return v
    whole = int(round(v)) == v
    s = f'{v:,.0f}' if whole else f'{v:,.2f}'
    return s.replace(',', 'X').replace('.', ',').replace('X', '.') + ' RSD'


def n(v):
    return f'{v:,}'.replace(',', '.')


# --------------------------------------------------------------- derived data
TIRES = [p for p in PRODUCTS if p['c'] != 'ostalo']
IN_STOCK = [p for p in TIRES if p['st']]
ON_SALE = [p for p in PRODUCTS if 'r' in p and 0 < p['p'] < p['r'] and not p.get('np')]
CAT_COUNT = Counter(p['c'] for p in TIRES)
CAT_STOCK = Counter(p['c'] for p in IN_STOCK)
SEASON_COUNT = Counter(p['z'] for p in TIRES if p['z'])
SEASON_STOCK = Counter(p['z'] for p in IN_STOCK if p['z'])
BY_SLUG = {p['s']: p for p in PRODUCTS}
MAX_DISCOUNT = max((round((1 - p['p'] / p['r']) * 100) for p in ON_SALE), default=0)
popular = Counter(p['sz'] for p in IN_STOCK if p['c'] == 'putnicke' and p['h'])
POPULAR_SIZES = [s for s, _ in popular.most_common(8)]
BRAND_COUNT = len([b for b, c in BRANDS['counts'] if b and c])


def logo_src(lg, color=False):
    """Trimmed, transparent copy from tools/logos.py when present (ink silhouette, or the
    brand's own colours for hover), else the shop's original."""
    sub = 'color/' if color else ''
    local = ROOT / 'assets' / 'img' / 'brands' / sub / (Path(lg['logo']).stem + '.png')
    return f'{R}assets/img/brands/{sub}{local.name}' if local.exists() else UPLOADS + lg['logo']


def logo_pair(lg, alt=''):
    """Silhouette + colour version stacked; CSS swaps them on hover/focus."""
    return (f'<img class="logo-mono" src="{logo_src(lg)}" alt="{esc(alt)}" loading="lazy" decoding="async">'
            f'<img class="logo-color" src="{logo_src(lg, True)}" alt="" aria-hidden="true" loading="lazy" decoding="async">')


def cat_image(c):
    """A real product photo that plainly shows the category's kind of tyre."""
    pref = {'putnicke': ('Continental', 'Goodyear', 'Michelin'), 'poluteretne': ('Continental', 'Barum'),
            'teretne': ('Continental',), 'industrijske': ('Speedways',), 'poljoprivredne': ('Speedways',)}[c]
    pool = [p for p in TIRES if p['c'] == c and p.get('i') and not p.get('ci') and p['st']]
    for b in pref:
        for p in pool:
            if p['b'] == b and (c != 'putnicke' or p['z'] == 'letnja'):
                return p
    return pool[0] if pool else None


def write_data():
    out = DATA / 'web'
    out.mkdir(parents=True, exist_ok=True)
    (out / 'products.json').write_text(json.dumps(PRODUCTS, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
    rows = defaultdict(lambda: [0, 0])
    for p in TIRES:
        if not p['w'] or not p['d']:
            continue
        k = (p['c'], p['z'], p['w'], p['h'], p['d'])
        rows[k][0] += 1
        rows[k][1] += p['st']
    sizes = [[*k, *v] for k, v in sorted(rows.items())]
    (out / 'sizes.json').write_text(json.dumps({'rows': sizes, 'brands': BRANDS['counts']}, ensure_ascii=False,
                                               separators=(',', ':')), encoding='utf-8')


# --------------------------------------------------------------- icons
SEAGULL = 'M-27 -10 L-4 1 L-14 5 Z M26 -10 L-11 6 L-21 10 L16 10 L7 6 Z'

ICONS = {
    'search': '<circle cx="11" cy="11" r="6.5"/><path d="m20 20-4.2-4.2"/>',
    'cart': '<path d="M3 4h2.2l2.3 11h11l2-8H6.5"/><circle cx="9" cy="19.5" r="1.3"/><circle cx="17" cy="19.5" r="1.3"/>',
    'user': '<circle cx="12" cy="8" r="4"/><path d="M4 21c.8-4 4-6 8-6s7.2 2 8 6"/>',
    'compare': '<path d="M4 8h14M15 4.5 18.5 8 15 11.5M20 16H6M9 12.5 5.5 16 9 19.5"/>',
    'phone': '<path d="M5 3h4l2 5-2.5 1.5a11 11 0 0 0 6 6L16 13l5 2v4a2 2 0 0 1-2 2A17 17 0 0 1 3 5a2 2 0 0 1 2-2"/>',
    'mail': '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3.5 6 8.5 7 8.5-7"/>',
    'pin': '<path d="M12 21s-7-6.2-7-11.5a7 7 0 0 1 14 0C19 14.8 12 21 12 21z"/><circle cx="12" cy="9.5" r="2.5"/>',
    'clock': '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
    'arrow': '<path d="M4 12h15M13 6l6 6-6 6"/>',
    'arrow-left': '<path d="M20 12H5M11 6l-6 6 6 6"/>',
    'arrow-ne': '<path d="M7 17 17 7M8 7h9v9"/>',
    'down': '<path d="m6 9 6 6 6-6"/>',
    'close': '<path d="M6 6l12 12M18 6 6 18"/>',
    'menu': '<path d="M3 8h18M3 16h12"/>',
    'check': '<path d="m5 12.5 4.5 4.5L19 7.5"/>',
    'filter': '<path d="M4 6h16M7 12h10M10 18h4"/>',
    'plus': '<path d="M12 5v14M5 12h14"/>',
    'minus': '<path d="M5 12h14"/>',
    'truck': '<path d="M2 6h11v10H2zM13 10h4.5l3.5 3.5V16h-8"/><circle cx="6" cy="17.5" r="1.8"/><circle cx="17" cy="17.5" r="1.8"/>',
    'shield': '<path d="M12 3 4.5 6v5.5c0 4.6 3.2 8.4 7.5 9.5 4.3-1.1 7.5-4.9 7.5-9.5V6z"/><path d="m8.5 12 2.5 2.5 4.5-5"/>',
    'wrench': '<path d="M14.5 5.5a4.5 4.5 0 0 0 5.6 5.6L12 19.2a2.1 2.1 0 1 1-3-3l8.1-8.1a4.5 4.5 0 0 1-2.6-2.6z"/>',
    'cash': '<rect x="2.5" y="6" width="19" height="12" rx="2"/><circle cx="12" cy="12" r="2.8"/><path d="M6 9.5v5M18 9.5v5"/>',
    'grid': '<rect x="4" y="4" width="7" height="7" rx="1"/><rect x="13" y="4" width="7" height="7" rx="1"/><rect x="4" y="13" width="7" height="7" rx="1"/><rect x="13" y="13" width="7" height="7" rx="1"/>',
    'list': '<path d="M9 6h11M9 12h11M9 18h11"/><circle cx="4.5" cy="6" r="1"/><circle cx="4.5" cy="12" r="1"/><circle cx="4.5" cy="18" r="1"/>',
    'play': '<path d="M8 5.5v13l10.5-6.5z"/>',
    'pause': '<path d="M8 5v14M16 5v14"/>',
    'info': '<circle cx="12" cy="12" r="9"/><path d="M12 11v6M12 7.5v.5"/>',
    'trash': '<path d="M4 7h16M9 7V4.5h6V7M6.5 7l1 13h9l1-13"/>',
    'b2b': '<rect x="3" y="7" width="18" height="13" rx="2"/><path d="M9 7V4.5h6V7M3 13h18"/>',
    'sun': '<circle cx="12" cy="12" r="4"/><path d="M12 2.5v2M12 19.5v2M2.5 12h2M19.5 12h2M5.3 5.3l1.4 1.4M17.3 17.3l1.4 1.4M5.3 18.7l1.4-1.4M17.3 6.7l1.4-1.4"/>',
    'drop': '<path d="M12 3.5s6 6.6 6 11a6 6 0 0 1-12 0c0-4.4 6-11 6-11z"/>',
    'snow': '<path d="M12 2.5v19M3.8 7.2l16.4 9.6M3.8 16.8l16.4-9.6M9.5 4 12 6.5 14.5 4M9.5 20l2.5-2.5 2.5 2.5"/>',
    'align': '<path d="M12 3v18M5 7l3 10M19 7l-3 10"/><circle cx="12" cy="12" r="2"/>',
    'patch': '<rect x="5" y="5" width="14" height="14" rx="4"/><path d="M9 12h6M12 9v6"/>',
    'oil': '<path d="M3 10h9l3-3h4v3l-2 2v6H3z"/><path d="M19 14s2 2.2 2 3.5a2 2 0 0 1-4 0c0-1.3 2-3.5 2-3.5z"/>',
    'hotel': '<rect x="4" y="4" width="16" height="4.5" rx="2.2"/><rect x="4" y="9.8" width="16" height="4.5" rx="2.2"/><rect x="4" y="15.6" width="16" height="4.5" rx="2.2"/>',
    'facebook': '<path d="M14 8h3V4.5h-3a4 4 0 0 0-4 4V11H7v3.5h3V21h3.5v-6.5H17l.5-3.5h-4V8.6c0-.3.2-.6.5-.6z"/>',
    'instagram': '<rect x="4" y="4" width="16" height="16" rx="4.5"/><circle cx="12" cy="12" r="3.8"/><circle cx="17" cy="7" r=".6"/>',
    'linkedin': '<path d="M5 9.5h3V19H5zM6.5 5.2a1.6 1.6 0 1 1 0 3.2 1.6 1.6 0 0 1 0-3.2zM10.5 9.5h2.9v1.4c.5-.9 1.6-1.6 3.1-1.6 3 0 3.5 2 3.5 4.5V19h-3v-4.6c0-1.1 0-2.5-1.6-2.5s-1.9 1.2-1.9 2.4V19h-3z"/>',
}

# Vehicle silhouettes (64×32) so a category never has to be guessed from a tyre photo.
VEHICLES = {
    'car': '<path d="M4 23v-5.5l7-2.5 8-6.5h19l9 6.5 10 2V23"/><path d="M19 15h28M30 9v6"/><circle cx="15" cy="23" r="4"/><circle cx="49" cy="23" r="4"/><path d="M19 23h26"/>',
    'van': '<path d="M4 23V7h36l9 8 10 2.5V23"/><path d="M40 7v9h9M22 7v16"/><circle cx="14" cy="23" r="4"/><circle cx="50" cy="23" r="4"/><path d="M18 23h28"/>',
    'truck': '<path d="M2 21V5h34v16M36 10h13l6 7v4"/><circle cx="11" cy="23" r="3.6"/><circle cx="20" cy="23" r="3.6"/><circle cx="48" cy="23" r="3.6"/><path d="M24 23h20M2 21h5M36 21h8"/>',
    'forklift': '<path d="M50 3v22M50 25h12M44 5h6"/><path d="M12 22V11h14l6 5h12v6"/><path d="M26 11V4h-9v7"/><circle cx="17" cy="23" r="4"/><circle cx="38" cy="24" r="3"/><path d="M21 23h14"/>',
    'tractor': '<circle cx="18" cy="20" r="9"/><circle cx="18" cy="20" r="3"/><circle cx="51" cy="24" r="5"/><path d="M27 20h19M10 11V4h14l3 9h20l5 6"/><path d="M24 4v9"/>',
}


def icon(name, cls='i'):
    # {R} is resolved per page in page(); one shared sprite file keeps every page small
    return f'<svg class="{cls}" aria-hidden="true"><use href="{R}assets/img/icons.svg#i-{name}"/></svg>'


def vehicle(name, cls='veh'):
    return (f'<svg class="{cls}" viewBox="0 0 64 30" aria-hidden="true" fill="none" stroke="currentColor" '
            f'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">{VEHICLES[name]}</svg>')


def write_sprite():
    """All icons as <symbol>s in one file; pages reference assets/img/icons.svg#i-<name>."""
    svg = ('<svg xmlns="http://www.w3.org/2000/svg">' + ''.join(
        f'<symbol id="i-{k}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" '
        f'stroke-linecap="round" stroke-linejoin="round">{v}</symbol>' for k, v in ICONS.items()) + '</svg>')
    (ROOT / 'assets' / 'img' / 'icons.svg').write_text(svg, encoding='utf-8')


# --------------------------------------------------------------- tread patterns
# Front-on tread tiles (one vertical repeat each). The signature section and
# the category cards roll these with background-position, so they must tile.
TREADS = {
    # summer: four straight circumferential grooves, calm wide shoulder blocks
    'letnja': ('0 0 240 120', '<rect width="240" height="120" fill="#1b1f22"/>'
               '<g fill="#2c3237"><rect x="10" y="4" width="38" height="52" rx="5"/><rect x="10" y="64" width="38" height="52" rx="5"/>'
               '<rect x="192" y="4" width="38" height="52" rx="5"/><rect x="192" y="64" width="38" height="52" rx="5"/>'
               '<rect x="58" y="0" width="30" height="120"/><rect x="152" y="0" width="30" height="120"/>'
               '<rect x="98" y="0" width="44" height="120"/></g>'
               '<g stroke="#15181b" stroke-width="3"><path d="M58 30l30 8M58 90l30 8M152 38l30-8M152 98l30-8"/></g>'
               '<g fill="#3a4147" opacity=".55"><rect x="12" y="6" width="6" height="48" rx="3"/><rect x="12" y="66" width="6" height="48" rx="3"/><rect x="100" y="0" width="5" height="120"/></g>'),
    # all-season: directional V blocks
    'sve': ('0 0 240 120', '<rect width="240" height="120" fill="#1b1f22"/>'
            '<g fill="#2c3237">'
            '<path d="M8 10 L52 32 L52 58 L8 36Z"/><path d="M8 70 L52 92 L52 118 L8 96Z"/>'
            '<path d="M232 10 L188 32 L188 58 L232 36Z"/><path d="M232 70 L188 92 L188 118 L232 96Z"/>'
            '<path d="M60 26 L114 52 L114 76 L60 50Z"/><path d="M60 -34 L114 -8 L114 16 L60 -10Z"/><path d="M60 86 L114 112 L114 136 L60 110Z"/>'
            '<path d="M180 26 L126 52 L126 76 L180 50Z"/><path d="M180 -34 L126 -8 L126 16 L180 -10Z"/><path d="M180 86 L126 112 L126 136 L180 110Z"/>'
            '</g><g stroke="#15181b" stroke-width="2.5"><path d="M20 22l20 10M20 82l20 10M220 22l-20 10M220 82l-20 10M74 44l26 13M166 44l-26 13"/></g>'),
    # winter: dense blocks, every block cut by zig-zag sipes
    'zimska': ('0 0 240 120', '<rect width="240" height="120" fill="#1b1f22"/>'
               '<g fill="#2c3237">' + ''.join(
                   f'<rect x="{x}" y="{y}" width="{w}" height="26" rx="3"/>'
                   for x, w in ((6, 40), (52, 38), (96, 48), (150, 38), (194, 40))
                   for y in ((4, 34, 64, 94) if x in (6, 96, 194) else (-11, 19, 49, 79, 109))) +
               '</g><g fill="none" stroke="#15181b" stroke-width="2">' + ''.join(
                   f'<path d="M{x + 4} {y + 13} l5 -4 5 4 5 -4 5 4 5 -4 5 4"/>'
                   for x in (6, 52, 96, 150, 194) for y in ((4, 34, 64, 94) if x in (6, 96, 194) else (-11, 19, 49, 79, 109))) +
               '</g>'),
}


def tread_svg(season):
    vb, body = TREADS[season]
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}" preserveAspectRatio="none">{body}</svg>'


def write_treads():
    d = ROOT / 'assets' / 'img'
    d.mkdir(parents=True, exist_ok=True)
    for s in TREADS:
        (d / f'tread-{s}.svg').write_text(tread_svg(s), encoding='utf-8')


# --------------------------------------------------------------- layout
def asset_version():
    h = hashlib.sha1()
    for f in sorted((ROOT / 'assets').rglob('*')):
        if f.is_file() and f.suffix in ('.css', '.js'):
            h.update(f.read_bytes())
    return h.hexdigest()[:8]


VER = asset_version()


def size_query(sz):
    m = re.match(r'([\d.]+)/([\d.]+) R([\d.]+C?)', sz)
    return f'sirina={m[1]}&amp;visina={m[2]}&amp;precnik={m[3]}' if m else f'q={sz}'


def cat_img_url(c, full=True):
    p = cat_image(c)
    return img_url(p, full) if p else ''


def header(Rp, active):
    cats = ''.join(
        f'<a class="mega__cat" href="{Rp}gume.html?tip={c}" style="--i:{i}"><span class="mega__img"><img src="{cat_img_url(c, False)}" alt="" loading="lazy" decoding="async"></span>'
        f'<span class="mega__txt">{vehicle(v)}<b>{t}</b><small>{d}</small></span></a>'
        for i, (c, t, d, v) in enumerate(CATS))
    seasons = ''.join(
        f'<a class="mega__season" data-s="{s}" href="{Rp}gume.html?sezona={s}">{icon({"letnja": "sun", "zimska": "snow", "sve": "drop"}[s])}{t}'
        f'</a>' for s, t in SEASONS)
    sizes = ''.join(f'<a class="size-chip" href="{Rp}gume.html?{size_query(s)}">{s}</a>' for s in POPULAR_SIZES[:6])
    nav = []
    for href, label, key in NAV:
        cur = ' aria-current="page"' if key == active else ''
        if key == 'gume':
            nav.append(f'<li class="has-mega"><a href="{Rp}{href}"{cur} class="nav__link">{label}</a>'
                       f'<button class="mega-toggle" aria-expanded="false" aria-controls="mega" aria-label="Kategorije guma">'
                       f'{icon("down")}</button></li>')
        else:
            nav.append(f'<li><a href="{Rp}{href}"{cur} class="nav__link">{label}</a></li>')
    return f'''
<a class="skip" href="#main">Preskoči na sadržaj</a>
<div class="topbar"><div class="wrap topbar__in">
 <p class="topbar__claim"><span>{icon('truck')}Dostava 1–3 radna dana</span><span class="hide-sm">{icon('shield')}Garancija 24 meseca</span><span class="hide-md">{icon('cash')}Plaćanje pouzećem</span></p>
 <ul class="topbar__links">
  <li><a href="tel:{BIZ['phone_href']}">{icon('phone')}{BIZ['phone']}</a></li>
  <li class="hide-sm"><a href="{Rp}kontakt.html#kako-do-nas">{icon('pin')}Kako do nas</a></li>
  <li><a class="topbar__b2b" href="{BIZ['b2b']}" rel="noopener">B2B portal{icon('arrow-ne')}</a></li>
 </ul>
</div></div>
<header class="hdr" data-hdr>
 <div class="wrap hdr__in">
  <button class="hdr__burger" data-menu-open aria-label="Otvori meni" aria-controls="drawer" aria-expanded="false"><span></span><span></span></button>
  <a class="logo" href="{Rp}index.html" aria-label="Čajka M — početna"><img src="{Rp}assets/img/logo.png" alt="Čajka M" width="180" height="20"></a>
  <nav class="nav" aria-label="Glavni meni"><ul class="nav__list">{''.join(nav)}</ul></nav>
  <div class="hdr__tools">
   <form class="search" action="{Rp}gume.html" role="search" data-search>
    <label class="sr" for="q">Pretraga guma</label>
    {icon('search', 'i search__i')}
    <input id="q" name="q" type="search" autocomplete="off" placeholder="205/55 R16, brend ili model" aria-autocomplete="list" aria-controls="suggest" aria-expanded="false">
    <kbd class="search__kbd" aria-hidden="true">/</kbd>
    <div class="suggest" id="suggest" role="listbox" hidden></div>
   </form>
   <a class="tool" href="{Rp}uporedi.html" aria-label="Uporedi gume">{icon('compare')}<b class="badge" data-compare-count hidden>0</b></a>
   <a class="tool hide-sm" href="{Rp}nalog.html" aria-label="Moj nalog">{icon('user')}</a>
   <a class="tool tool--cart" href="{Rp}korpa.html" data-cart-open aria-label="Korpa">{icon('cart')}<span class="tool__l" data-cart-total>Korpa</span><b class="badge" data-cart-count hidden>0</b></a>
  </div>
 </div>
 <div class="mega" id="mega" hidden><div class="wrap mega__in">
  <div class="mega__cats">{cats}</div>
  <div class="mega__side">
   <p class="label">Po sezoni</p><div class="mega__seasons">{seasons}</div>
   <p class="label">Najtraženije dimenzije</p><div class="mega__sizes">{sizes}</div>
   <a class="btn btn--ink" href="{Rp}gume.html"><span>Sve gume</span>{icon('arrow')}</a>
  </div>
 </div></div>
</header>
<div class="roadrail" aria-hidden="true"><div class="roadrail__line"></div><div class="roadrail__tyre" data-rail-tyre></div></div>'''


def drawer(Rp):
    links = ''.join(f'<li style="--i:{i}"><a href="{Rp}{h}">{l}</a></li>' for i, (h, l, _) in enumerate(NAV))
    cats = ''.join(f'<li><a href="{Rp}gume.html?tip={c}">{vehicle(v)}<span>{t}</span></a></li>'
                   for c, t, _, v in CATS)
    return f'''
<div class="drawer" id="drawer" hidden data-drawer>
 <div class="drawer__panel" role="dialog" aria-modal="true" aria-label="Meni">
  <div class="drawer__head"><img src="{Rp}assets/img/logo-white.png" alt="Čajka M" width="150" height="17"><button class="icon-btn icon-btn--light" data-menu-close aria-label="Zatvori meni">{icon('close')}</button></div>
  <form class="drawer__search" action="{Rp}gume.html" role="search"><label class="sr" for="dq">Pretraga</label>{icon('search')}<input id="dq" name="q" type="search" placeholder="Dimenzija, brend ili model"></form>
  <ul class="drawer__links">{links}</ul>
  <p class="label label--light">Kategorije</p><ul class="drawer__cats">{cats}</ul>
  <div class="drawer__contact">
   <a href="tel:{BIZ['phone_href']}">{icon('phone')}{BIZ['phone']}<small>centrala</small></a>
   <a href="tel:{BIZ['sales_href']}">{icon('phone')}{BIZ['sales']}<small>prodaja</small></a>
   <a href="{Rp}nalog.html">{icon('user')}Moj nalog</a>
   <a href="{BIZ['b2b']}" rel="noopener">{icon('b2b')}B2B portal za partnere</a>
  </div>
 </div>
</div>
<div class="cartdrawer" id="cartdrawer" hidden data-cartdrawer>
 <aside class="cartdrawer__panel" role="dialog" aria-modal="true" aria-labelledby="cd-title">
  <div class="cartdrawer__head"><h2 id="cd-title">Korpa</h2><button class="icon-btn" data-cart-close aria-label="Zatvori korpu">{icon('close')}</button></div>
  <div class="cartdrawer__body" data-cart-lines></div>
  <div class="cartdrawer__foot">
   <div class="sumrow"><span>Ukupno sa PDV-om</span><b data-cart-sum>0 RSD</b></div>
   <p class="fine">Cena ne uključuje montažu. Dostavu obračunavamo pri poručivanju.</p>
   <a class="btn btn--go btn--block" href="{Rp}kasa.html"><span>Nastavi na poručivanje</span>{icon('arrow')}</a>
   <a class="btn btn--line btn--block" href="{Rp}korpa.html"><span>Pregled korpe</span></a>
  </div>
 </aside>
</div>
<div class="toast" role="status" aria-live="polite" data-toast hidden></div>'''


def footer(Rp):
    pol = ''.join(f'<li><a href="{Rp}{h}">{l}</a></li>' for h, l in POLICY)
    sitemap = ''.join(f'<li><a href="{Rp}{h}">{l}</a></li>' for h, l, _ in NAV)
    social = ''.join(f'<a href="{u}" rel="noopener" aria-label="{l}">{icon(i)}</a>' for l, u, i in BIZ['social'])
    hours = ''.join(f'<li><span>{d}</span><b>{h}</b></li>' for d, h in BIZ['hours'])
    return f'''
<footer class="ftr">
 <div class="wrap">
  <section class="ftr__news" aria-labelledby="nl-title">
   <div><p class="label label--light">Newsletter</p><h2 id="nl-title" class="d3">5 % popusta na prvu kupovinu</h2>
   <p>Prijavite se i prvi saznajte za nove akcije, ponude i savete o održavanju guma.</p></div>
   <form class="ftr__form" data-demo-form data-success="Hvala! Prijava je zabeležena.">
    <label class="sr" for="nl-email">E-mail adresa</label>
    <input id="nl-email" type="email" required placeholder="vasa@adresa.rs" autocomplete="email">
    <button class="btn btn--go" type="submit"><span>Prijavi me</span>{icon('arrow')}</button>
    <p class="fine">Prijavom prihvatate <a href="{Rp}uslovi-koriscenja.html">Uslove korišćenja</a> i <a href="{Rp}politika-privatnosti.html">Politiku privatnosti</a>.</p>
   </form>
  </section>
  <div class="ftr__grid">
   <div class="ftr__brand">
    <img src="{Rp}assets/img/logo-white.png" alt="Čajka M" width="200" height="22" loading="lazy">
    <p>Uvoz i prodaja pneumatika na domaćem tržištu i u regionu — od 1992. godine.</p>
    <p class="ftr__iso">SRPS ISO 9001:2015<br>SRPS ISO 14001:2015</p>
    <div class="ftr__social">{social}</div>
   </div>
   <div><h3>Kontakt</h3>
    <ul class="ftr__list">
     <li>{BIZ['address']}<br>{BIZ['city']}</li>
     <li><a href="tel:{BIZ['phone_href']}">{BIZ['phone']}</a> <small>centrala</small></li>
     <li><a href="tel:{BIZ['sales_href']}">{BIZ['sales']}</a> <small>prodaja</small></li>
     <li><a href="mailto:office@cajkam.rs">office@cajkam.rs</a></li>
    </ul>
    <h3>Radno vreme</h3><ul class="ftr__hours">{hours}</ul>
   </div>
   <div><h3>Gume</h3><ul class="ftr__list">{''.join(f'<li><a href="{Rp}kategorija-proizvoda/{c}/">{t} gume</a></li>' for c, t, _, _ in CATS)}</ul>
    <h3>Korisnički servis</h3><ul class="ftr__list">{pol}</ul></div>
   <div><h3>Prodavnica</h3><ul class="ftr__list">{sitemap}<li><a href="{Rp}nalog.html">Moj nalog</a></li><li><a href="{BIZ['b2b']}" rel="noopener">B2B portal {icon('arrow-ne')}</a></li></ul></div>
  </div>
 </div>
 <div class="ftr__sign" aria-hidden="true"><p data-bye>Srećan put.</p></div>
 <div class="wrap ftr__legal"><p>Udobnost, performanse i sigurnost — srećan put želi Vam Čajka M Čačak.</p><p>© 1992–2026 {BIZ['name']} Sva prava zadržana.</p></div>
</footer>'''


FONTS = ('https://fonts.googleapis.com/css2?family=Barlow+Condensed:ital,wght@0,500;0,600;0,700;0,800;1,700'
         '&family=Inter:wght@400;500;600;700&display=swap')


LOCAL_PAGES = {'', 'kontakt/', 'guma-servis/', 'hotel-za-gume/', 'o-nama/'}


def descriptions():
    return {
        'index.html': f'Online prodaja guma Čajka M iz Čačka: gume za automobile, kombije, kamione, radne i poljoprivredne mašine. Dva servisa i hotel za gume u Čačku.',
        'gume.html': f'Katalog guma Čajka M: gume za automobile, kombije, kamione, viljuškare i traktore. Filtrirajte po dimenziji, sezoni, proizvođaču i ceni.',
        'akcije.html': f'Gume na akciji u Čajka M: modeli sa sniženom cenom, do {MAX_DISCOUNT} % popusta. Cene po komadu sa PDV-om, dostava 1-3 radna dana.',
        'servis.html': 'Guma Servis u Čačku, Dr. Dragiše Mišovića 100: montaža i balansiranje od 400 RSD, reglaža trapa, vulkanizerske usluge i brzi servis. Zakažite termin.',
        'hotel-za-gume.html': 'Hotel za gume u Čačku: čuvanje guma svih vrsta i veličina, 600 RSD po komadu za jednu sezonu, uz montažu i balansiranje u Guma Servisu.',
        'brendovi.html': 'Brendovi guma u ponudi Čajka M: Continental, Goodyear, Michelin, Sava, Tigar i drugi. Ovlašćeni uvoznik brendova Speedways i Tourador.',
        'blog.html': 'Saveti o gumama: izbor, oznake, pritisak, čuvanje i sezonska zamena guma. Blog Čajka M iz Čačka.',
        'o-nama.html': 'Čajka M iz Čačka, osnovana 1992: uvoz i prodaja pneumatika u Srbiji i regionu. SRPS ISO 9001:2015 i 14001:2015, uvoznik Speedways i Tourador.',
        'kontakt.html': f'Kontakt Čajka M: {BIZ["address"]} i Guma Servis, {BIZ["service_address"]}, Čačak. Tel. {BIZ["phone"]}, radno vreme i mapa.',
        'cesta-pitanja.html': 'Česta pitanja o kupovini guma u Čajka M: poručivanje, isporuka 1-3 radna dana, plaćanje pouzećem, garancija i reklamacije.',
        'reklamacije.html': 'Reklamacije na gume kupljene u Čajka M: postupak, potrebni podaci i obrazac za prijavu reklamacije.',
        'uslovi-isporuke.html': 'Uslovi isporuke guma kupljenih u online prodavnici Čajka M: rokovi i način dostave.',
        'zastita-potrosaca.html': 'Zaštita potrošača u Čajka M: prava kupaca pri kupovini guma na daljinu.',
        'uslovi-koriscenja.html': 'Uslovi korišćenja i prodaje online prodavnice guma Čajka M iz Čačka.',
        'politika-privatnosti.html': 'Politika privatnosti Čajka M: kako prikupljamo, koristimo i čuvamo podatke kupaca.',
        'korpa.html': 'Vaša korpa u online prodavnici guma Čajka M.', 'kasa.html': 'Poručivanje guma u online prodavnici Čajka M.',
        'nalog.html': 'Prijava i registracija kupaca Čajka M.', 'uporedi.html': 'Uporedite do četiri gume jednu pored druge.',
    }


def page(path, title, body, active='', desc='', scripts=(), cls='', head_extra='', ld=(), og_image=None,
         og_type='website', noindex=None, sitemap='strane', images=()):
    """Write one page. `path` is the template name (gume.html, blog/<slug>.html,
    kupi-gume/<slug>/index.html …); seo.out_file() maps it to its public address."""
    out_path = seo.out_file(path)
    Rp = '../' * out_path.count('/')
    pub = seo.clean(out_path)
    page_url = seo.public(pub)
    canon = seo.canonical(pub)
    if noindex is None:
        noindex = pub in seo.NOINDEX
    desc = desc or descriptions().get(path) or ('Online prodaja guma - Čajka M Čačak. Putničke, poluteretne, teretne, industrijske i '
                    'poljoprivredne gume, Guma Servis i hotel za gume.')
    og_img = og_image or seo.public('assets/img/og-cajkam.jpg')
    social = f'''<link rel="canonical" href="{esc(canon)}">
<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="Čajka M">
<meta property="og:locale" content="sr_RS">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{esc(canon)}">
<meta property="og:image" content="{esc(og_img)}">
<meta name="twitter:card" content="summary_large_image">'''
    robots = '<meta name="robots" content="noindex, follow">' + chr(10) if noindex else ''
    # One module per page. Page modules import ./core.js themselves; loading
    # core.js as well would create a second instance (double clicks).
    mod = scripts[0] if scripts else 'core'
    doc = f'''<!doctype html>
<html lang="sr-Latn" data-root="{Rp}" data-v="{VER}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
{robots}{social}
<meta name="theme-color" content="#101416">
<meta name="view-transition" content="same-origin">
<link rel="icon" href="{Rp}assets/img/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="{FONTS}">
<link rel="stylesheet" href="{Rp}assets/css/site.css?v={VER}">
<script>document.documentElement.classList.add('js');try{{var q=location.search;if(/[?&]motion=0/.test(q))sessionStorage.setItem('cm.motion','0');if(/[?&]motion=1/.test(q))sessionStorage.removeItem('cm.motion');if(sessionStorage.getItem('cm.motion')==='0')document.documentElement.classList.add('calm')}}catch(e){{}}</script>
{head_extra}
<!--LD-->
</head>
<body class="{cls}">
{header(Rp, active)}
<main id="main">
{body}
</main>
{footer(Rp)}
{drawer(Rp)}
<script type="module" src="{Rp}assets/js/{mod}.js?v={VER}"></script>
</body>
</html>'''
    doc = doc.replace('{R}', Rp)
    if Rp:
        # templates were written with root-relative links ("gume.html", "assets/…"); pages now
        # live in sub-folders, so anchor every plain relative reference at the site root
        doc = re.sub(r'(href|action|src)="(?!\.\./|/|#|[a-z]+:)([^"]+)"', lambda m: f'{m.group(1)}="{Rp}{m.group(2)}"', doc)
        doc = re.sub(r"url\((?!['\"]?(?:\.\./|/|[a-z]+:))", f'url({Rp}', doc)
    doc = seo.route_links(doc)
    # house style: a plain hyphen instead of the em dash, everywhere (templates and imported texts)
    doc = doc.replace('&mdash;', '-').replace('—', '-')
    graph = seo.org_graph(BIZ) + (seo.local_graph(BIZ) if pub in LOCAL_PAGES else []) + seo.breadcrumb_graph(doc, page_url) + list(ld)
    doc = doc.replace('<!--LD-->', seo.ld_script(graph))
    out = ROOT / out_path
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(doc, encoding='utf-8')
    if not noindex and pub not in ('404.html',):
        seo.SITEMAP.append((pub, sitemap, list(images)))
    return out_path


# --------------------------------------------------------------- building blocks
def km(no, text, light=False):
    """Small section label above a heading (the number is kept for call sites, not shown)."""
    return f'<p class="km{" km--light" if light else ""}">{text}</p>'


def crumbs(items):
    li = ''.join(f'<li><a href="{R}{h}">{t}</a></li>' if h else f'<li aria-current="page">{t}</li>' for h, t in items)
    return f'<nav class="crumbs" aria-label="Putanja"><ol>{li}</ol></nav>'


def page_head(title, lede='', label='', trail=(), extra='', no=1, dark=False):
    return f'''<section class="phead{' phead--dark' if dark else ''}"><div class="wrap">
 {crumbs([('index.html', 'Početna'), *trail, (None, title)])}
 {km(no, label) if label else ''}
 <h1 class="phead__t" data-split>{title}</h1>
 {f'<p class="phead__lede">{lede}</p>' if lede else ''}{extra}
 <div class="phead__road" aria-hidden="true"></div>
</div></section>'''


def todo(text):
    """Visible marker for content the client still has to supply."""
    return f'<span class="todo" title="Sadržaj za dopunu">{icon("info")}{text}</span>'


def media_slot(label, ratio='4/3', cls='', ico='wrench'):
    """Placeholder for photography that must come from the client."""
    return (f'<figure class="slot {cls}" style="aspect-ratio:{ratio}" data-reveal="wipe"><div class="slot__art" aria-hidden="true">{icon(ico)}</div>'
            f'<figcaption>{todo("Fotografija za dopunu")}<span>{label}</span></figcaption></figure>')


def season_label(z):
    return {'letnja': 'Letnja', 'zimska': 'Zimska', 'sve': 'Sve sezone'}.get(z, '')


def img_url(p, full=False):
    t = p.get('i', '')
    if full:
        t = re.sub(r'-\d+x\d+(\.\w+)$', r'\1', t)
    return UPLOADS + t if t else ''


def card(p):
    """Server-side twin of cardHTML() in core.js (same markup, same classes)."""
    sale = 'r' in p and 0 < p['p'] < p['r'] and not p.get('np')
    pct = round((1 - p['p'] / p['r']) * 100) if sale else 0
    idx = f'{p["li"]}{p["si"]}' if p.get('li') else ''
    flags = ''.join(f'<span class="tag">{f}</span>' for f in p.get('f', []) if f in ('XL', 'RunFlat'))
    stock = ('<p class="stock stock--ok"><i></i>Na stanju</p>' if p['st'] else
             '<p class="stock stock--no"><i></i>Nije na stanju</p>')
    price = ('<p class="price price--ask">Cena na upit</p>' if p.get('np') else
             f'<p class="price">{f"<s>{fmt(p["r"])}</s>" if sale else ""}<b>{fmt(p["p"])}</b><small>sa PDV-om</small></p>')
    z = p['z']
    snap = {k: p[k] for k in ('id', 's', 'sz', 'b', 'm', 'p', 'r', 'i', 'st', 'z', 'li', 'si') if k in p}
    href = f'{R}guma.html?p={p["s"]}'
    return f'''<article class="card" data-id="{p['id']}" data-snap='{esc(json.dumps(snap, ensure_ascii=False))}'>
 <a class="card__media" href="{href}" tabindex="-1" aria-hidden="true">
  <img src="{img_url(p)}" alt="" loading="lazy" decoding="async" width="300" height="300">
  {f'<span class="card__sale">−{pct} %</span>' if sale else ''}{f'<span class="season" data-s="{z}"><i></i>{season_label(z)}</span>' if z else ''}
 </a>
 <div class="card__body">
  <p class="card__brand">{esc(p['b']) or '&nbsp;'}</p>
  <h3 class="card__title"><a href="{href}"><span class="sz">{esc(p['sz'])}</span><span class="card__model">{esc(p['m'])}</span></a></h3>
  <p class="card__meta">{f'<span class="tag tag--idx">{idx}</span>' if idx else ''}{flags}</p>
  <div class="card__foot">{price}{stock}</div>
 </div>
 <div class="card__act">
  <button class="btn btn--go btn--sm" data-add="{p['id']}"{' disabled' if not p['st'] or p.get('np') else ''}>{icon('cart')}<span>U korpu</span></button>
  <button class="icon-btn icon-btn--line" data-compare="{p['id']}" aria-pressed="false" aria-label="Dodaj u poređenje">{icon('compare')}</button>
 </div>
</article>'''


def rail(cards_html, label):
    return f'''<div class="rail" data-rail>
 <div class="rail__track" tabindex="0" aria-label="{label}">{cards_html}</div>
 <div class="rail__bar"><div class="rail__progress"><i data-rail-progress></i></div>
  <div class="rail__nav"><button class="icon-btn icon-btn--line" data-rail-prev aria-label="Prethodne">{icon('arrow-left')}</button><button class="icon-btn icon-btn--line" data-rail-next aria-label="Sledeće">{icon('arrow')}</button></div></div>
</div>'''


def explainer():
    parts = [('205', 'Širina', 'Širina gume u milimetrima.'),
             ('55', 'Visina', 'Visina bočnice kao procenat širine (55 % od 205 mm).'),
             ('R', 'Konstrukcija', 'R označava radijalnu gumu.'),
             ('16', 'Prečnik', 'Prečnik felne u colima.'),
             ('91', 'Indeks nosivosti', 'Najveće dozvoljeno opterećenje po gumi (91 = 615 kg).'),
             ('V', 'Indeks brzine', 'Najveća dozvoljena brzina (V = 240 km/h).')]
    segs = []
    for i, (a, _, _) in enumerate(parts):
        if i == 1:
            segs.append('<span class="xp__slash">/</span>')
        if i in (2, 4):
            segs.append('<span class="xp__gap"></span>')
        segs.append(f'<button type="button" class="xp__seg" data-xp="{i}" aria-pressed="{str(i == 0).lower()}">{a}</button>')
    info = ''.join(f'<div class="xp__info" data-xp-info="{i}"{"" if i == 0 else " hidden"}><b>{b}</b><p>{c}</p></div>'
                   for i, (_, b, c) in enumerate(parts))
    return f'''<dialog class="xp" data-xp-dialog aria-labelledby="xp-t">
 <div class="xp__in">
  <button class="icon-btn xp__x" data-xp-close aria-label="Zatvori">{icon('close')}</button>
  <p class="label">Bočnica gume</p>
  <h2 id="xp-t" class="d3">Dimenzija piše na vašoj gumi</h2>
  <p>Pogledajte bočnicu gume koju trenutno vozite. Niz poput ovog je sve što vam treba — dodirnite deo oznake:</p>
  <div class="xp__code" role="group" aria-label="Primer oznake 205/55 R16 91V">{''.join(segs)}</div>
  {info}
  <p class="fine">Za kupovinu su dovoljna prva tri broja: širina, visina i prečnik. Niste sigurni? Pozovite nas: <a href="tel:{BIZ['phone_href']}">{BIZ['phone']}</a>.</p>
  <button class="btn btn--ink btn--block" data-xp-close><span>Razumem, biram dimenziju</span></button>
 </div>
</dialog>'''


MONTHS = ['januar', 'februar', 'mart', 'april', 'maj', 'jun', 'jul', 'avgust', 'septembar', 'oktobar', 'novembar', 'decembar']


def date_sr(d):
    y, m, dd = d.split('-')
    return f'{int(dd)}. {MONTHS[int(m) - 1]} {y}.'


def post_card(p, big=False):
    img = f'<img src="{p["img"]}" alt="" loading="lazy" decoding="async">' if p['img'] else '<div class="post__noimg" aria-hidden="true"></div>'
    cat = {'Uncategorized': 'Saveti'}.get(p['cat'], p['cat'] or 'Saveti')
    return f'''<article class="post{' post--big' if big else ''}" data-reveal>
 <a class="post__media" href="{R}blog/{p['slug']}.html" tabindex="-1" aria-hidden="true">{img}</a>
 <p class="post__meta"><span>{cat}</span><time datetime="{p['date']}">{date_sr(p['date'])}</time><span>{p['min']} min</span></p>
 <h3 class="post__t"><a href="{R}blog/{p['slug']}.html">{esc(p['title'])}</a></h3>
 {f'<p class="post__x">{esc(p["excerpt"][:170].rsplit(" ", 1)[0])}…</p>' if big else ''}
</article>'''


OLD_TO_NEW = {
    'reklamacije': 'reklamacije.html', 'uslovi-isporuke': 'uslovi-isporuke.html', 'zastita-potrosaca': 'zastita-potrosaca.html',
    'uslovi-koriscenja': 'uslovi-koriscenja.html', 'politika-privatnosti': 'politika-privatnosti.html',
    'najcesce-postavljana-pitanja': 'cesta-pitanja.html', 'guma-servis': 'servis.html', 'hotel-za-gume': 'hotel-za-gume.html',
    'kontakt': 'kontakt.html', 'kako-do-nas': 'kontakt.html#kako-do-nas', 'o-nama': 'o-nama.html', 'brendovi': 'brendovi.html',
    'akcije-2': 'akcije.html', 'blog': 'blog.html', 'kupi-gume': 'gume.html', '': 'index.html',
}


def relink(h):
    """Imported WordPress HTML: send known pages to their redesigned twins,
    everything else site-relative back to cajkam.rs (files, uploads)."""
    def sub(m):
        url = m.group(1)
        path = re.sub(r'^https?://(www\.)?cajkam\.rs', '', url)
        if path == url and not url.startswith('/'):
            return m.group(0)
        slug = path.strip('/').split('?')[0]
        if slug in OLD_TO_NEW:
            return f'href="{R}{OLD_TO_NEW[slug]}"'
        if slug.count('/') == 3 and re.match(r'\d{4}/\d{2}/\d{2}/', slug):
            return f'href="{R}blog/{slug.split("/")[-1]}.html"'
        if slug.startswith('proizvodjac/'):
            brand = {b.lower(): b for b, _ in BRANDS['counts'] if b}.get(slug.split('/')[1].replace('-', ' '))
            season = re.search(r'pa_sezona=(letnja|zimska)', path)
            if brand:
                return f'href="{R}gume.html?brend={brand}{"&amp;sezona=" + season[1] if season else ""}"'
        if slug.startswith('kategorija-proizvoda/'):
            return f'href="{R}gume.html?tip={slug.split("/")[1]}"'
        if slug.startswith('kupi-gume/'):
            return f'href="{R}guma.html?p={slug.split("/")[1]}"'
        return f'href="https://cajkam.rs{path}"'
    return re.sub(r'href="([^"]+)"', sub, h)


def favicon():
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="-32 -32 64 64"><rect x="-32" y="-32" width="64" height="64" rx="14" fill="#243B4A"/>'
           f'<path fill="#F2B51C" transform="scale(.95)" d="{SEAGULL}"/></svg>')
    (ROOT / 'assets' / 'img' / 'favicon.svg').write_text(svg, encoding='utf-8')
    write_treads()
    write_sprite()
