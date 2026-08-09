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
