#!/usr/bin/env python3
"""Validate a Piscine Nette Salon page against the site's content/SEO rules."""
import json
import os
import re
import sys

VILLAGES_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "villages.json")


def load_villages():
    with open(VILLAGES_PATH, encoding="utf-8") as f:
        return json.load(f)


def validate(html, page_slug, villages, is_hub=False):
    """Return a list of human-readable error strings; empty means the page passes."""
    errors = []

    if "<title>" not in html or "</title>" not in html:
        errors.append("Missing <title> tag")

    if 'name="description"' not in html:
        errors.append("Missing meta description")

    if 'rel="canonical"' not in html:
        errors.append("Missing canonical link")

    if '"@type": "Service"' not in html:
        errors.append("Missing JSON-LD Service structured data")

    if "€" in html:
        errors.append("Page must not display any price (found '€')")

    if "formsubmit.co" not in html:
        errors.append("Missing formsubmit.co lead form")

    if 'name="_honey"' not in html:
        errors.append("Missing honeypot anti-spam field")

    if (
        "On vous recontacte pour cerner la demande" not in html
        or "Un professionnel qualifié intervient chez vous" not in html
    ):
        errors.append("Missing or altered honest-intermediary step 3 copy")

    ld_json_match = re.search(
        r'<script type="application/ld\+json">(.*?)</script>', html, re.DOTALL
    )
    if not is_hub:
        current = next((v for v in villages if v["slug"] == page_slug), None)
        if current:
            ld_json_content = ld_json_match.group(1) if ld_json_match else ""
            if current["name"] not in ld_json_content:
                errors.append(
                    f"JSON-LD areaServed block does not contain village name '{current['name']}'"
                )

    other_villages = [v for v in villages if v["slug"] != page_slug]
    if is_hub:
        expected_min = len(villages)
        footer_links = len(re.findall(r'href="[a-z-]+/"', html))
    else:
        expected_min = len(other_villages)
        footer_links = len(re.findall(r'href="\.\./[a-z-]+/"', html))
    if footer_links < expected_min:
        errors.append(f"Footer should link to {expected_min} other pages, found {footer_links}")

    if not is_hub:
        current = next((v for v in villages if v["slug"] == page_slug), None)
        if current and current["name"] not in html:
            errors.append(f"Village name '{current['name']}' not found in page content")
        if current and f'href="../{page_slug}/"' in html:
            errors.append("Footer must not self-link to the current village's own page")

    return errors


def main():
    if len(sys.argv) < 2:
        print("Usage: validate_page.py <path/to/index.html> [--hub]", file=sys.stderr)
        sys.exit(2)
    path = sys.argv[1]
    is_hub = "--hub" in sys.argv
    with open(path, encoding="utf-8") as f:
        html = f.read()
    villages = load_villages()
    slug = None if is_hub else os.path.basename(os.path.dirname(os.path.abspath(path)))
    errors = validate(html, slug, villages, is_hub=is_hub)
    if errors:
        print(f"FAIL: {path}")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)
    print(f"OK: {path}")


if __name__ == "__main__":
    main()
