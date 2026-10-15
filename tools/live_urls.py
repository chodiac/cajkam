"""Snapshot of every URL the current WordPress cajkam.rs lists in its sitemaps.

    python tools/live_urls.py

Writes data/live-urls.txt (one site-relative path per line, e.g. kupi-gume/<slug>/).
The build uses it to decide which canonical URLs already exist on cajkam.rs
(see SWITCHED in tools/site_lib/seo.py) and to write the 301 map for pages
whose address changes.
"""
import re
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASE = 'https://cajkam.rs/'


def get(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'cajkam-redesign-build'})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode('utf-8', 'replace')


def main():
    index = get(BASE + 'sitemap_index.xml')
    paths = set()
    for sm in re.findall(r'<loc>([^<]+)</loc>', index):
        for loc in re.findall(r'<loc>([^<]+)</loc>', get(sm)):
            if loc.startswith(BASE):
                paths.add(loc[len(BASE):])
    out = ROOT / 'data' / 'live-urls.txt'
    out.write_text('\n'.join(sorted(paths)) + '\n', encoding='utf-8')
    print('live urls', len(paths), '->', out)


if __name__ == '__main__':
    main()
