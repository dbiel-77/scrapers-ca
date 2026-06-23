from utils import CanadianPerson as Person
from utils import CanadianScraper

COUNCIL_PAGE = "https://www.lethbridge.ca/council-administration-governance/mayor-and-councillors/councillors-office"
MAYOR_PAGE = "https://www.lethbridge.ca/council-administration-governance/mayor-and-councillors/mayors-office"


class LethbridgePersonScraper(CanadianScraper):
    def scrape_mayor(self):
        page = self.lxmlize(MAYOR_PAGE)

        # Use the first p following the biography h4 (e.g. "Mayor Hyggen"), which starts "FirstName LastName was..."
        bio_paragraphs = page.xpath("//h4[contains(., 'Mayor') and not(contains(., 'Watch'))]/following-sibling::p")
        bio_text = bio_paragraphs[0].text_content().strip()
        # Extract "FirstName LastName" from "FirstName LastName was ..." or fallback to first two words
        name_match = bio_text.split(" was ")[0].strip() if " was " in bio_text else " ".join(bio_text.split()[:2])
        name = name_match

        p = Person(primary_org="legislature", name=name, district="Lethbridge", role="Mayor")
        p.image = page.xpath("//img/@src")[0]
        p.add_source(MAYOR_PAGE)

        return p

    def scrape_person(self, url, seat_number):
        page = self.lxmlize(url)
        name = page.xpath('//h1[contains(@class, "heading main base-heading")]')[0].text_content().split(",")[0]

        p = Person(
            primary_org="legislature",
            name=name,
            district=f"Lethbridge (seat {seat_number + 1})",
            role="Councillor",
        )

        p.image = page.xpath('//span[contains(@class, "img-right")]/img/@src[1]')[0]
        p.add_source(COUNCIL_PAGE)
        p.add_source(url)

        return p

    def scrape(self):
        yield self.scrape_mayor()

        page = self.lxmlize(COUNCIL_PAGE)
        councillors = page.xpath('//div[contains(@class, "inner ")]/a[@href]')
        assert len(councillors), "No councillors found"
        for seat_number, councillor in enumerate(councillors):
            name = councillor.xpath(".//span")[0].text_content()
            if "Vacant" in name:
                continue
            url = councillor.xpath("./@href")[0]
            yield self.scrape_person(url, seat_number)
