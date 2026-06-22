import re

from utils import CanadianPerson as Person
from utils import CanadianScraper

COUNCIL_PAGE = "https://www.wilmot.ca/township-office/council/"


class WilmotPersonScraper(CanadianScraper):
    def scrape(self):
        page = self.lxmlize(COUNCIL_PAGE)

        # Collapsible sections; trigger link text is "Mayor Natasha Salonen"
        # or "Ward 1 Councillor Stewart Cressman"
        councillors = page.xpath('//a[contains(@href, "#collapse_")]')
        assert len(councillors), "No councillors found"
        for councillor in councillors:
            heading = councillor.text_content().strip()
            match = re.match(r"(Mayor|(?:Ward \d+ )?Councillor)\s+(.+)", heading)
            if not match:
                continue
            role_text = match.group(1).strip()
            name = match.group(2).strip()

            if "Councillor" in role_text and role_text != "Councillor":
                district = role_text.split(" Councillor")[0]
                role = "Councillor"
            elif role_text == "Mayor":
                district = "Wilmot"
                role = "Mayor"
            else:
                district = "Wilmot"
                role = role_text

            collapse_id = councillor.get("href").lstrip("#")
            panel = page.xpath(f'//div[@id="{collapse_id}"]')
            if not panel:
                continue
            panel = panel[0]

            phone = self.get_phone(panel)
            email = self.get_email(panel)
            p = Person(primary_org="legislature", name=name, district=district, role=role)
            p.add_source(COUNCIL_PAGE)
            p.add_contact("voice", phone, "legislature")
            p.add_contact("email", email)
            yield p
