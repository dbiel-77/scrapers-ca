from utils import CanadianPerson as Person
from utils import CanadianScraper

COUNCIL_PAGE = "https://www.thunderbay.ca/en/city-hall/mayor-and-council-profiles.aspx"
BASE_URL = "https://www.thunderbay.ca"


class ThunderBayPersonScraper(CanadianScraper):
    def scrape(self):
        seat_number = 1
        # SSLError(SSLError(1, '[SSL: DH_KEY_TOO_SMALL] dh key too small (_ssl.c:1133)'))
        page = self.lxmlize(COUNCIL_PAGE, verify=False)

        # Current structure: <img src="/en/city-hall/resources/Images/Mayor-and-Council/...">
        # followed by ward-label text (as anchor tail or div), then <h6>Name</h6>
        # Some cards are wrapped in <a href="...">; others are bare.
        # Pattern per card (linked):
        #   <a href="..."><img ...>Ward Label text</a><h6>Name</h6>
        # Pattern per card (unlinked):
        #   <img ...><div>Ward Label</div><h6>Name</h6>
        councillor_imgs = page.xpath('//img[contains(@src, "/Mayor-and-Council/")]')
        assert len(councillor_imgs), "No councillors found"

        for img in councillor_imgs:
            photo_src = img.get("src", "")
            photo = BASE_URL + photo_src if photo_src.startswith("/") else photo_src

            parent = img.getparent()

            if parent.tag == "a":
                # Linked: ward label is the tail text of the img inside the anchor
                ward_label = (img.tail or "").strip()
                if not ward_label:
                    # fallback: full text of anchor minus img alt text
                    ward_label = parent.text_content().strip()
                # Name h6 is a following sibling of the anchor
                name_h6 = parent.xpath("following-sibling::h6")
                name = name_h6[0].text_content().strip() if name_h6 else ""
                search_node = parent.getparent()
            else:
                # Unlinked: ward label is in a following sibling div or text node
                ward_div = img.xpath("following-sibling::div")
                ward_label = ward_div[0].text_content().strip() if ward_div else (img.tail or "").strip()
                name_h6 = img.xpath("following-sibling::h6")
                name = name_h6[0].text_content().strip() if name_h6 else ""
                search_node = parent

            if not name:
                continue

            # Strip leading "Mayor " from name if present in h6 (e.g. "Mayor Ken Boshcoff")
            if name.startswith("Mayor "):
                name = name[len("Mayor "):]

            if ward_label == "Mayor":
                role = "Mayor"
                district = "Thunder Bay"
            elif "At Large" in ward_label:
                role = "Councillor at Large"
                district = f"Thunder Bay (seat {seat_number})"
                seat_number += 1
            elif ward_label:
                role = "Councillor"
                district = ward_label
            else:
                role = "Councillor"
                district = "Thunder Bay"

            email = self.get_email(search_node, error=False)
            phone = self.get_phone(search_node, error=False)

            p = Person(primary_org="legislature", name=name, district=district, role=role)
            p.add_source(COUNCIL_PAGE)
            if email:
                p.add_contact("email", email)
            if phone:
                p.add_contact("voice", phone, "legislature")
            p.image = photo

            yield p
