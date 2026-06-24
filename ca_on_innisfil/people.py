import re

from utils import CanadianPerson as Person
from utils import CanadianScraper

COUNCIL_URL = "https://www.innisfil.ca/government-administration/council-committees/members-council"


class InnisfilPersonScraper(CanadianScraper):
    def scrape(self):
        page = self.lxmlize(COUNCIL_URL)
        name_links = page.xpath('//h3/a[contains(@href,"/members-council/")]')
        assert name_links, "No council member links found"
        for a in name_links:
            name = a.text_content().strip()
            if not name:
                continue
            # Walk up to find card container with <p><strong> elements
            card = a.getparent()
            for _ in range(10):
                if card is None:
                    break
                if card.xpath(".//p[./strong]"):
                    break
                card = card.getparent()
            if card is None:
                continue
            pos_strong = card.xpath('.//strong[contains(.,"Position")]')
            pos_text = (
                pos_strong[0].tail.strip()
                if pos_strong and pos_strong[0].tail
                else ""
            )
            if not pos_text:
                pos_p = card.xpath('.//p[./strong[contains(.,"Position")]]')
                pos_text = (
                    pos_p[0].text_content().replace("Position:", "").strip()
                    if pos_p
                    else ""
                )
            if "Mayor" in pos_text and "Deputy" not in pos_text:
                role, district = "Mayor", "Innisfil"
            elif "Deputy Mayor" in pos_text:
                role, district = "Councillor", "Deputy Mayor"
            else:
                m = re.search(r"Ward\s+(\d+)", pos_text)
                role = "Councillor"
                district = f"Ward {m.group(1)}" if m else pos_text
            email = self.get_email(card, error=False)
            phone_link = card.xpath('.//a[starts-with(@href,"tel:")]')
            phone = phone_link[0].text_content().strip() if phone_link else None
            image = card.xpath(".//img/@src")
            p = Person(primary_org="legislature", name=name, district=district, role=role)
            p.add_source(COUNCIL_URL)
            if email:
                p.add_contact("email", email)
            if phone:
                p.add_contact("voice", phone, "legislature")
            if image:
                p.image = image[0]
            yield p
