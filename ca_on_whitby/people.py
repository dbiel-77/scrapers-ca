from utils import CanadianPerson as Person
from utils import CanadianScraper

COUNCIL_PAGE = "https://www.whitby.ca/en/town-hall/mayor-and-council.aspx"
BASE_URL = "https://www.whitby.ca"


class WhitbyPersonScraper(CanadianScraper):
    def scrape(self):
        regional_councillor_seat_number = 1
        page = self.lxmlize(COUNCIL_PAGE)

        # Collapse trigger anchors have href="#collapse_UUID_N" and contain councillor name
        councillors = page.xpath('//a[contains(@href, "#collapse_")]')
        assert len(councillors), "No councillors found"

        for trigger in councillors:
            label = trigger.text_content().strip()
            if not label:
                continue

            # Find the corresponding collapsed content div by ID
            collapse_id = trigger.get("href", "").lstrip("#")
            content_nodes = page.xpath(f'//div[@id="{collapse_id}"]')
            node = content_nodes[0] if content_nodes else trigger.getparent()

            if label.startswith("Mayor "):
                role = "Mayor"
                name = label[len("Mayor "):]
                district = "Whitby"
            elif ", Regional Councillor" in label:
                name = label.split(", Regional Councillor")[0]
                role = "Regional Councillor"
                district = f"Whitby (seat {regional_councillor_seat_number})"
                regional_councillor_seat_number += 1
            elif ", Town Councillor" in label:
                # "Steve Lee, Town Councillor – North Ward 1"
                name, rest = label.split(", Town Councillor")
                # rest is " – North Ward 1"
                district = rest.split(" – ")[-1].strip() if " – " in rest else "Whitby"
                role = "Councillor"
            else:
                continue

            image_nodes = node.xpath(".//img/@src")
            image = image_nodes[0] if image_nodes else None
            if image and not image.startswith("http"):
                image = BASE_URL + image

            p = Person(primary_org="legislature", name=name, district=district, role=role)
            p.add_source(COUNCIL_PAGE)
            phone = self.get_phone(node, error=False)
            if phone:
                p.add_contact("voice", phone, "legislature")
            if image:
                p.image = image

            yield p
