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
<h3>On vous recontacte pour cerner la demande</h3>
<h3>Un professionnel qualifié intervient chez vous</h3>
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
<h3>On vous recontacte pour cerner la demande</h3>
<h3>Un professionnel qualifié intervient chez vous</h3>
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

    def test_missing_title_fails(self):
        html = VALID_VILLAGE_PAGE.replace("<title>Entretien piscine Pélissanne</title>", "")
        errors = validate(html, "pelissanne", VILLAGES, is_hub=False)
        self.assertIn("Missing <title> tag", errors)

    def test_missing_meta_description_fails(self):
        html = VALID_VILLAGE_PAGE.replace('<meta name="description" content="Devis gratuit à Pélissanne">', "")
        errors = validate(html, "pelissanne", VILLAGES, is_hub=False)
        self.assertIn("Missing meta description", errors)

    def test_missing_json_ld_fails(self):
        html = VALID_VILLAGE_PAGE.replace(
            '<script type="application/ld+json">{"@type": "Service", "areaServed": {"name": "Pélissanne"}}</script>',
            "",
        )
        errors = validate(html, "pelissanne", VILLAGES, is_hub=False)
        self.assertIn("Missing JSON-LD Service structured data", errors)

    def test_missing_form_fails(self):
        html = VALID_VILLAGE_PAGE.replace(
            '<form action="https://formsubmit.co/nicolas@noilhan.com" method="POST">\n'
            '<input type="text" name="_honey" style="display:none">\n'
            "</form>",
            "",
        )
        errors = validate(html, "pelissanne", VILLAGES, is_hub=False)
        self.assertIn("Missing formsubmit.co lead form", errors)

    def test_step3_copy_present_passes(self):
        errors = validate(VALID_VILLAGE_PAGE, "pelissanne", VILLAGES, is_hub=False)
        self.assertNotIn("Missing or altered honest-intermediary step 3 copy", errors)

    def test_step3_copy_altered_fails(self):
        html = VALID_VILLAGE_PAGE.replace(
            "<h3>Un professionnel qualifié intervient chez vous</h3>",
            "<h3>Un professionnel qualifié du secteur intervient chez vous</h3>",
        )
        errors = validate(html, "pelissanne", VILLAGES, is_hub=False)
        self.assertIn("Missing or altered honest-intermediary step 3 copy", errors)

    def test_area_served_matches_village_passes(self):
        errors = validate(VALID_VILLAGE_PAGE, "pelissanne", VILLAGES, is_hub=False)
        self.assertNotIn(
            "JSON-LD areaServed block does not contain village name 'Pélissanne'", errors
        )

    def test_area_served_wrong_village_fails(self):
        # The JSON-LD block names a different village than page_slug, even
        # though the correct village name still appears elsewhere in the body.
        html = VALID_VILLAGE_PAGE.replace(
            '<script type="application/ld+json">{"@type": "Service", "areaServed": {"name": "Pélissanne"}}</script>',
            '<script type="application/ld+json">{"@type": "Service", "areaServed": {"name": "Grans"}}</script>',
        )
        errors = validate(html, "pelissanne", VILLAGES, is_hub=False)
        self.assertIn(
            "JSON-LD areaServed block does not contain village name 'Pélissanne'", errors
        )


if __name__ == "__main__":
    unittest.main()
