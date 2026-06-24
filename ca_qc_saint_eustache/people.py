import re

from utils import CanadianPerson as Person
from utils import CanadianScraper

COUNCIL_URL = "https://www.saint-eustache.ca/ville/vie-democratique/conseil-municipal"


class SaintEustachePersonScraper(CanadianScraper):
    def scrape(self):
        page = self.lxmlize(COUNCIL_URL)
        h3_nodes = page.xpath("//main//h3")
        assert h3_nodes, "No member h3 found"
        for h3 in h3_nodes:
            name = h3.text_content().strip()
            if not name:
                continue
            preceding_h2 = h3.xpath("preceding::h2[1]")
            h2_text = preceding_h2[0].text_content().strip() if preceding_h2 else ""
            if "Maire" in h2_text or "Mayor" in h2_text:
                role, district = "Mayor", "Saint-Eustache"
            else:
                m = re.search(r"District\s+(\d+)", h2_text, re.I)
                if not m:
                    continue
                role, district = "Councillor", f"District {int(m.group(1))}"
            parent = h3.getparent()
            email = self.get_email(parent, error=False)
            phone_link = parent.xpath('.//a[starts-with(@href,"tel:")]')
            phone = phone_link[0].text_content().strip() if phone_link else None
            image = parent.xpath(".//img/@src")
            p = Person(primary_org="legislature", name=name, district=district, role=role)
            p.add_source(COUNCIL_URL)
            if email:
                p.add_contact("email", email)
            if phone:
                p.add_contact("voice", phone, "legislature")
            if image:
                p.image = image[0]
            yield p
