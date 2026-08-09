# Piscine Nette Salon Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a static, GitHub-Pages-hosted lead-generation site for pool maintenance around Salon-de-Provence — one hub page + 14 village pages — reusing the exact template already proven on `karcher-k7-salon` / `bissell-location-salon`, pushed further on local SEO.

**Architecture:** Pure static HTML/CSS, one directory per village (`<slug>/index.html`), a single shared `assets/style.css`, a `formsubmit.co`-backed lead form on every page, and two small Python stdlib-only scripts (a Pexels image fetcher, a page-content validator) with no other dependencies.

**Tech Stack:** HTML5, CSS (no framework), vanilla Python 3 (stdlib only) for the two support scripts, Pexels API for stock photos, GitHub Pages for hosting.

## Global Constraints

- No price or currency figure (`€` or any number+"euro") appears anywhere on any page — every CTA is a free-quote request ("Devis gratuit sous 24h"), never a price.
- `assets/style.css` is byte-identical to `karcher-k7-salon`'s (given verbatim in Task 1) — no visual customization for this vertical.
- No build step, no JS framework, no npm/node — plain files only, exactly as in the two existing sites.
- Lead form on every page posts to `https://formsubmit.co/nicolas@noilhan.com`, includes a hidden honeypot field `name="_honey"`, and redirects to `https://a-louer.github.io/piscine-entretien-salon/merci.html`.
- Copy never claims a specific company performs the maintenance work — the "Comment ça marche" section always uses this exact 3-step framing: (1) the visitor describes their need, (2) "on vous recontacte pour cerner la demande", (3) "un professionnel qualifié du secteur intervient chez vous".
- Every content page (hub + 14 villages) carries a `<script type="application/ld+json">` block of type `Service` with a `provider` of type `LocalBusiness` and an `areaServed` naming that page's village.
- Footer "Autres secteurs desservis" list must **exclude the current page's own village** (the existing Bissell/Kärcher sites incorrectly self-link here — this is a deliberate fix, not a deviation to flag). The separate "Zone de service" chip list may still include the current village, since it's phrased as a service-area summary, not an "other pages" list.
- Repo: `a-louer/piscine-entretien-salon`, default branch `main` (already pushed with the design spec) — note this differs from the two older sites, which use `master`.

---

### Task 1: Scaffolding — shared assets, village manifest, robots.txt, merci.html

**Files:**
- Create: `assets/style.css`
- Create: `robots.txt`
- Create: `merci.html`
- Create: `scripts/villages.json`
- Create: `scripts/image-manifest.json`
- Test: none (static content + data files; validated structurally by later tasks that consume them)

**Interfaces:**
- Produces: `scripts/villages.json` — a JSON array of 14 objects, each `{"name": str, "slug": str, "intro": str}`, consumed by `scripts/validate_page.py` (Task 2), the sitemap (Task 10), and every village-page task (Tasks 5-9) for the exact intro sentence and footer link set.
- Produces: `scripts/image-manifest.json` — a JSON array of 15 objects `{"filename": str, "query": str}`, consumed by `scripts/fetch_images.py` (Task 3).

