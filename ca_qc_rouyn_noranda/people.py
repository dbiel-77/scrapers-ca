import re

from utils import CanadianPerson as Person
from utils import CanadianScraper

COUNCIL_URL = "https://www.rouyn-noranda.ca/ville/vie-democratique/conseil-municipal"


class RouynNorandaPersonScraper(CanadianScraper):
    def scrape(self):
        page = self.lxmlize(COUNCIL_URL)

        # Mayor
        mairie_h2 = page.xpath('//h2[contains(., "Mairie") or contains(., "mairie")]')
        assert mairie_h2, "Mairie section not found"
        mayor_h3 = mairie_h2[0].xpath("following-sibling::h3[1]")
        assert mayor_h3, "Mayor name h3 not found"
        mayor_name = mayor_h3[0].text_content().strip()
        mayor_email_a = mairie_h2[0].xpath(
            'following-sibling::a[starts-with(@href,"mailto:")][1]'
        )
        mayor_email = (
            mayor_email_a[0].get("href").replace("mailto:", "") if mayor_email_a else None
        )
        p = Person(
            primary_org="legislature", name=mayor_name, district="Rouyn-Noranda", role="Mayor"
        )
        p.add_source(COUNCIL_URL)
        if mayor_email:
            p.add_contact("email", mayor_email)
        yield p

        # Councillors: h3 elements matching "District N"
        all_h3 = page.xpath("//h3")
        district_h3s = [
            h for h in all_h3 if re.match(r"District\s+\d+", h.text_content().strip())
        ]
        assert district_h3s, "No district h3 headings found"
        for h3 in district_h3s:
            district_text = h3.text_content().strip()
            m = re.match(r"District\s+(\d+)", district_text)
            district = f"District {int(m.group(1))}"
            name_h4 = h3.xpath("following-sibling::h4[1]")
            if not name_h4:
                continue
            name = name_h4[0].text_content().strip()
            email_a = h3.xpath('following-sibling::a[starts-with(@href,"mailto:")][1]')
            email = email_a[0].get("href").replace("mailto:", "") if email_a else None
            p = Person(
                primary_org="legislature", name=name, district=district, role="Councillor"
            )
            p.add_source(COUNCIL_URL)
            if email:
                p.add_contact("email", email)
            yield p
