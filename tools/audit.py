"""Check every built page: local links/assets resolve (relative to the page's own
folder), no leftover template tokens, one <h1>, and the page modules exist.

    python tools/audit.py
"""
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
pages = sorted(p for p in ROOT.rglob('*.html') if 'data' not in p.parts and 'media' not in p.parts)
bad, checked = [], 0
for page in pages:
    html = page.read_text(encoding='utf-8')
    if '{R}' in html:
        bad.append(f'{page.name}: unreplaced {{R}}')
    h1 = len(re.findall(r'<h1[\s>]', html))
    if h1 != 1 and page.name not in ('guma.html',):  # pdp swaps its h1 on a missing product
        bad.append(f'{page.relative_to(ROOT)}: {h1} <h1>')
    for ref in re.findall(r'(?:href|src)="([^"#]+)', html):
        u = urlparse(ref)
        if u.scheme or ref.startswith(('mailto:', 'tel:', '//', 'data:')):
            continue
        target = (page.parent / u.path).resolve()
        checked += 1
        if not target.exists():
            bad.append(f'{page.relative_to(ROOT)} -> {ref}')

print(f'{len(pages)} pages, {checked} local links checked')
if checked == 0:
    sys.exit('audit checked zero links - the pattern is wrong, not the site')
for b in sorted(set(bad)):
    print('  FAIL', b)
sys.exit(1 if bad else 0)