- [ ] **Step 1: Create `assets/style.css`** with exactly this content (byte-identical to `karcher-k7-salon`/`bissell-location-salon`'s shared template):

```css
  :root{
    --ink:#1c2320;
    --ink-soft:#4a534f;
    --cream:#fbf6ee;
    --cream-2:#f3ecdd;
    --teal:#0d5c56;
    --teal-dark:#0a4a45;
    --coral:#e1592f;
    --coral-dark:#c2461f;
    --line:#e3dccb;
    --radius:14px;
    --shadow:0 12px 32px -12px rgba(28,35,32,.18);
  }
  *{box-sizing:border-box;margin:0;padding:0}
  html{scroll-behavior:smooth}
  body{
    font-family:'Inter',system-ui,sans-serif;
    color:var(--ink);
    background:var(--cream);
    line-height:1.55;
    -webkit-font-smoothing:antialiased;
  }
  h1,h2,h3{font-family:'Fraunces',Georgia,serif;font-weight:600;letter-spacing:-0.01em;color:var(--ink)}
  a{color:inherit}
  img{max-width:100%;display:block}
  .wrap{max-width:1080px;margin:0 auto;padding:0 24px}

  /* Header */
  header{
    position:sticky;top:0;z-index:50;
    background:rgba(251,246,238,.92);
    backdrop-filter:blur(8px);
    border-bottom:1px solid var(--line);
  }
  .nav{display:flex;align-items:center;justify-content:space-between;padding:16px 24px;max-width:1080px;margin:0 auto}
  .brand{display:flex;align-items:center;gap:10px;font-family:'Fraunces',serif;font-weight:600;font-size:1.05rem}
  .brand-dot{width:10px;height:10px;border-radius:50%;background:var(--coral)}
  .nav-cta{
    background:var(--teal);color:#fff;padding:10px 20px;border-radius:100px;
    font-weight:600;font-size:.9rem;text-decoration:none;transition:background .15s;
    white-space:nowrap;
  }
  .nav-cta:hover{background:var(--teal-dark)}

  /* Hero */
  .hero{padding:56px 0 64px}
  .hero-grid{display:grid;grid-template-columns:1.1fr 1fr;gap:48px;align-items:center}
  .eyebrow{
    display:inline-flex;align-items:center;gap:8px;
    background:var(--cream-2);border:1px solid var(--line);
    padding:6px 14px;border-radius:100px;font-size:.82rem;font-weight:600;
    color:var(--teal-dark);margin-bottom:20px;
  }
  .hero h1{font-size:2.6rem;line-height:1.08;margin-bottom:18px}
  .hero h1 em{font-style:normal;color:var(--coral)}
  .hero p.lead{font-size:1.1rem;color:var(--ink-soft);max-width:46ch;margin-bottom:28px}
  .price-badge{
    display:inline-flex;align-items:baseline;gap:6px;
    background:var(--teal);color:#fff;padding:14px 22px;border-radius:12px;
    margin-bottom:28px;box-shadow:var(--shadow);
  }
  .price-badge .num{font-family:'Fraunces',serif;font-size:1.9rem;font-weight:700}
  .price-badge .unit{font-size:.95rem;opacity:.85}
  .hero-actions{display:flex;gap:14px;flex-wrap:wrap}
  .btn-primary{
    background:var(--coral);color:#fff;padding:15px 28px;border-radius:100px;
    font-weight:700;text-decoration:none;font-size:1rem;
    box-shadow:0 10px 24px -8px rgba(225,89,47,.55);
    transition:transform .15s, background .15s;
  }
  .btn-primary:hover{background:var(--coral-dark);transform:translateY(-1px)}
  .btn-ghost{
    padding:15px 24px;border-radius:100px;font-weight:600;text-decoration:none;
    border:1.5px solid var(--line);color:var(--ink);
  }
  .hero-img{
    position:relative;border-radius:20px;overflow:hidden;box-shadow:var(--shadow);
    aspect-ratio:4/3;
  }
  .hero-img img{width:100%;height:100%;object-fit:cover}
  .hero-img::after{
    content:"";position:absolute;inset:0;
    background:linear-gradient(180deg,rgba(0,0,0,0) 60%,rgba(0,0,0,.35) 100%);
  }
  .hero-img-tag{
    position:absolute;bottom:16px;left:16px;z-index:2;
    background:rgba(255,255,255,.94);padding:8px 14px;border-radius:10px;
    font-size:.82rem;font-weight:600;color:var(--ink);
  }

  /* Sections */
  section{padding:64px 0}
  .section-head{max-width:52ch;margin-bottom:40px}
  .section-head .kicker{color:var(--coral);font-weight:700;font-size:.82rem;text-transform:uppercase;letter-spacing:.06em;display:block;margin-bottom:10px}
  .section-head h2{font-size:1.9rem}

  .features{display:grid;grid-template-columns:repeat(3,1fr);gap:24px}
  .feature-card{
    background:#fff;border:1px solid var(--line);border-radius:var(--radius);
    padding:28px 24px;
  }
  .feature-icon{
    width:44px;height:44px;border-radius:10px;background:var(--cream-2);
    display:flex;align-items:center;justify-content:center;margin-bottom:16px;font-size:1.3rem;
  }
  .feature-card h3{font-size:1.1rem;margin-bottom:8px}
  .feature-card p{color:var(--ink-soft);font-size:.95rem}

  .how{background:var(--teal);color:#fff;border-radius:24px}
  .how .section-head h2{color:#fff}
  .how .section-head .kicker{color:#9fd8cf}
  .steps{display:grid;grid-template-columns:repeat(3,1fr);gap:28px}
  .step{position:relative;padding-left:44px}
  .step-num{
    position:absolute;left:0;top:0;width:32px;height:32px;border-radius:50%;
    background:rgba(255,255,255,.15);border:1.5px solid rgba(255,255,255,.4);
    display:flex;align-items:center;justify-content:center;font-weight:700;font-size:.9rem;
  }
  .step h3{color:#fff;font-size:1.05rem;margin-bottom:6px}
  .step p{color:rgba(255,255,255,.82);font-size:.92rem}

  .zone{display:grid;grid-template-columns:1fr 1fr;gap:40px;align-items:center}
  .zone-list{list-style:none;display:flex;flex-wrap:wrap;gap:10px;margin-top:20px}
  .zone-list li{
    background:#fff;border:1px solid var(--line);padding:8px 16px;border-radius:100px;
    font-size:.88rem;font-weight:500;
  }
  .zone-note{color:var(--ink-soft);font-size:.92rem;margin-top:16px}

  /* Form */
  .contact{background:var(--cream-2);border-radius:24px}
  .contact-grid{display:grid;grid-template-columns:.9fr 1.1fr;gap:48px;align-items:flex-start}
  .contact-info h2{font-size:1.9rem;margin-bottom:14px}
  .contact-info p{color:var(--ink-soft);margin-bottom:20px}
  .contact-point{display:flex;gap:12px;align-items:flex-start;margin-bottom:16px}
  .contact-point .ico{
    width:36px;height:36px;border-radius:9px;background:#fff;border:1px solid var(--line);
    display:flex;align-items:center;justify-content:center;flex-shrink:0;
  }
  .contact-point strong{display:block;font-size:.92rem}
  .contact-point span{color:var(--ink-soft);font-size:.88rem}

  form{background:#fff;border:1px solid var(--line);border-radius:var(--radius);padding:32px;box-shadow:var(--shadow)}
  .field{margin-bottom:18px}
  .field label{display:block;font-size:.86rem;font-weight:600;margin-bottom:7px}
  .field input{
    width:100%;padding:12px 14px;border:1.5px solid var(--line);border-radius:9px;
    font-family:inherit;font-size:.96rem;background:var(--cream);
  }
  .field input:focus{outline:none;border-color:var(--teal)}
  .field-row{display:grid;grid-template-columns:1fr 1fr;gap:14px}
  .submit-btn{
    width:100%;background:var(--coral);color:#fff;border:none;padding:16px;
    border-radius:100px;font-weight:700;font-size:1rem;cursor:pointer;
    box-shadow:0 10px 24px -8px rgba(225,89,47,.55);transition:background .15s;
  }
  .submit-btn:hover{background:var(--coral-dark)}
  .form-note{font-size:.8rem;color:var(--ink-soft);text-align:center;margin-top:12px}
  input[name="_honey"]{display:none}

  footer{padding:36px 0;border-top:1px solid var(--line)}
  .footer-row{display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px;font-size:.85rem;color:var(--ink-soft)}

  @media (max-width: 860px){
    .hero-grid,.contact-grid,.zone{grid-template-columns:1fr}
    .hero-img{order:-1}
    .features,.steps{grid-template-columns:1fr}
    .hero h1{font-size:2.1rem}
    .field-row{grid-template-columns:1fr}
    section{padding:44px 0}
    .how{padding:8px 4px}
  }
```

- [ ] **Step 2: Create `robots.txt`** at repo root:

```
User-agent: *
Allow: /

Sitemap: https://a-louer.github.io/piscine-entretien-salon/sitemap.xml
```

- [ ] **Step 3: Create `merci.html`** at repo root:

```html
<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Merci — Piscine Nette Salon</title>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:wght@600&family=Inter:wght@400;600&display=swap" rel="stylesheet">
<style>
  :root{--ink:#1c2320;--cream:#fbf6ee;--teal:#0d5c56;--coral:#e1592f;--line:#e3dccb}
  *{box-sizing:border-box;margin:0;padding:0}
  body{
    font-family:'Inter',system-ui,sans-serif;background:var(--cream);color:var(--ink);
    min-height:100vh;display:flex;align-items:center;justify-content:center;padding:24px;
  }
  .card{
    background:#fff;border:1px solid var(--line);border-radius:20px;padding:48px 36px;
    max-width:440px;text-align:center;box-shadow:0 12px 32px -12px rgba(28,35,32,.18);
  }
  .check{
    width:56px;height:56px;border-radius:50%;background:var(--teal);color:#fff;
    display:flex;align-items:center;justify-content:center;font-size:1.6rem;margin:0 auto 20px;
  }
  h1{font-family:'Fraunces',serif;font-size:1.6rem;margin-bottom:12px}
  p{color:#4a534f;margin-bottom:24px;line-height:1.55}
  a{
    display:inline-block;background:var(--coral);color:#fff;text-decoration:none;
    padding:13px 26px;border-radius:100px;font-weight:600;font-size:.95rem;
  }
</style>
</head>
<body>
  <div class="card">
    <div class="check">✓</div>
    <h1>Demande bien reçue</h1>
    <p>Merci ! Vous serez recontacté sous 24h pour cerner votre besoin d'entretien et organiser une intervention.</p>
    <a href="/">Retour à l'accueil</a>
  </div>
</body>
</html>
```

- [ ] **Step 4: Create `scripts/villages.json`** with exactly this content:

```json
[
  {"name": "Pélissanne", "slug": "pelissanne", "intro": "Pélissanne, village au pied de la chaîne de la Trévaresse, à 5 minutes de Salon-de-Provence."},
  {"name": "Grans", "slug": "grans", "intro": "Grans, aux portes de la plaine de la Crau, à 7 km au sud-ouest de Salon-de-Provence."},
  {"name": "Lançon-Provence", "slug": "lancon-provence", "intro": "Lançon-Provence, aux portes de l'étang de Berre, à une quinzaine de kilomètres au nord-est de Salon-de-Provence."},
  {"name": "Eyguières", "slug": "eyguieres", "intro": "Eyguières, au pied du massif des Alpilles, à l'est de Salon-de-Provence."},
  {"name": "Miramas", "slug": "miramas", "intro": "Miramas, dans la plaine de la Crau, tout près de l'étang de Berre, à l'ouest de Salon-de-Provence."},
  {"name": "Berre-l'Étang", "slug": "berre-letang", "intro": "Berre-l'Étang, sur les rives de l'étang de Berre, au sud de Salon-de-Provence."},
  {"name": "La Barben", "slug": "la-barben", "intro": "La Barben, dans la vallée de la Touloubre, au sud-est de Salon-de-Provence."},
  {"name": "Alleins", "slug": "alleins", "intro": "Alleins, village perché dominant la vallée de la Durance, au nord de Salon-de-Provence."},
  {"name": "Aurons", "slug": "aurons", "intro": "Aurons, petit village rural sur le plateau au nord de Salon-de-Provence."},
  {"name": "Sénas", "slug": "senas", "intro": "Sénas, aux portes de la vallée de la Durance et des Alpilles, au nord-est de Salon-de-Provence."},
  {"name": "Charleval", "slug": "charleval", "intro": "Charleval, dans la vallée de la Durance, au nord-est de Salon-de-Provence."},
  {"name": "Lambesc", "slug": "lambesc", "intro": "Lambesc, au pied de la chaîne de la Trévaresse, entre Salon-de-Provence et Aix-en-Provence."},
  {"name": "La Fare-les-Oliviers", "slug": "la-fare-les-oliviers", "intro": "La Fare-les-Oliviers, réputée pour ses oliveraies, au sud-est de Salon-de-Provence."},
  {"name": "Velaux", "slug": "velaux", "intro": "Velaux, entre Salon-de-Provence et l'étang de Berre, sur les rives de l'Arc."}
]
```

- [ ] **Step 5: Create `scripts/image-manifest.json`** with exactly this content:

```json
[
  {"filename": "hero.jpg", "query": "swimming pool clean water sunny garden"},
  {"filename": "pelissanne.jpg", "query": "swimming pool maintenance provence house"},
  {"filename": "grans.jpg", "query": "swimming pool garden villa"},
  {"filename": "lancon-provence.jpg", "query": "swimming pool net skimmer blue water"},
  {"filename": "eyguieres.jpg", "query": "swimming pool countryside villa provence"},
  {"filename": "miramas.jpg", "query": "swimming pool cleaning pool net"},
  {"filename": "berre-letang.jpg", "query": "swimming pool sunny terrace"},
  {"filename": "la-barben.jpg", "query": "swimming pool villa garden provence"},
  {"filename": "alleins.jpg", "query": "swimming pool water clean blue sky"},
  {"filename": "aurons.jpg", "query": "swimming pool countryside house summer"},
  {"filename": "senas.jpg", "query": "swimming pool clean maintenance technician"},
  {"filename": "charleval.jpg", "query": "swimming pool villa summer relax"},
  {"filename": "lambesc.jpg", "query": "swimming pool provence house garden"},
  {"filename": "la-fare-les-oliviers.jpg", "query": "swimming pool olive trees villa"},
  {"filename": "velaux.jpg", "query": "swimming pool clean water house terrace"}
]
```

- [ ] **Step 6: Commit**

```bash
git add assets/style.css robots.txt merci.html scripts/villages.json scripts/image-manifest.json
git commit -m "chore: scaffold shared assets, village manifest, robots.txt, merci page"
```

---

### Task 2: Page content validator (TDD)

**Files:**
- Create: `scripts/validate_page.py`
- Test: `scripts/test_validate_page.py`

**Interfaces:**
- Consumes: the shape of `scripts/villages.json` from Task 1 (`[{"name": str, "slug": str, "intro": str}, ...]`), passed in as a Python list, not read from disk inside the pure function.
- Produces: `validate(html: str, page_slug: str | None, villages: list[dict], is_hub: bool = False) -> list[str]` — pure function returning a list of human-readable error strings (empty list = page passes). Consumed by every content task (4-9) to self-check pages before commit, and by Task 10's final audit.
- Produces: CLI entry point `python3 scripts/validate_page.py <path/to/index.html> [--hub]`, exit code 0 on pass / 1 on validation failure / 2 on usage error.

- [ ] **Step 1: Write the failing tests**

Create `scripts/test_validate_page.py`:

```python
import unittest

from validate_page import validate

VILLAGES = [
    {"name": "Pélissanne", "slug": "pelissanne", "intro": "Pélissanne, village au pied de la chaîne de la Trévaresse."},
    {"name": "Grans", "slug": "grans", "intro": "Grans, aux portes de la plaine de la Crau."},
    {"name": "Velaux", "slug": "velaux", "intro": "Velaux, sur les rives de l'Arc."},
]

VALID_VILLAGE_PAGE = """
<html><head><title>Entretien piscine Pélissanne</title>
<meta name="description" content="Devis gratuit à Pélissanne">
<link rel="canonical" href="https://a-louer.github.io/piscine-entretien-salon/pelissanne/">
<script type="application/ld+json">{"@type": "Service", "areaServed": {"name": "Pélissanne"}}</script>
</head><body>
Pélissanne, village au pied de la chaîne de la Trévaresse.
<form action="https://formsubmit.co/nicolas@noilhan.com" method="POST">
<input type="text" name="_honey" style="display:none">
</form>
<footer><a href="../">Salon-de-Provence</a> <a href="../grans/">Grans</a> <a href="../velaux/">Velaux</a></footer>
</body></html>
"""

VALID_HUB_PAGE = """
<html><head><title>Entretien piscine Salon-de-Provence</title>
<meta name="description" content="Devis gratuit à Salon-de-Provence">
<link rel="canonical" href="https://a-louer.github.io/piscine-entretien-salon/">
<script type="application/ld+json">{"@type": "Service", "areaServed": {"name": "Salon-de-Provence"}}</script>
</head><body>
<form action="https://formsubmit.co/nicolas@noilhan.com" method="POST">
<input type="text" name="_honey" style="display:none">
</form>
<footer><a href="pelissanne/">Pélissanne</a> <a href="grans/">Grans</a> <a href="velaux/">Velaux</a></footer>
</body></html>
"""


class ValidatePageTests(unittest.TestCase):
    def test_valid_village_page_passes(self):
        errors = validate(VALID_VILLAGE_PAGE, "pelissanne", VILLAGES, is_hub=False)
        self.assertEqual(errors, [])

    def test_valid_hub_page_passes(self):
        errors = validate(VALID_HUB_PAGE, None, VILLAGES, is_hub=True)
        self.assertEqual(errors, [])

    def test_missing_canonical_fails(self):
        html = VALID_VILLAGE_PAGE.replace('<link rel="canonical" href="https://a-louer.github.io/piscine-entretien-salon/pelissanne/">', "")
        errors = validate(html, "pelissanne", VILLAGES, is_hub=False)
        self.assertIn("Missing canonical link", errors)

    def test_price_symbol_fails(self):
        html = VALID_VILLAGE_PAGE.replace("<body>", "<body><p>20€ / mois</p>")
        errors = validate(html, "pelissanne", VILLAGES, is_hub=False)
        self.assertTrue(any("price" in e.lower() for e in errors))

    def test_missing_honeypot_fails(self):
        html = VALID_VILLAGE_PAGE.replace('<input type="text" name="_honey" style="display:none">', "")
        errors = validate(html, "pelissanne", VILLAGES, is_hub=False)
        self.assertIn("Missing honeypot anti-spam field", errors)

    def test_self_link_in_footer_fails(self):
        html = VALID_VILLAGE_PAGE.replace(
            '<footer><a href="../">Salon-de-Provence</a> <a href="../grans/">Grans</a> <a href="../velaux/">Velaux</a></footer>',
            '<footer><a href="../">Salon-de-Provence</a> <a href="../pelissanne/">Pélissanne</a> <a href="../grans/">Grans</a> <a href="../velaux/">Velaux</a></footer>',
        )
        errors = validate(html, "pelissanne", VILLAGES, is_hub=False)
        self.assertIn("Footer must not self-link to the current village's own page", errors)

    def test_insufficient_footer_links_fails(self):
        html = VALID_VILLAGE_PAGE.replace(
            '<footer><a href="../">Salon-de-Provence</a> <a href="../grans/">Grans</a> <a href="../velaux/">Velaux</a></footer>',
            '<footer><a href="../">Salon-de-Provence</a></footer>',
        )
        errors = validate(html, "pelissanne", VILLAGES, is_hub=False)
        self.assertTrue(any("Footer should link to" in e for e in errors))

    def test_missing_village_name_fails(self):
        html = VALID_VILLAGE_PAGE.replace("Pélissanne", "Nulle Part")
        errors = validate(html, "pelissanne", VILLAGES, is_hub=False)
        self.assertTrue(any("not found in page content" in e for e in errors))


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd scripts && python3 -m unittest test_validate_page.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'validate_page'` (the module doesn't exist yet).

- [ ] **Step 3: Write the implementation**

Create `scripts/validate_page.py`:

```python
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd scripts && python3 -m unittest test_validate_page.py -v`
Expected: all 8 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add scripts/validate_page.py scripts/test_validate_page.py
git commit -m "test: add page content validator with TDD coverage"
```

---

### Task 3: Source images from Pexels

**Files:**
- Create: `scripts/fetch_images.py`
- Create (generated by running the script): `assets/hero.jpg`, `assets/pelissanne.jpg`, `assets/grans.jpg`, `assets/lancon-provence.jpg`, `assets/eyguieres.jpg`, `assets/miramas.jpg`, `assets/berre-letang.jpg`, `assets/la-barben.jpg`, `assets/alleins.jpg`, `assets/aurons.jpg`, `assets/senas.jpg`, `assets/charleval.jpg`, `assets/lambesc.jpg`, `assets/la-fare-les-oliviers.jpg`, `assets/velaux.jpg`
- Create (generated): `assets/CREDITS.md`

**Interfaces:**
- Consumes: `scripts/image-manifest.json` from Task 1.
- Produces: 15 JPEG files under `assets/`, referenced by filename (e.g. `pelissanne.jpg`) in Tasks 4-9's `<img src="../assets/<filename>">` tags.

- [ ] **Step 1: Write `scripts/fetch_images.py`**

```python
#!/usr/bin/env python3
"""Fetch pool-themed stock photos from Pexels for Piscine Nette Salon."""
import json
import os
import sys
import time
import urllib.parse
import urllib.request

API_KEY = os.environ.get("PEXELS_API_KEY")
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MANIFEST_PATH = os.path.join(SCRIPT_DIR, "image-manifest.json")
ASSETS_DIR = os.path.join(SCRIPT_DIR, "..", "assets")
CREDITS_PATH = os.path.join(ASSETS_DIR, "CREDITS.md")

# Pexels sits behind Cloudflare, which blocks urllib's default
# "Python-urllib/x.y" User-Agent with a 403 — a browser-like UA is required
# for both the search API call and the image download itself.
BROWSER_UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"


def search_photo(query):
    url = "https://api.pexels.com/v1/search?" + urllib.parse.urlencode(
        {"query": query, "per_page": 5, "orientation": "landscape"}
    )
    req = urllib.request.Request(url, headers={"Authorization": API_KEY, "User-Agent": BROWSER_UA})
    with urllib.request.urlopen(req, timeout=20) as resp:
        data = json.load(resp)
    photos = data.get("photos", [])
    if not photos:
        raise RuntimeError(f"No Pexels results for query: {query}")
    return photos[0]


def download(url, dest_path):
    req = urllib.request.Request(url, headers={"User-Agent": BROWSER_UA})
    with urllib.request.urlopen(req, timeout=30) as resp, open(dest_path, "wb") as f:
        f.write(resp.read())


def main():
    if not API_KEY:
        print("ERROR: set PEXELS_API_KEY environment variable", file=sys.stderr)
        sys.exit(1)

    with open(MANIFEST_PATH, encoding="utf-8") as f:
        manifest = json.load(f)

    os.makedirs(ASSETS_DIR, exist_ok=True)
    credits_lines = ["# Image credits\n\n", "All photos from [Pexels](https://www.pexels.com), free to use.\n\n"]
    if os.path.exists(CREDITS_PATH):
        with open(CREDITS_PATH, encoding="utf-8") as f:
            existing = f.read()
    else:
        existing = ""

    for entry in manifest:
        dest = os.path.join(ASSETS_DIR, entry["filename"])
        if os.path.exists(dest):
            print(f"SKIP (already downloaded): {entry['filename']}")
            continue
        print(f"Searching: {entry['query']}")
        photo = search_photo(entry["query"])
        download(photo["src"]["large"], dest)
        credit_line = (
            f"- `{entry['filename']}` — photo by {photo['photographer']} "
            f"({photo['photographer_url']}) via Pexels: {photo['url']}\n"
        )
        credits_lines.append(credit_line)
        # Write credits immediately after each successful download (not only
        # at the end) so a partial run never loses attribution for the
        # images it did fetch.
        with open(CREDITS_PATH, "w", encoding="utf-8") as f:
            f.writelines(credits_lines)
        print(f"Saved: {dest}")
        time.sleep(1)


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Run the script**

Run: `PEXELS_API_KEY="1qQgxinQU2YOw3Txrho24yMCuwaHmOwNNiYLihVbTsIMSEuwxjYQEn9j" python3 scripts/fetch_images.py`
Expected: 15 `.jpg` files appear under `assets/`, plus `assets/CREDITS.md` listing all 15 with photographer attribution. If any query returns no results, adjust that one query string in `scripts/image-manifest.json` (keep it pool-themed and landscape-appropriate) and re-run — the script skips files that already exist, so it only retries the missing ones.

- [ ] **Step 3: Verify no image is a placeholder/broken file**

Run: `file assets/*.jpg | grep -v "JPEG image data"`
Expected: no output (every file is a real JPEG).

- [ ] **Step 4: Commit**

```bash
git add assets/*.jpg assets/CREDITS.md scripts/fetch_images.py
git commit -m "feat: source pool photos from Pexels for hub and all 14 villages"
```

---

### Task 4: Hub page (Salon-de-Provence)

**Files:**
- Create: `index.html`

**Interfaces:**
- Consumes: `assets/style.css` (Task 1), `assets/hero.jpg` (Task 3), `scripts/villages.json` for the footer link list (Task 1).
- Produces: the canonical URL `https://a-louer.github.io/piscine-entretien-salon/`, linked FROM every village page's footer as `../` (Tasks 5-9 depend on this existing at repo root).

- [ ] **Step 1: Create `index.html`** with exactly this content:

```html
<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Entretien de piscine à Salon-de-Provence | Devis gratuit — Piscine Nette Salon</title>
<meta name="description" content="Entretien régulier de piscine à Salon-de-Provence et alentours : équilibrage, nettoyage, hivernage. Devis gratuit sous 24h.">
<link rel="canonical" href="https://a-louer.github.io/piscine-entretien-salon/">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600;9..144,700&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="assets/style.css">
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Service",
  "serviceType": "Entretien de piscine",
  "name": "Piscine Nette Salon",
  "areaServed": {
    "@type": "City",
    "name": "Salon-de-Provence"
  },
  "provider": {
    "@type": "LocalBusiness",
    "name": "Piscine Nette Salon"
  }
}
</script>
</head>
<body>

<header>
  <div class="nav">
    <div class="brand"><span class="brand-dot"></span> Piscine Nette Salon</div>
    <a class="nav-cta" href="#contact">Devis gratuit</a>
  </div>
</header>

<div class="wrap">
  <section class="hero">
    <div class="hero-grid">
      <div>
        <span class="eyebrow">💧 Entretien de piscine à domicile</span>
        <h1>Un entretien de piscine <em>fiable et régulier</em>, sans avoir à y penser</h1>
        <p class="lead">Équilibrage chimique, nettoyage de la filtration, brossage et vacuité, remise en service et hivernage : votre piscine reste propre et sûre toute l'année. Intervention organisée sur Salon-de-Provence et les communes alentours.</p>
        <p style="color:var(--ink-soft);font-size:.92rem;margin:-14px 0 24px">Salon-de-Provence, ville-centre entre plaine de la Crau, étang de Berre et Alpilles — carrefour naturel du secteur.</p>
        <div class="hero-actions">
          <a class="btn-primary" href="#contact">Demander mon devis gratuit</a>
          <a class="btn-ghost" href="#comment">Comment ça marche</a>
        </div>
      </div>
      <div class="hero-img">
        <img src="assets/hero.jpg" alt="Piscine bien entretenue, eau claire, à Salon-de-Provence" loading="eager">
        <div class="hero-img-tag">Devis gratuit sous 24h</div>
      </div>
    </div>
  </section>

  <section id="pourquoi">
    <div class="section-head">
      <span class="kicker">Pourquoi déléguer l'entretien</span>
      <h2>Une piscine mal entretenue coûte plus cher à rattraper qu'à entretenir</h2>
    </div>
    <div class="features">
      <div class="feature-card">
        <div class="feature-icon">🧪</div>
        <h3>Eau équilibrée en permanence</h3>
        <p>pH, chlore ou sel : un contrôle régulier évite l'eau trouble, les algues et les irritations pour les baigneurs.</p>
      </div>
      <div class="feature-card">
        <div class="feature-icon">🧹</div>
        <h3>Filtration et parois nettoyées</h3>
        <p>Skimmers, préfiltre, ligne d'eau, fond du bassin : les gestes techniques faits au bon moment, sans y penser.</p>
      </div>
      <div class="feature-card">
        <div class="feature-icon">🗓️</div>
        <h3>Ouverture et hivernage inclus</h3>
        <p>Remise en service au printemps, hivernage à l'automne : les deux moments les plus techniques de l'année, pris en charge.</p>
      </div>
    </div>
  </section>

  <section id="comment">
    <div class="how wrap" style="padding:48px 40px">
      <div class="section-head">
        <span class="kicker">Comment ça marche</span>
        <h2>Trois étapes, un devis gratuit sous 24h</h2>
      </div>
      <div class="steps">
        <div class="step">
          <div class="step-num">1</div>
          <h3>Vous décrivez votre besoin</h3>
          <p>Nom, téléphone et type de piscine — 30 secondes suffisent.</p>
        </div>
        <div class="step">
          <div class="step-num">2</div>
          <h3>On vous recontacte pour cerner la demande</h3>
          <p>Quelques questions pour bien qualifier votre besoin d'entretien.</p>
        </div>
        <div class="step">
          <div class="step-num">3</div>
          <h3>Un professionnel qualifié intervient chez vous</h3>
          <p>Un prestataire du secteur prend le relais, au jour convenu.</p>
        </div>
      </div>
    </div>
  </section>

  <section id="zone">
    <div class="zone">
      <div>
        <div class="section-head" style="margin-bottom:0">
          <span class="kicker">Zone de service</span>
          <h2>Salon-de-Provence et communes alentours</h2>
        </div>
        <ul class="zone-list">
          <li>Salon-de-Provence</li>
          <li>Pélissanne</li>
          <li>Grans</li>
          <li>Lançon-Provence</li>
          <li>Eyguières</li>
          <li>Miramas</li>
          <li>Berre-l'Étang</li>
          <li>La Barben</li>
          <li>Alleins</li>
          <li>Aurons</li>
          <li>Sénas</li>
          <li>Charleval</li>
          <li>Lambesc</li>
          <li>La Fare-les-Oliviers</li>
          <li>Velaux</li>
        </ul>
        <p class="zone-note">Une autre commune proche ? Demandez au moment du rappel, c'est souvent possible.</p>
      </div>
      <div class="hero-img" style="aspect-ratio:1/1">
        <img src="assets/hero.jpg" alt="Entretien de piscine à domicile" loading="lazy">
      </div>
    </div>
  </section>

  <section id="contact">
    <div class="contact wrap" style="padding:48px 40px">
      <div class="contact-grid">
        <div class="contact-info">
          <h2>Demandez votre devis gratuit</h2>
          <p>Laissez vos coordonnées, vous êtes recontacté sous 24h pour cerner votre besoin et organiser une intervention.</p>
          <div class="contact-point">
            <div class="ico">📞</div>
            <div><strong>Réponse rapide</strong><span>Sous 24h, par téléphone</span></div>
          </div>
          <div class="contact-point">
            <div class="ico">📍</div>
            <div><strong>Intervention locale</strong><span>Salon-de-Provence et alentours</span></div>
          </div>
          <div class="contact-point">
            <div class="ico">✅</div>
            <div><strong>Devis gratuit</strong><span>Sans engagement</span></div>
          </div>
        </div>

        <form action="https://formsubmit.co/nicolas@noilhan.com" method="POST">
          <input type="hidden" name="_subject" value="Nouvelle demande de devis piscine — Salon-de-Provence">
          <input type="hidden" name="_template" value="table">
          <input type="hidden" name="_next" value="https://a-louer.github.io/piscine-entretien-salon/merci.html">
          <input type="text" name="_honey" style="display:none" tabindex="-1" autocomplete="off">

          <div class="field-row">
            <div class="field">
              <label for="nom">Nom</label>
              <input type="text" id="nom" name="Nom" required>
            </div>
            <div class="field">
              <label for="prenom">Prénom</label>
              <input type="text" id="prenom" name="Prénom" required>
            </div>
          </div>

          <div class="field-row">
            <div class="field">
              <label for="tel">Téléphone</label>
              <input type="tel" id="tel" name="Téléphone" placeholder="06 12 34 56 78" required>
            </div>
            <div class="field">
              <label for="besoin">Type de piscine / besoin</label>
              <input type="text" id="besoin" name="Type de piscine ou besoin" placeholder="Ex: piscine enterrée 8x4m">
            </div>
          </div>

          <button class="submit-btn" type="submit">Demander mon devis gratuit</button>
          <p class="form-note">Vos informations servent uniquement à organiser votre devis. Aucune donnée revendue.</p>
        </form>
      </div>
    </div>
  </section>
</div>

<footer>
  <div class="wrap">
    <div class="footer-row" style="margin-bottom:14px">
      <span>Piscine Nette Salon — Entretien de piscine</span>
      <span>Salon-de-Provence &amp; alentours</span>
    </div>
    <div class="footer-row">
      <span>Autres secteurs desservis :
        <a href="pelissanne/">Pélissanne</a> ·
        <a href="grans/">Grans</a> ·
        <a href="lancon-provence/">Lançon-Provence</a> ·
        <a href="eyguieres/">Eyguières</a> ·
        <a href="miramas/">Miramas</a> ·
        <a href="berre-letang/">Berre-l'Étang</a> ·
        <a href="la-barben/">La Barben</a> ·
        <a href="alleins/">Alleins</a> ·
        <a href="aurons/">Aurons</a> ·
        <a href="senas/">Sénas</a> ·
        <a href="charleval/">Charleval</a> ·
        <a href="lambesc/">Lambesc</a> ·
        <a href="la-fare-les-oliviers/">La Fare-les-Oliviers</a> ·
        <a href="velaux/">Velaux</a>
      </span>
    </div>
  </div>
</footer>

</body>
</html>
```

- [ ] **Step 2: Validate**

Run: `python3 scripts/validate_page.py index.html --hub`
Expected: `OK: index.html`

- [ ] **Step 3: Commit**

```bash
git add index.html
git commit -m "feat: add Salon-de-Provence hub page"
```

---

### Task 5: Village pages — batch A (Pélissanne, Grans, Lançon-Provence)

**Files:**
- Create: `pelissanne/index.html`
- Create: `grans/index.html`
- Create: `lancon-provence/index.html`

**Interfaces:**
- Consumes: the shared village-page template below, `scripts/villages.json` (exact `intro` text per village), `assets/style.css`, `assets/<slug>.jpg` from Task 3, `index.html` from Task 4 (footer must link back to it via `../`).
- Produces: three pages at `https://a-louer.github.io/piscine-entretien-salon/<slug>/`, each referenced from every other content page's footer (Tasks 4, 6-9 all link here).

**Shared village-page template** (used verbatim by this task and Tasks 6-9 — every `[TOKEN]` is replaced with the literal value from the table that follows; nothing here is a judgment call):

```html
<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Entretien de piscine à [VILLAGE] | Devis gratuit — Piscine Nette [VILLAGE]</title>
<meta name="description" content="Entretien régulier de piscine à [VILLAGE] : équilibrage, nettoyage, hivernage. Devis gratuit sous 24h, un professionnel qualifié du secteur intervient chez vous.">
<link rel="canonical" href="https://a-louer.github.io/piscine-entretien-salon/[SLUG]/">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600;9..144,700&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="../assets/style.css">
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Service",
  "serviceType": "Entretien de piscine",
  "name": "Piscine Nette [VILLAGE]",
  "areaServed": {
    "@type": "City",
    "name": "[VILLAGE]"
  },
  "provider": {
    "@type": "LocalBusiness",
    "name": "Piscine Nette [VILLAGE]"
  }
}
</script>
</head>
<body>

<header>
  <div class="nav">
    <div class="brand"><span class="brand-dot"></span> Piscine Nette [VILLAGE]</div>
    <a class="nav-cta" href="#contact">Devis gratuit</a>
  </div>
</header>

<div class="wrap">
  <section class="hero">
    <div class="hero-grid">
      <div>
        <span class="eyebrow">💧 Entretien de piscine à [VILLAGE]</span>
        <h1>Un entretien de piscine <em>fiable et régulier</em>, sans avoir à y penser</h1>
        <p class="lead">Équilibrage chimique, nettoyage de la filtration, brossage et vacuité, remise en service et hivernage : votre piscine reste propre et sûre toute l'année. Intervention organisée à [VILLAGE] et alentours.</p>
        <p style="color:var(--ink-soft);font-size:.92rem;margin:-14px 0 24px">[INTRO]</p>
        <div class="hero-actions">
          <a class="btn-primary" href="#contact">Demander mon devis gratuit</a>
          <a class="btn-ghost" href="#comment">Comment ça marche</a>
        </div>
      </div>
      <div class="hero-img">
        <img src="../assets/[IMAGE].jpg" alt="Piscine bien entretenue, eau claire, à [VILLAGE]" loading="eager">
        <div class="hero-img-tag">Devis gratuit sous 24h</div>
      </div>
    </div>
  </section>

  <section id="pourquoi">
    <div class="section-head">
      <span class="kicker">Pourquoi déléguer l'entretien</span>
      <h2>Une piscine mal entretenue coûte plus cher à rattraper qu'à entretenir</h2>
    </div>
    <div class="features">
      <div class="feature-card">
        <div class="feature-icon">🧪</div>
        <h3>Eau équilibrée en permanence</h3>
        <p>pH, chlore ou sel : un contrôle régulier évite l'eau trouble, les algues et les irritations pour les baigneurs.</p>
      </div>
      <div class="feature-card">
        <div class="feature-icon">🧹</div>
        <h3>Filtration et parois nettoyées</h3>
        <p>Skimmers, préfiltre, ligne d'eau, fond du bassin : les gestes techniques faits au bon moment, sans y penser.</p>
      </div>
      <div class="feature-card">
        <div class="feature-icon">🗓️</div>
        <h3>Ouverture et hivernage inclus</h3>
        <p>Remise en service au printemps, hivernage à l'automne : les deux moments les plus techniques de l'année, pris en charge.</p>
      </div>
    </div>
  </section>

  <section id="comment">
    <div class="how wrap" style="padding:48px 40px">
      <div class="section-head">
        <span class="kicker">Comment ça marche</span>
        <h2>Trois étapes, un devis gratuit sous 24h</h2>
      </div>
      <div class="steps">
        <div class="step">
          <div class="step-num">1</div>
          <h3>Vous décrivez votre besoin</h3>
          <p>Nom, téléphone et type de piscine — 30 secondes suffisent.</p>
        </div>
        <div class="step">
          <div class="step-num">2</div>
          <h3>On vous recontacte pour cerner la demande</h3>
          <p>Quelques questions pour bien qualifier votre besoin d'entretien.</p>
        </div>
        <div class="step">
          <div class="step-num">3</div>
          <h3>Un professionnel qualifié intervient chez vous</h3>
          <p>Un prestataire du secteur prend le relais, au jour convenu.</p>
        </div>
      </div>
    </div>
  </section>

  <section id="zone">
    <div class="zone">
      <div>
        <div class="section-head" style="margin-bottom:0">
          <span class="kicker">Zone de service</span>
          <h2>[VILLAGE] et communes alentours</h2>
        </div>
        <ul class="zone-list">
          <li>Salon-de-Provence</li>
          <li>Pélissanne</li>
          <li>Grans</li>
          <li>Lançon-Provence</li>
          <li>Eyguières</li>
          <li>Miramas</li>
          <li>Berre-l'Étang</li>
          <li>La Barben</li>
          <li>Alleins</li>
          <li>Aurons</li>
          <li>Sénas</li>
          <li>Charleval</li>
          <li>Lambesc</li>
          <li>La Fare-les-Oliviers</li>
          <li>Velaux</li>
        </ul>
        <p class="zone-note">Une autre commune proche ? Demandez au moment du rappel, c'est souvent possible.</p>
      </div>
      <div class="hero-img" style="aspect-ratio:1/1">
        <img src="../assets/[IMAGE].jpg" alt="Entretien de piscine à [VILLAGE]" loading="lazy">
      </div>
    </div>
  </section>

  <section id="contact">
    <div class="contact wrap" style="padding:48px 40px">
      <div class="contact-grid">
        <div class="contact-info">
          <h2>Demandez votre devis gratuit</h2>
          <p>Laissez vos coordonnées, vous êtes recontacté sous 24h pour cerner votre besoin et organiser une intervention.</p>
          <div class="contact-point">
            <div class="ico">📞</div>
            <div><strong>Réponse rapide</strong><span>Sous 24h, par téléphone</span></div>
          </div>
          <div class="contact-point">
            <div class="ico">📍</div>
            <div><strong>Intervention locale</strong><span>[VILLAGE] et alentours</span></div>
          </div>
          <div class="contact-point">
            <div class="ico">✅</div>
            <div><strong>Devis gratuit</strong><span>Sans engagement</span></div>
          </div>
        </div>

        <form action="https://formsubmit.co/nicolas@noilhan.com" method="POST">
          <input type="hidden" name="_subject" value="Nouvelle demande de devis piscine — [VILLAGE]">
          <input type="hidden" name="_template" value="table">
          <input type="hidden" name="_next" value="https://a-louer.github.io/piscine-entretien-salon/merci.html">
          <input type="text" name="_honey" style="display:none" tabindex="-1" autocomplete="off">

          <div class="field-row">
            <div class="field">
              <label for="nom">Nom</label>
              <input type="text" id="nom" name="Nom" required>
            </div>
            <div class="field">
              <label for="prenom">Prénom</label>
              <input type="text" id="prenom" name="Prénom" required>
            </div>
          </div>

          <div class="field-row">
            <div class="field">
              <label for="tel">Téléphone</label>
              <input type="tel" id="tel" name="Téléphone" placeholder="06 12 34 56 78" required>
            </div>
            <div class="field">
              <label for="besoin">Type de piscine / besoin</label>
              <input type="text" id="besoin" name="Type de piscine ou besoin" placeholder="Ex: piscine enterrée 8x4m">
            </div>
          </div>

          <button class="submit-btn" type="submit">Demander mon devis gratuit</button>
          <p class="form-note">Vos informations servent uniquement à organiser votre devis. Aucune donnée revendue.</p>
        </form>
      </div>
    </div>
  </section>
</div>

<footer>
  <div class="wrap">
    <div class="footer-row" style="margin-bottom:14px">
      <span>Piscine Nette [VILLAGE] — Entretien de piscine</span>
      <span>[VILLAGE] &amp; alentours</span>
    </div>
    <div class="footer-row">
      <span>Autres secteurs desservis :
        [FOOTER_LINKS]
      </span>
    </div>
  </div>
</footer>

</body>
</html>
```

**Substitution rule for `[FOOTER_LINKS]`:** always `<a href="../">Salon-de-Provence</a> ·` followed by `<a href="../<slug>/"><Name></a> ·` for every village in `scripts/villages.json` **except the current page's own village**, joined with ` · ` (no trailing `·` after the last one). This is the fix noted in Global Constraints — do not include the current village in its own "autres secteurs" list.

**Substitution table for this task's 3 pages:**

| File | `[VILLAGE]` | `[SLUG]` | `[INTRO]` | `[IMAGE]` |
|---|---|---|---|---|
| `pelissanne/index.html` | Pélissanne | pelissanne | Pélissanne, village au pied de la chaîne de la Trévaresse, à 5 minutes de Salon-de-Provence. | pelissanne |
| `grans/index.html` | Grans | grans | Grans, aux portes de la plaine de la Crau, à 7 km au sud-ouest de Salon-de-Provence. | grans |
| `lancon-provence/index.html` | Lançon-Provence | lancon-provence | Lançon-Provence, aux portes de l'étang de Berre, à une quinzaine de kilomètres au nord-est de Salon-de-Provence. | lancon-provence |

- [ ] **Step 1: Create the 3 files** by copying the shared template above and substituting the table's values (including the `[FOOTER_LINKS]` rule) for each of `pelissanne/index.html`, `grans/index.html`, `lancon-provence/index.html`.

- [ ] **Step 2: Validate all 3**

Run:
```bash
python3 scripts/validate_page.py pelissanne/index.html
python3 scripts/validate_page.py grans/index.html
python3 scripts/validate_page.py lancon-provence/index.html
```
Expected: `OK: <path>` for all three. If a footer-link-count error appears, it means `[FOOTER_LINKS]` was built from the full 14-village list instead of the 13-village "all except self" list — recount and fix.

- [ ] **Step 3: Commit**

```bash
git add pelissanne/ grans/ lancon-provence/
git commit -m "feat: add village pages for Pélissanne, Grans, Lançon-Provence"
```

---

### Task 6: Village pages — batch B (Eyguières, Miramas, Berre-l'Étang)

**Files:**
- Create: `eyguieres/index.html`
- Create: `miramas/index.html`
- Create: `berre-letang/index.html`

**Interfaces:**
- Consumes: the same shared village-page template from Task 5 (reproduced there in full — reuse it verbatim, only the substitution values differ) and the `[FOOTER_LINKS]` substitution rule from Task 5.
- Produces: three more pages in the footer mesh that Task 4, 5, 7, 8, 9 all link to.

**Substitution table:**

| File | `[VILLAGE]` | `[SLUG]` | `[INTRO]` | `[IMAGE]` |
|---|---|---|---|---|
| `eyguieres/index.html` | Eyguières | eyguieres | Eyguières, au pied du massif des Alpilles, à l'est de Salon-de-Provence. | eyguieres |
| `miramas/index.html` | Miramas | miramas | Miramas, dans la plaine de la Crau, tout près de l'étang de Berre, à l'ouest de Salon-de-Provence. | miramas |
| `berre-letang/index.html` | Berre-l'Étang | berre-letang | Berre-l'Étang, sur les rives de l'étang de Berre, au sud de Salon-de-Provence. | berre-letang |

- [ ] **Step 1: Create the 3 files** using Task 5's shared template, substituting this task's table values (and building `[FOOTER_LINKS]` per Task 5's rule: all 14 villages except the current one, plus the hub link).

- [ ] **Step 2: Validate all 3**

Run:
```bash
python3 scripts/validate_page.py eyguieres/index.html
python3 scripts/validate_page.py miramas/index.html
python3 scripts/validate_page.py berre-letang/index.html
```
Expected: `OK: <path>` for all three.

- [ ] **Step 3: Commit**

```bash
git add eyguieres/ miramas/ berre-letang/
git commit -m "feat: add village pages for Eyguières, Miramas, Berre-l'Étang"
```

---

### Task 7: Village pages — batch C (La Barben, Alleins, Aurons)

**Files:**
- Create: `la-barben/index.html`
- Create: `alleins/index.html`
- Create: `aurons/index.html`

**Interfaces:**
- Consumes: the same shared village-page template and `[FOOTER_LINKS]` rule from Task 5.
- Produces: three more pages in the footer mesh.

**Substitution table:**

| File | `[VILLAGE]` | `[SLUG]` | `[INTRO]` | `[IMAGE]` |
|---|---|---|---|---|
| `la-barben/index.html` | La Barben | la-barben | La Barben, dans la vallée de la Touloubre, au sud-est de Salon-de-Provence. | la-barben |
| `alleins/index.html` | Alleins | alleins | Alleins, village perché dominant la vallée de la Durance, au nord de Salon-de-Provence. | alleins |
| `aurons/index.html` | Aurons | aurons | Aurons, petit village rural sur le plateau au nord de Salon-de-Provence. | aurons |

- [ ] **Step 1: Create the 3 files** using Task 5's shared template and `[FOOTER_LINKS]` rule with this task's table values.

- [ ] **Step 2: Validate all 3**

Run:
```bash
python3 scripts/validate_page.py la-barben/index.html
python3 scripts/validate_page.py alleins/index.html
python3 scripts/validate_page.py aurons/index.html
```
Expected: `OK: <path>` for all three.

- [ ] **Step 3: Commit**

```bash
git add la-barben/ alleins/ aurons/
git commit -m "feat: add village pages for La Barben, Alleins, Aurons"
```

---

### Task 8: Village pages — batch D (Sénas, Charleval, Lambesc)

**Files:**
- Create: `senas/index.html`
- Create: `charleval/index.html`
- Create: `lambesc/index.html`

**Interfaces:**
- Consumes: the same shared village-page template and `[FOOTER_LINKS]` rule from Task 5.
- Produces: three more pages in the footer mesh.

**Substitution table:**

| File | `[VILLAGE]` | `[SLUG]` | `[INTRO]` | `[IMAGE]` |
|---|---|---|---|---|
| `senas/index.html` | Sénas | senas | Sénas, aux portes de la vallée de la Durance et des Alpilles, au nord-est de Salon-de-Provence. | senas |
| `charleval/index.html` | Charleval | charleval | Charleval, dans la vallée de la Durance, au nord-est de Salon-de-Provence. | charleval |
| `lambesc/index.html` | Lambesc | lambesc | Lambesc, au pied de la chaîne de la Trévaresse, entre Salon-de-Provence et Aix-en-Provence. | lambesc |

- [ ] **Step 1: Create the 3 files** using Task 5's shared template and `[FOOTER_LINKS]` rule with this task's table values.

- [ ] **Step 2: Validate all 3**

Run:
```bash
python3 scripts/validate_page.py senas/index.html
python3 scripts/validate_page.py charleval/index.html
python3 scripts/validate_page.py lambesc/index.html
```
Expected: `OK: <path>` for all three.

- [ ] **Step 3: Commit**

```bash
git add senas/ charleval/ lambesc/
git commit -m "feat: add village pages for Sénas, Charleval, Lambesc"
```

---

### Task 9: Village pages — batch E (La Fare-les-Oliviers, Velaux)

**Files:**
- Create: `la-fare-les-oliviers/index.html`
- Create: `velaux/index.html`

**Interfaces:**
- Consumes: the same shared village-page template and `[FOOTER_LINKS]` rule from Task 5.
- Produces: the last two pages in the footer mesh — after this task, all 14 village pages + hub exist.

**Substitution table:**

| File | `[VILLAGE]` | `[SLUG]` | `[INTRO]` | `[IMAGE]` |
|---|---|---|---|---|
| `la-fare-les-oliviers/index.html` | La Fare-les-Oliviers | la-fare-les-oliviers | La Fare-les-Oliviers, réputée pour ses oliveraies, au sud-est de Salon-de-Provence. | la-fare-les-oliviers |
| `velaux/index.html` | Velaux | velaux | Velaux, entre Salon-de-Provence et l'étang de Berre, sur les rives de l'Arc. | velaux |

- [ ] **Step 1: Create the 2 files** using Task 5's shared template and `[FOOTER_LINKS]` rule with this task's table values.

- [ ] **Step 2: Validate both**

Run:
```bash
python3 scripts/validate_page.py la-fare-les-oliviers/index.html
python3 scripts/validate_page.py velaux/index.html
```
Expected: `OK: <path>` for both.

- [ ] **Step 3: Commit**

```bash
git add la-fare-les-oliviers/ velaux/
git commit -m "feat: add village pages for La Fare-les-Oliviers, Velaux"
```

---

### Task 10: Sitemap, full-site audit, and GitHub Pages deployment

**Files:**
- Create: `sitemap.xml`
- Test: none new — this task runs the Task 2 validator across every page as its test.

**Interfaces:**
- Consumes: every page created in Tasks 4-9, plus `scripts/validate_page.py` from Task 2.
- Produces: a live site at `https://a-louer.github.io/piscine-entretien-salon/`.

- [ ] **Step 1: Create `sitemap.xml`** at repo root:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>https://a-louer.github.io/piscine-entretien-salon/</loc></url>
  <url><loc>https://a-louer.github.io/piscine-entretien-salon/pelissanne/</loc></url>
  <url><loc>https://a-louer.github.io/piscine-entretien-salon/grans/</loc></url>
  <url><loc>https://a-louer.github.io/piscine-entretien-salon/lancon-provence/</loc></url>
  <url><loc>https://a-louer.github.io/piscine-entretien-salon/eyguieres/</loc></url>
  <url><loc>https://a-louer.github.io/piscine-entretien-salon/miramas/</loc></url>
  <url><loc>https://a-louer.github.io/piscine-entretien-salon/berre-letang/</loc></url>
  <url><loc>https://a-louer.github.io/piscine-entretien-salon/la-barben/</loc></url>
  <url><loc>https://a-louer.github.io/piscine-entretien-salon/alleins/</loc></url>
  <url><loc>https://a-louer.github.io/piscine-entretien-salon/aurons/</loc></url>
  <url><loc>https://a-louer.github.io/piscine-entretien-salon/senas/</loc></url>
  <url><loc>https://a-louer.github.io/piscine-entretien-salon/charleval/</loc></url>
  <url><loc>https://a-louer.github.io/piscine-entretien-salon/lambesc/</loc></url>
  <url><loc>https://a-louer.github.io/piscine-entretien-salon/la-fare-les-oliviers/</loc></url>
  <url><loc>https://a-louer.github.io/piscine-entretien-salon/velaux/</loc></url>
</urlset>
```

- [ ] **Step 2: Run the validator across every content page**

Run:
```bash
python3 scripts/validate_page.py index.html --hub
for d in pelissanne grans lancon-provence eyguieres miramas berre-letang la-barben alleins aurons senas charleval lambesc la-fare-les-oliviers velaux; do
  python3 scripts/validate_page.py "$d/index.html"
done
```
Expected: `OK:` for all 15 pages, no `FAIL:` lines. Fix any failure by re-checking that page's substitution values against its table entry in Tasks 5-9 before proceeding.

- [ ] **Step 3: Confirm the full footer mesh**

Run: `grep -rL "villages.json" --include=index.html . | wc -l` is not a meaningful check by itself; instead confirm every page's footer link count matches expectations already enforced by Step 2's validator run (which checks this per page) — no separate step needed beyond re-running Step 2 clean.

- [ ] **Step 4: Commit the sitemap**

```bash
git add sitemap.xml
git commit -m "chore: add sitemap.xml for all 15 pages"
```

- [ ] **Step 5: Push and enable GitHub Pages**

```bash
git push -u origin main
gh api repos/a-louer/piscine-entretien-salon/pages -X POST -f "source[branch]=main" -f "source[path]=/" 2>&1 || \
gh api repos/a-louer/piscine-entretien-salon/pages -X PUT -f "source[branch]=main" -f "source[path]=/"
```

Note: the `POST` creates the Pages site if it doesn't exist yet; if it already exists, `POST` fails and the `PUT` fallback updates its source branch/path instead — the `||` handles either starting state.

- [ ] **Step 6: Verify the live site**

Run: `sleep 30 && curl -s -o /dev/null -w "%{http_code}\n" https://a-louer.github.io/piscine-entretien-salon/`
Expected: `200` (GitHub Pages builds typically finish within 30-60s; if it prints something else, wait longer and retry rather than treating it as a failure).

Run: `curl -s -o /dev/null -w "%{http_code}\n" https://a-louer.github.io/piscine-entretien-salon/pelissanne/`
Expected: `200`.
