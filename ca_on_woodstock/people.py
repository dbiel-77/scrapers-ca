from utils import CanadianPerson as Person
from utils import CanadianScraper

COUNCIL_PAGE = "https://www.cityofwoodstock.ca/your-government/mayor-and-council/"


class WoodstockPersonScraper(CanadianScraper):
    def scrape(self):
        page = self.lxmlize(COUNCIL_PAGE)

        current_role = None
        seat = 0
        for block in page.xpath('//div[contains(@class,"text base-text")]'):
            h2 = block.xpath(".//h2")
            if h2:
                h2_text = h2[0].text_content().strip()
                if h2_text == "Mayor":
                    current_role = "Mayor"
                elif "Councillor" in h2_text:
                    current_role = "Councillor"
                continue

            h3 = block.xpath(".//h3")
            if not h3 or not current_role:
                continue

            name = h3[0].text_content().strip()
            if not name:
                continue

            if current_role == "Mayor":
                district = "Woodstock"
            else:
                seat += 1
                district = f"Woodstock (seat {seat})"

            phone = self.get_phone(block, area_codes=[519, 226, 548], error=False)
            image = block.xpath(".//img/@src")

            p = Person(primary_org="legislature", name=name, district=district, role=current_role)
            p.add_source(COUNCIL_PAGE)
            if phone:
                p.add_contact("voice", phone, "legislature")
            if image:
                p.image = image[0]
            yield p
