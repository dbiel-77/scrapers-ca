from utils import CanadianPerson as Person
from utils import CanadianScraper

COUNCIL_PAGE = "https://www.thunderbay.ca/en/city-hall/mayor-and-council-profiles.aspx"
BASE_URL = "https://www.thunderbay.ca"


class ThunderBayPersonScraper(CanadianScraper):
    def scrape(self):
        seat_number = 1
        # SSLError(SSLError(1, '[SSL: DH_KEY_TOO_SMALL] dh key too small (_ssl.c:1133)'))
        page = self.lxmlize(COUNCIL_PAGE, verify=False)

        # All councillor photos are in the Mayor-and-Council images folder.
        # Structure varies by councillor:
        #   Linked:     <a href="..."><img src="..."><h6>Ward Name</h6></a><h6>Name</h6>
        #   Unlinked:   <img src="...">At Large text<h6>Name</h6>
        #   (ward/role label may be h6 inside <a> or plain text sibling of img)
        councillor_imgs = page.xpath('//img[contains(@src, "/Mayor-and-Council/")]')
        assert len(councillor_imgs), "No councillors found"

        for img in councillor_imgs:
            photo_src = img.get("src", "")
            photo = BASE_URL + photo_src if photo_src.startswith("/") else photo_src

            parent = img.getparent()

            if parent.tag == "a":
                # Linked councillor: ward/role h6 is inside the <a>, name h6 is after the <a>
                ward_h6 = parent.xpath("./h6")
                ward_label = ward_h6[0].text_content().strip() if ward_h6 else ""
                name_h6 = parent.xpath("following-sibling::h6")
                name = name_h6[0].text_content().strip() if name_h6 else ""
                search_node = parent.getparent()
            else:
                # Unlinked councillor: ward label is a text node sibling, name is in next h6
                # Get the text immediately following the img (tail text or next sibling text)
                ward_label = (img.tail or "").strip()
                if not ward_label:
                    # Try next sibling text nodes
                    next_sib = img.getnext()
                    if next_sib is not None and next_sib.tag not in ("h6", "h5", "h4"):
                        ward_label = next_sib.text_content().strip()
                name_h6 = img.xpath("following-sibling::h6")
                name = name_h6[0].text_content().strip() if name_h6 else ""
                search_node = parent

            if not name:
                continue

            # Default ward_label from h6 if still empty (some pages may use h6 for all)
            if not ward_label:
                h6_before_name = img.xpath("following-sibling::h6")
                if len(h6_before_name) >= 2:
                    ward_label = h6_before_name[0].text_content().strip()
                    name = h6_before_name[1].text_content().strip()

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
