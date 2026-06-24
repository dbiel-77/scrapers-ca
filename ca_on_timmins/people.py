import re

from utils import CanadianPerson as Person
from utils import CanadianScraper

LISTING_URL = "https://www.timmins.ca/how_do_i_/contact_an_elected_official"
BASE = "https://www.timmins.ca"


class TimminsPersonScraper(CanadianScraper):
    def scrape(self):
        page = self.lxmlize(LISTING_URL)
        member_links = list(dict.fromkeys(page.xpath('//a[contains(@href,"portalId=11976429")]/@href')))
        assert member_links, "No member CMS links found"
        ward5_seat = 0
        for href in member_links:
            url = href if href.startswith("http") else BASE + href
            ppage = self.lxmlize(url)
            name_h = ppage.xpath('//h1 | //h2[@class="page-title"]')
            name = name_h[0].text_content().strip() if name_h else ""
            if not name:
                continue
            body_text = " ".join(ppage.xpath("//body//text()"))
            if re.search(r"\bMayor\b", body_text) and not re.search(r"\bWard\b", body_text, re.I):
                role, district = "Mayor", "Timmins"
            else:
                ward_m = re.search(r"Ward\s+(\d+)", body_text, re.I)
                ward_num = int(ward_m.group(1)) if ward_m else None
                role = "Councillor"
                if ward_num == 5:
                    ward5_seat += 1
                    district = f"Ward 5 (seat {ward5_seat})"
                elif ward_num:
                    district = f"Ward {ward_num}"
                else:
                    district = "Timmins"
            email = self.get_email(ppage, error=False)
            phone = self.get_phone(ppage, area_codes=[705], error=False)
            image = ppage.xpath('//img[contains(@src,"civiclive.com")]/@src')
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
