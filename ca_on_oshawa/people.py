import re

from utils import CanadianPerson as Person
from utils import CanadianScraper

COUNCIL_PAGE = "https://www.oshawa.ca/city-hall/city-council/council-members/"


class OshawaPersonScraper(CanadianScraper):
    def scrape(self):
        page = self.lxmlize(COUNCIL_PAGE)
        # Each card is a div.item containing div.inner > div.image + div.info
        councillors = page.xpath('//div[contains(@class, "usn_pod_textimage")]')

        assert len(councillors), "No councillors found"
        for councillor in councillors:
            name = councillor.xpath('.//p[contains(@class, "heading")]')[0].text_content().strip()
            role_text = councillor.xpath('.//div[contains(@class, "text")]//p[1]')[0].text_content().strip()

            if "Mayor" in role_text and "Ward" not in role_text:
                role = "Mayor"
                district = "Oshawa"
            else:
                # e.g. "Ward 1 Regional & City Councillor" or "Ward 1 City Councillor"
                # Strip trailing name if present (some paragraphs include it)
                role_text = re.sub(r"\s+" + re.escape(name) + r"$", "", role_text).strip()
                ward_match = re.match(r"(Ward \d+)\s+(.+)", role_text)
                if not ward_match:
                    continue
                district = ward_match.group(1)
                role_desc = ward_match.group(2)
                role = "Regional Councillor" if "Regional" in role_desc else "Councillor"

            photo_url = councillor.xpath(".//img/@src")
            photo_url = photo_url[0] if photo_url else None
            phone = self.get_phone(councillor)
            email = self.get_email(councillor)
            links = councillor.xpath(".//a/@href")

            p = Person(primary_org="legislature", name=name, district=district, role=role, image=photo_url)
            p.add_source(COUNCIL_PAGE)
            p.add_contact("voice", phone, "legislature")
            p.add_contact("email", email)
            for link in links:
                if "mailto:" not in link and "tel:" not in link:
                    p.add_link(link)
            yield p
