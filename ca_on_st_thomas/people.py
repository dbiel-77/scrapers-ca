from utils import CanadianPerson as Person
from utils import CanadianScraper

LISTING_URL = "https://www.stthomas.ca/city_hall/city_council"


class StThomasPersonScraper(CanadianScraper):
    def scrape(self):
        page = self.lxmlize(LISTING_URL)
        profile_links = list(
            dict.fromkeys(
                page.xpath(
                    '//a[contains(@href,"/city_hall/city_council/mayor_")'
                    ' or contains(@href,"/city_hall/city_council/councillor_")]/@href'
                )
            )
        )
        assert profile_links, "No member profile links found"
        seat = 0
        for href in profile_links:
            url = href if href.startswith("http") else f"https://www.stthomas.ca{href}"
            ppage = self.lxmlize(url)
            name_h = ppage.xpath('//h1 | //h2[contains(@class,"page-title")]')
            name = name_h[0].text_content().strip() if name_h else ""
            if not name:
                continue
            if "mayor_" in href:
                role, district = "Mayor", "St. Thomas"
            else:
                seat += 1
                role, district = "Councillor", f"St. Thomas (seat {seat})"
            email = self.get_email(ppage, error=False)
            phone = self.get_phone(ppage, area_codes=[519, 226, 548], error=False)
            image = ppage.xpath(
                '//img[contains(@src,"civiclive.com") or contains(@src,"UserFiles")]/@src'
            )
            p = Person(primary_org="legislature", name=name, district=district, role=role)
            p.add_source(LISTING_URL)
            p.add_source(url)
            if email:
                p.add_contact("email", email)
            if phone:
                p.add_contact("voice", phone, "legislature")
            if image:
                p.image = image[0]
            yield p
