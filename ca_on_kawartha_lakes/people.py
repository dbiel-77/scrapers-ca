import re

from utils import CanadianPerson as Person
from utils import CanadianScraper

COUNCIL_PAGE = "https://www.kawarthalakes.ca/government-administration/mayor-and-council/get-to-know-your-council/"


class KawarthaLakesPersonScraper(CanadianScraper):
    def scrape(self):
        page = self.lxmlize(COUNCIL_PAGE)

        # h2 headings: "Ward 1 Councillor Emmett Yeo", "Ward 8 Deputy Mayor Tracy Richardson"
        # Mayor section uses a different heading
        councillors = page.xpath(
            '//h2[contains(., "Councillor") or contains(., "Deputy Mayor") or contains(., "Mayor")]'
        )
        assert len(councillors), "No councillors found"
        for councillor in councillors:
            heading = councillor.text_content().strip()

            ward_match = re.match(r"(Ward \d+)\s+((?:Deputy )?(?:Mayor|Councillor))\s+(.+)", heading)
            mayor_match = re.match(r"Mayor\s+(.+)", heading)

            if ward_match:
                district = ward_match.group(1)
                role_text = ward_match.group(2)
                name = ward_match.group(3).strip()
                role = "Councillor"
            elif mayor_match:
                district = "Kawartha Lakes"
                name = mayor_match.group(1).strip()
                role = "Mayor"
            else:
                continue

            if "RESIGNED" in name or "Vacant" in name:
                continue

            # Contact info follows the heading
            section = councillor.xpath("./following-sibling::*")
            email = self.get_email(councillor.getparent())
            phone = self.get_phone(councillor.getparent())
            image = councillor.getparent().xpath(".//img/@src")

            p = Person(primary_org="legislature", name=name, district=district, role=role)
            p.add_source(COUNCIL_PAGE)
            p.add_contact("voice", phone, "legislature")
            p.add_contact("email", email)
            if image:
                p.image = image[0]
            yield p
