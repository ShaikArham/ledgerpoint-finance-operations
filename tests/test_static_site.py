"""Static site release checks using only Python's standard library."""
from html.parser import HTMLParser
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
class Inspector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()
        self.links = []
        self.scripts = []
        self.styles = []
        self.images = []
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "id" in a:
            assert a["id"] not in self.ids, f"Duplicate id: {a['id']}"
            self.ids.add(a["id"])
        if tag == "a" and "href" in a: self.links.append(a["href"])
        if tag == "script" and "src" in a: self.scripts.append(a["src"])
        if tag == "link" and a.get("rel") == "stylesheet": self.styles.append(a["href"])
        if tag == "img" and "src" in a: self.images.append(a["src"])

def test_static_assets_and_navigation():
    html = (ROOT / "index.html").read_text(encoding="utf-8")
    inspector = Inspector()
    inspector.feed(html)
    for path in inspector.scripts + inspector.styles + inspector.images:
        assert (ROOT / path).is_file(), f"Missing asset: {path}"
    for link in inspector.links:
        if link.startswith("#"):
            assert link[1:] in inspector.ids, f"Broken navigation: {link}"
    assert "viewport" in html
    assert "Not affiliated" in html

def test_all_five_views_are_reachable():
    html = (ROOT / "index.html").read_text(encoding="utf-8")
    js = (ROOT / "script.js").read_text(encoding="utf-8")
    for view in ("overview", "reconciliation", "invoices", "performance", "case-study"):
        assert f'id="{view}"' in html
        assert f'data-view="{view}"' in html
        assert view in js

def test_accessibility_and_responsive_basics():
    html = (ROOT / "index.html").read_text(encoding="utf-8")
    css = (ROOT / "styles.css").read_text(encoding="utf-8")
    assert 'class="skip"' in html
    assert "prefers-reduced-motion" in css
    assert "max-width:900px" in css
    assert "max-width:560px" in css
    assert "overflow-x:auto" in css
    assert "aria-label" in html

def test_no_unintended_external_dependencies():
    html = (ROOT / "index.html").read_text(encoding="utf-8")
    assert not re.search(r'<script[^>]+src=["\']https?://', html)
    assert not re.search(r'<link[^>]+href=["\']https?://', html)
