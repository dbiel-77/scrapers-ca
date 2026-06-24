import re

from utils import CanadianPerson as Person
from utils import CanadianScraper

MAYOR_URL = "https://www.ville.sorel-tracy.qc.ca/ville/vos-elus/maire"
COUNCIL_URL = "https://www.ville.sorel-tracy.qc.ca/ville/vos-elus/conseillers-et-conseilleres"


class SorelTracyPersonScraper(CanadianScraper):
    def scrape(self):
        # Mayor
        mpage = self.lxmlize(MAYOR_URL)
        name_h1 = mpage.xpath("//h1")
        name = name_h1[0].text_content().strip() if name_h1 else ""
        assert name, "Mayor name not found"
        email_a = mpage.xpath('.//a[starts-with(@href,"mailto:")]')
        email = email_a[0].get("href").replace("mailto:", "") if email_a else None
        phone_link = mpage.xpath('.//a[starts-with(@href,"tel:")]')
        phone = phone_link[0].text_content().strip() if phone_link else None
        p = Person(primary_org="legislature", name=name, district="Sorel-Tracy", role="Mayor")
        p.add_source(MAYOR_URL)
        if email:
            p.add_contact("email", email)
        if phone:
            p.add_contact("voice", phone, "legislature")
        yield p

        # Councillors
        cpage = self.lxmlize(COUNCIL_URL)
        h4_nodes = cpage.xpath('//h4[contains(., "M.") or contains(., "Mme")]')
        assert h4_nodes, "No councillor h4 found"
        for h4 in h4_nodes:
            name = re.sub(r"^(M\.|Mme\.?)\s*", "", h4.text_content().strip()).strip()
            if not name:
                continue
            preceding_h3 = h4.xpath("preceding::h3[1]")
            if not preceding_h3:
                continue
            m = re.search(r"n[°o]?\s*(\d+)", preceding_h3[0].text_content(), re.I)
            if not m:
                continue
            district = f"District {int(m.group(1))}"
            block = h4.getparent()
            email_a = block.xpath('.//a[starts-with(@href,"mailto:")]')
            email = email_a[0].get("href").replace("mailto:", "") if email_a else None
            phone_link = block.xpath('.//a[starts-with(@href,"tel:")]')
            phone = phone_link[0].text_content().strip() if phone_link else None
            image = block.xpath(".//img/@src")
            p = Person(
                primary_org="legislature", name=name, district=district, role="Councillor"
            )
            p.add_source(COUNCIL_URL)
            if email:
                p.add_contact("email", email)
            if phone:
                p.add_contact("voice", phone, "legislature")
            if image:
                p.image = image[0]
            yield p
