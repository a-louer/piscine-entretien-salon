# Piscine Nette Salon — Design

**Goal:** A lead-generation static site for pool maintenance around Salon-de-Provence, on the same proven model as `a-louer/karcher-k7-salon` and `NicoNoilhan/bissell-location-salon`, pushed further on local SEO (15 village pages instead of 4).

**Why:** Nicolas runs a small factory of local lead-gen sites (rent Bissell carpet cleaner, rent Kärcher pressure washer). This is the third vertical: a pool-maintenance subscription service. He collects the leads himself and routes them to real professionals afterward — the site must never claim a specific company performs the work. This spec also locks in the template so future verticals (chimney sweeping, AC installation, garden creation, mandatory brush-clearing, tree pruning, etc. — see idea list from brainstorming) can reuse it directly.

## Repo & hosting

- `a-louer/piscine-entretien-salon` (created), static HTML/CSS, no build step, no JS framework — identical stack to the two existing sites.
- GitHub Pages, branch `master`, root path, no custom domain: `https://a-louer.github.io/piscine-entretien-salon/`.
- `assets/style.css` is copied byte-for-byte from `karcher-k7-salon` (same palette: teal `#0d5c56` / coral `#e1592f` / cream `#fbf6ee`, Fraunces + Inter fonts). No visual changes — confirmed with Nicolas: one shared template across all verticals, content-only differentiation.

## Pages

Hub + 15 village pages, each in its own directory (`<slug>/index.html`), mirroring the existing `pelissanne/`, `grans/` pattern:

| Village | Slug |
|---|---|
| Salon-de-Provence (hub) | `/` (root `index.html`) |
| Pélissanne | `pelissanne/` |
| Grans | `grans/` |
| Lançon-Provence | `lancon-provence/` |
| Eyguières | `eyguieres/` |
| Miramas | `miramas/` |
| Berre-l'Étang | `berre-letang/` |
| La Barben | `la-barben/` |
| Alleins | `alleins/` |
| Aurons | `aurons/` |
| Sénas | `senas/` |
| Charleval | `charleval/` |
| Lambesc | `lambesc/` |
| La Fare-les-Oliviers | `la-fare-les-oliviers/` |
| Velaux | `velaux/` |
| `merci.html` | thank-you page after form submit |

Every page's footer links to every other page (full internal mesh, matching the existing pattern) — with 16 pages this list is long but is standard practice for local-SEO mesh linking.

## SEO strategy (the point Nicolas wants pushed hardest)

The existing sites' village pages are near-duplicates of each other (village name swapped, otherwise identical copy) — a known weak point for local ranking. This site goes further:

- **Unique local intro per village**: one sentence anchoring the page geographically, using only well-established, safe-to-state regional landmarks (Alpilles, Étang de Berre, Chaîne de la Trévaresse, Plaine de la Crau, cardinal direction and approximate distance from Salon-de-Provence). No invented or unverifiable hyper-local trivia (specific monuments, population figures, business names) — geographic anchoring only, kept factually conservative.
- **JSON-LD structured data** (`schema.org` `LocalBusiness` + `Service`) embedded on every page, naming the village as `areaServed`.
- **Unique `<title>` and meta description per page**, including village name and "devis gratuit" (already the pattern; kept).
- **`sitemap.xml`** listing all 16 URLs and **`robots.txt`** allowing full crawl, both at repo root.
- **`<link rel="canonical">`** per page (existing pattern, kept).

## Content & conversion

- No prices shown anywhere on the site (decided over the jules-piscines.fr reference model, which shows full pricing tables) — every page's only CTA is a free-quote request: "Devis gratuit sous 24h".
- Brand: **Piscine Nette Salon**, declined per village in the header (e.g. "Piscine Nette Pélissanne"), same pattern as "SpotClean Pélissanne" / "Kärcher K7 Salon-de-Provence".
- Service description (generic, not tied to a specific company): regular maintenance visits — chemical balance, filtration cleaning, brushing/vacuuming, seasonal opening ("remise en service") and closing ("hivernage"). No specific visit counts or formulas (unlike jules-piscines' 5-tier model) — kept intentionally vague since there's no real subscription being sold on the page itself.
- **"Comment ça marche" reworded to stay honest about Nicolas's intermediary role** (he collects the lead and calls back to qualify it, before handing off to a real local professional — the copy must never claim to be that professional):
  1. Vous décrivez votre besoin (formulaire, 30 secondes)
  2. On vous recontacte pour cerner la demande
  3. Un professionnel qualifié du secteur intervient chez vous
- Lead form: same `formsubmit.co` POST mechanism as the existing sites, honeypot field kept, one form field set per page (nom/prénom/téléphone + a short text field for "type de piscine ou besoin" since there's no date-of-rental equivalent here), `_subject` includes the village name, redirects to `merci.html`.

## Images

16 pool photos (1 hero + 1 per village) sourced from the Pexels API (same key already used for the Bob comic project), matching the existing sites' approach of one hero-style photo per page.

## Reusability note

This repo's structure (village-mesh SEO, JSON-LD, sitemap/robots, honest-intermediary copy pattern) becomes the reference template for the other verticals identified in brainstorming (chimney sweeping, mandatory brush-clearing, AC installation/maintenance, garden creation, tree pruning, roof demossing, window cleaning, emergency locksmith, pest control, heat-pump maintenance, motorized shutter installation) — each gets its own repo under `a-louer`, copying this site's `style.css`, sitemap/robots/JSON-LD approach, and the three-step honest-intermediary copy pattern, with only the service description, brand name, and images changed.
