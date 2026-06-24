import re

from utils import CanadianPerson as Person
from utils import CanadianScraper

COUNCIL_URL = "https://www.westkelownacity.ca/city-hall/mayor-and-council/contact-mayor-and-council/"


class WestKelownaPersonScraper(CanadianScraper):
    def scrape(self):
        page = self.lxmlize(COUNCIL_URL)
        h4_nodes = page.xpath(
            '//h4[contains(., "Contact Mayor") or contains(., "Contact Councillor")]'
        )
        assert h4_nodes, "No council member headings found"
        seat = 0
        for h4 in h4_nodes:
            header = h4.text_content().strip()
            if "Contact Mayor" in header:
                role, district = "Mayor", "West Kelowna"
            else:
                seat += 1
                role, district = "Councillor", f"West Kelowna (seat {seat})"
            container = h4.getparent()
            # Try to find full name in sibling h3 or parent container
            name_el = container.xpath(".//h3")
            if not name_el and container.getparent() is not None:
                name_el = container.getparent().xpath(".//h3")
            email_a = container.xpath('.//a[starts-with(@href,"mailto:")]')
            if not email_a and container.getparent() is not None:
                email_a = container.getparent().xpath('.//a[starts-with(@href,"mailto:")]')
            email = email_a[0].get("href").replace("mailto:", "") if email_a else None
            if name_el:
                name = name_el[0].text_content().strip()
            elif email:
                local = email.split("@")[0]
                name = " ".join(w.capitalize() for w in re.split(r"[\._]", local))
            else:
                name = (
                    header.replace("Contact Mayor ", "")
                    .replace("Contact Councillor ", "")
                    .strip()
                )
            phone_li_texts = container.xpath(".//li//text()")
            if container.getparent() is not None:
                phone_li_texts += container.getparent().xpath(".//li//text()")
            phone = None
            for t in phone_li_texts:
                m = re.search(r"\d{3}[-.\s]\d{3}[-.\s]\d{4}", t)
                if m:
                    phone = m.group(0)
                    break
            p = Person(primary_org="legislature", name=name, district=district, role=role)
            p.add_source(COUNCIL_URL)
            if email:
                p.add_contact("email", email)
            if phone:
                p.add_contact("voice", phone, "legislature")
            yield p
