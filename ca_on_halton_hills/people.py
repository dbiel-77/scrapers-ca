from urllib.parse import quote, urljoin

from utils import CanadianPerson as Person
from utils import CanadianScraper

COUNCIL_PAGE = "https://www.haltonhills.ca/en/your-government/elected-officials.aspx"

MEMBERS = [
    ("Ann Lawlor", "Mayor", "Halton Hills", "Ann Lawlors"),
    ("Clark Somerville", "Regional Councillor", "Wards 1 & 2", "Clark Somerville"),
    ("Jane Fogal", "Regional Councillor", "Wards 3 & 4", "Jane Fogal"),
    ("Alex Hilson", "Councillor", "Ward 1 (seat 1)", "Alex Hilson"),
    ("Michael Albano", "Councillor", "Ward 1 (seat 2)", "Mike Albano"),
    ("Jason Brass", "Councillor", "Ward 2 (seat 1)", "Jason Brass"),
    ("Matt Kindbom", "Councillor", "Ward 2 (seat 2)", "Matt-Kindbom"),
    ("Chantal Garneau", "Councillor", "Ward 3 (seat 1)", "CouncillorGarneau"),
    ("Ron Norris", "Councillor", "Ward 3 (seat 2)", "Ron Norris"),
    ("Bob Inglis", "Councillor", "Ward 4 (seat 1)", "Bob Inglis"),
    ("D'Arcy Keene", "Councillor", "Ward 4 (seat 2)", "D'Arcy Keene"),
]


class HaltonHillsPersonScraper(CanadianScraper):
    def scrape(self):
        page = self.lxmlize(COUNCIL_PAGE)

        for name, role, district, image_hint in MEMBERS:
            blocks = page.xpath(
                '//div[contains(concat(" ", normalize-space(@class), " "), " iCreateDynaToken ")]'
                "[.//*[self::h3 or self::h4 or self::h5][contains(normalize-space(), $name)]]",
                name=name,
            )
            assert len(blocks) == 1, f"Expected one profile block for {name}"
            block = blocks[0]

            p = Person(primary_org="legislature", name=name, district=district, role=role)
            p.add_source(COUNCIL_PAGE)

            image = block.xpath(".//img/@src")
            if not image:
                encoded_hint = quote(image_hint, safe="'")
                image = page.xpath("//img[contains(@src, $hint)]/@src", hint=encoded_hint)
            if image:
                p.image = urljoin(COUNCIL_PAGE, image[0])

            email = self.get_email(block, error=False)
            if email:
                p.add_contact("email", email)

            phone = self.get_phone(block, area_codes=[289, 365, 416, 437, 519, 647, 742, 905], error=False)
            if phone:
                p.add_contact("voice", phone, "legislature")

            yield p
