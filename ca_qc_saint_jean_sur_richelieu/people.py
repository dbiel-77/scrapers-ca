import re
from urllib.parse import urljoin

from utils import CanadianPerson as Person
from utils import CanadianScraper

COUNCIL_PAGE = "https://sjsr.ca/conseil-municipal/"
BASE_URL = "https://sjsr.ca"


class SaintJeanSurRichelieuPersonScraper(CanadianScraper):
    def scrape(self):
        page = self.lxmlize(COUNCIL_PAGE, encoding="utf-8")

        # Councillor links appear twice each (image + name), so deduplicate
        all_links = page.xpath(
            '//a[contains(@href, "/conseil-municipal/") or contains(@href, "/maire/")]/@href'
        )
        seen = set()
        councillors = []
        for link in all_links:
            # Exclude the main conseil-municipal listing page itself
            if link.rstrip("/").endswith("/conseil-municipal"):
                continue
            if link not in seen:
                seen.add(link)
                councillors.append(link)

        assert len(councillors), "No councillors found"

        for href in councillors:
            url = urljoin(BASE_URL, href)

            if "/maire" in href:
                role = "Maire"
                district = "Saint-Jean-sur-Richelieu"
            else:
                role = "Conseiller"
                district = None

            node = self.lxmlize(url)

            if role == "Maire":
                # Mayor page: h1="Mairie", name is in h2
                name_nodes = node.xpath("//h2")
                name = name_nodes[0].text_content().strip() if name_nodes else ""
            else:
                # Councillor page: h1 contains the name
                name_nodes = node.xpath("//h1")
                name = name_nodes[0].text_content().strip() if name_nodes else ""

            # For councillors, district is in h2[@class="entry-title"]
            # e.g. "Conseillère municipale du district 1"
            if role == "Conseiller":
                entry_title_nodes = node.xpath('//h2[@class="entry-title"]')
                if entry_title_nodes:
                    district_text = entry_title_nodes[0].text_content().strip()
                    m = re.search(r"district\s+(\d+)", district_text, re.IGNORECASE)
                    district = f"District {m.group(1)}" if m else district_text
                if not district:
                    district = "Saint-Jean-sur-Richelieu"

            # Photo: try Beaver Builder class first, then any WordPress upload img
            photo_nodes = node.xpath('//div[@class="fl-photo-content fl-photo-img-jpg"]//img/@src')
            if not photo_nodes:
                photo_nodes = node.xpath('//img[contains(@src, "wp-content/uploads")]/@src')
            photo_url = urljoin(url, photo_nodes[0]) if photo_nodes else None

            p = Person(primary_org="legislature", name=name, district=district, role=role)
            p.add_source(COUNCIL_PAGE)
            p.add_source(url)
            if photo_url:
                p.image = photo_url

            voice = self.get_phone(node, error=False)
            if voice:
                p.add_contact("voice", voice, "legislature")

            yield p
