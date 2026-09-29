"""Static site generator for the Čajka M redesign, concept "Trag".

    python tools/build.py

Reads data/*.json (produced by tools/import.py) and writes every page to the
project root. All links are relative, so the output works from a domain root,
a sub-path or straight from disk. Python only, no Node.

Templates live in tools/site/*.py; this file holds shared data and layout.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

# One stylesheet, authored in parts (assets/css/src/NN-*.css). Concatenate
# before site_lib is imported, because it hashes the assets for cache-busting.
_css = Path(__file__).resolve().parent.parent / 'assets' / 'css'
(_css / 'site.css').write_text('\n'.join(p.read_text(encoding='utf-8') for p in sorted((_css / 'src').glob('*.css'))),
                               encoding='utf-8')

from site_lib.base import ROOT, POSTS, write_data, favicon  # noqa: E402
from site_lib import pages_home, pages_shop, pages_info  # noqa: E402


def main():
    write_data()
    favicon()
    out = [pages_home.home(), *pages_shop.all_pages(), *pages_info.all_pages()]
    (ROOT / '.nojekyll').write_text('', encoding='utf-8')
    print('built', len(out) + len(POSTS), 'pages')


if __name__ == '__main__':
    main()
