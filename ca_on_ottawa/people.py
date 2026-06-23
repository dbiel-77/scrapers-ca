from utils import CSVScraper


class OttawaPersonScraper(CSVScraper):
    # https://open.ottawa.ca/documents/ottawa::elected-officials-2022-2026/about
    csv_url = (
        "https://hub.arcgis.com/api/download/v1/items/d099928f2e344b1b909fcf63e5acf3d1/csv?redirect=true&layers=0"
    )
    fallbacks = {"district name": "ward name"}
