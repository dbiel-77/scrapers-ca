from utils import CanadianPerson as Person
from utils import CanadianScraper

LISTING_URL = "https://ville.vaudreuil-dorion.qc.ca/fr/la-ville/conseil-municipal/maire-et-conseillers-municipaux"
BASE = "https://ville.vaudreuil-dorion.qc.ca"


class VaudreuilDorionPersonScraper(CanadianScraper):
    def scrape(self):
        page = self.lxmlize(LISTING_URL)
        cards = page.xpath('//a[.//h3 and .//p and starts-with(@href, "/fr/")]')
        assert cards, "No member cards found"
        for card in cards:
            num_div = card.xpath('.//div[translate(normalize-space(.), "0123456789", "") = ""]')
            num = int(num_div[0].text_content().strip()) if num_div else None
            district_p = card.xpath(".//p")
            district_text = district_p[0].text_content().strip() if district_p else ""
            href = card.get("href")
            profile_url = BASE + href if not href.startswith("http") else href
            ppage = self.lxmlize(profile_url)
            name_h = ppage.xpath("//h1")
            name = name_h[0].text_content().strip() if name_h else ""
            if not name:
                continue
            if num is None or "aire" in district_text.lower():
                role, district = "Mayor", "Vaudreuil-Dorion"
            else:
                role, district = "Councillor", f"District {num}"
            email_el = ppage.xpath('.//a[starts-with(@href,"mailto:")]')
            email = email_el[0].get("href").replace("mailto:", "") if email_el else None
            image = ppage.xpath(
                '//img[contains(@src,"/sites/default/") or contains(@src,"/media/")]/@src'
            )
            p = Person(primary_org="legislature", name=name, district=district, role=role)
            p.add_source(LISTING_URL)
            p.add_source(profile_url)
            if email:
                p.add_contact("email", email)
            if image:
                p.image = image[0]
            yield p
