from utils import CanadianPerson as Person
from utils import CanadianScraper

COUNCIL_PAGE = "https://banff.ca/686/Meet-Town-Council"
MEMBERS = [
    ("Corrie DiManno", "Mayor", "Banff", "Corrie.DiManno@banff.ca"),
    ("Michelle Backhouse", "Councillor", "Banff (seat 1)", "Michelle.Backhouse@banff.ca"),
    ("David Fullerton", "Councillor", "Banff (seat 2)", "David.Fullerton@banff.ca"),
    ("Barb Pelham", "Councillor", "Banff (seat 3)", "Barb.Pelham@banff.ca"),
    ("Marc Ledwidge", "Councillor", "Banff (seat 4)", "Marc.Ledwidge@banff.ca"),
    ("Kaylee Ram", "Councillor", "Banff (seat 5)", "Kaylee.Ram@banff.ca"),
    ("Brian Standish", "Councillor", "Banff (seat 6)", "Brian.Standish@banff.ca"),
]


class BanffPersonScraper(CanadianScraper):
    def scrape(self):
        page = self.lxmlize(COUNCIL_PAGE, verify=False)
        text = page.text_content()
        assert all(email in text for _, _, _, email in MEMBERS), "Expected all Banff emails on page"

        for name, role, district, email in MEMBERS:
            p = Person(primary_org="legislature", name=name, district=district, role=role)
            p.add_source(COUNCIL_PAGE)
            p.add_contact("email", email)
            yield p
