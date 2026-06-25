import re

from utils import CanadianPerson as Person
from utils import CanadianScraper

COUNCIL_PAGE = "https://www.oshawa.ca/city-hall/city-council/council-members/"


class OshawaPersonScraper(CanadianScraper):
    def scrape(self):
        page = self.lxmlize(COUNCIL_PAGE)
        # Page uses semantic HTML: h3 (name) + p (role) + p (tel) + p (email), no container class.
        # Anchor on h3 elements that have a following mailto: link.
        h3_nodes = page.xpath('//h3[following-sibling::p[a[contains(@href,"mailto:")]]]')
        assert h3_nodes, "No council member headings found"

        for h3 in h3_nodes:
            name = h3.text_content().strip()
            if not name:
                continue
            parent = h3.getparent()
            children = list(parent)
            h3_idx = children.index(h3)
            # Collect sibling elements up to the next h3 or img (next member boundary)
            next_boundary = next(
                (i for i, el in enumerate(children[h3_idx + 1 :], h3_idx + 1) if el.tag in ("h3", "img")),
                len(children),
            )
            member_els = children[h3_idx + 1 : next_boundary]
            p_els = [el for el in member_els if el.tag == "p"]

            role_text = p_els[0].text_content().strip() if p_els else ""
            role_text = re.sub(r"\s+" + re.escape(name) + r"$", "", role_text).strip()

            if "Mayor" in role_text and "Ward" not in role_text:
                role = "Mayor"
                district = "Oshawa"
            else:
                ward_match = re.match(r"(Ward \d+)\s+(.+)", role_text)
                if not ward_match:
                    continue
                district = ward_match.group(1)
                role_desc = ward_match.group(2)
                role = "Regional Councillor" if "Regional" in role_desc else "Councillor"

            # Image from preceding img sibling
            img_els = [children[i] for i in range(h3_idx - 1, max(-1, h3_idx - 4), -1) if children[i].tag == "img"]
            photo_url = img_els[0].get("src") if img_els else None

            phone = None
            email = None
            links = []
            for p in p_els:
                for a in p.xpath(".//a"):
                    href = a.get("href", "")
                    if href.startswith("tel:"):
                        phone_text = a.text_content().strip().lstrip("/")
                        if phone_text:
                            phone = phone_text
                    elif href.startswith("mailto:"):
                        email = href.replace("mailto:", "")
                    elif href:
                        links.append(href)

            p = Person(primary_org="legislature", name=name, district=district, role=role, image=photo_url)
            p.add_source(COUNCIL_PAGE)
            if phone:
                p.add_contact("voice", phone, "legislature")
            if email:
                p.add_contact("email", email)
            for link in links:
                p.add_link(link)
            yield p
