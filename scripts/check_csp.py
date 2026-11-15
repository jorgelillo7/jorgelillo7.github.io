#!/usr/bin/env python3
"""Check that each page's CSP meta allows exactly the hash of its inline script.

  python3 scripts/check_csp.py          # exit 1 on a stale hash
  python3 scripts/check_csp.py --fix    # rewrite the stale hashes
"""

import base64
import hashlib
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CSP = re.compile(r"script-src 'sha256-([A-Za-z0-9+/=]+)'")
SCRIPT = re.compile(r"<script>(.*?)</script>", re.S)


def expected(html):
    """The base64 SHA-256 of the page's single inline script."""
    scripts = SCRIPT.findall(html)
    if len(scripts) != 1:
        raise ValueError(f"expected one inline script, found {len(scripts)}")
    return base64.b64encode(hashlib.sha256(scripts[0].encode()).digest()).decode()


def main(fix):
    stale = []
    for page in sorted(ROOT.rglob("*.html")):
        html = page.read_text()
        found = CSP.search(html)
        if not found:
            continue
        want = expected(html)
        if found.group(1) != want:
            stale.append(page.relative_to(ROOT))
            if fix:
                page.write_text(html.replace(found.group(1), want, 1))
    for page in stale:
        print(f"{'fixed' if fix else 'stale'} CSP script hash: {page}")
    return 0 if fix or not stale else 1


if __name__ == "__main__":
    sys.exit(main("--fix" in sys.argv))
