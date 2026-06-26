import re

from utils import CanadianPerson as Person
from utils import CanadianScraper

LISTING_URL = "https://www.stthomas.ca/city_hall/city_council"
BROWSER_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36"
)


class StThomasPersonScraper(CanadianScraper):
    def scrape(self):
        page = self.lxmlize(LISTING_URL, user_agent=BROWSER_USER_AGENT)
        # Collect link nodes (not just hrefs) to also capture link text for names
        seen = set()
        profile_nodes = []
        for node in page.xpath(
            '//a[contains(@href,"/city_hall/city_council/mayor_")'
            ' or contains(@href,"/city_hall/city_council/councillor_")]'
        ):
            href = node.get("href", "")
            if href and href not in seen:
                seen.add(href)
                profile_nodes.append((href, node.text_content().strip()))
        assert profile_nodes, "No member profile links found"
        seat = 0
        for href, link_text in profile_nodes:
            # Profile page content is JS-rendered — derive name from link text or slug
            name_from_text = re.sub(r"^(Mayor|Councillor)\s+", "", link_text).strip()
            if len(name_from_text.split()) >= 2:
                name = name_from_text
            else:
                slug = href.rstrip("/").split("/")[-1]
                slug = re.sub(r"^(mayor_|councillor_)", "", slug)
                name = " ".join(w.capitalize() for w in slug.split("_"))
            if not name:
                continue
            if "mayor_" in href:
                role, district = "Mayor", "St. Thomas"
            else:
                seat += 1
                role, district = "Councillor", f"St. Thomas (seat {seat})"
            url = href if href.startswith("http") else f"https://www.stthomas.ca{href}"
            ppage = self.lxmlize(url, user_agent=BROWSER_USER_AGENT)
            email = self.get_email(ppage, error=False)
            phone = self.get_phone(ppage, area_codes=[519, 226, 548], error=False)
            image = ppage.xpath('//img[contains(@src,"civiclive.com") or contains(@src,"UserFiles")]/@src')
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
