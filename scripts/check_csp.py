#!/usr/bin/env python3
"""Check that each page's CSP meta allows exactly the hash of its inline script and style.

A page is checked for a tag only when its CSP allows that tag by hash
(`script-src 'sha256-…'`, `style-src 'sha256-…'`); it must then have exactly one such inline tag.

  python3 scripts/check_csp.py          # exit 1 on a stale hash
  python3 scripts/check_csp.py --fix    # rewrite the stale hashes
"""

import base64
import hashlib
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TAGS = ("script", "style")


def csp_hash(tag):
    return re.compile(tag + r"-src 'sha256-([A-Za-z0-9+/=]+)'")


def inline(tag):
    return re.compile(f"<{tag}>(.*?)</{tag}>", re.S)


def expected(html, tag="script"):
    """The base64 SHA-256 of the page's single inline <tag>."""
    blocks = inline(tag).findall(html)
    if len(blocks) != 1:
        raise ValueError(f"expected one inline {tag}, found {len(blocks)}")
    return base64.b64encode(hashlib.sha256(blocks[0].encode()).digest()).decode()


def main(fix):
    stale = []
    for page in sorted(ROOT.rglob("*.html")):
        html = page.read_text()
        for tag in TAGS:
            found = csp_hash(tag).search(html)
            if not found:
                continue
            want = expected(html, tag)
            if found.group(1) != want:
                stale.append((page.relative_to(ROOT), tag))
                if fix:
                    html = html[:found.start(1)] + want + html[found.end(1):]
                    page.write_text(html)
    for page, tag in stale:
        print(f"{'fixed' if fix else 'stale'} CSP {tag} hash: {page}")
    return 0 if fix or not stale else 1


if __name__ == "__main__":
    sys.exit(main("--fix" in sys.argv))
