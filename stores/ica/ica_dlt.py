import dlt
from dlt.sources.filesystem import filesystem
import datetime
import requests

week = datetime.date.today().isocalendar()[1]
today = datetime.date.today()
end_date = today + datetime.timedelta(days=(6 - today.weekday()))

url = 'https://handlaprivatkund.ica.se/stores/1003777/api/v6/products?pageToken=dfc403f8-04cf-4a1e-8891-7a483f6d16ca'

@dlt.source
def ica_source():
    @dlt.resource(write_disposition="append", table_name="ica")
    def get_ica():
        session = requests.Session()

        session.headers.update({
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
            "Accept": "application/json",
        })

        # 1️⃣ Bootstrap – besök ICA
        r1 = session.get("https://www.ica.se")
        print("ICA landing:", r1.status_code)
        print("Cookies after landing:", session.cookies.get_dict())

        # 2️⃣ API-call med samma session
        api_url = (
            "https://handlaprivatkund.ica.se/"
            "stores/1003777/api/v6/products"
            "?pageToken=dfc403f8-04cf-4a1e-8891-7a483f6d16ca"
        )

        data = session.get(
            api_url,
            headers={
                "Referer": "https://handlaprivatkund.ica.se/",
                "Origin": "https://handlaprivatkund.ica.se",
                "ecom-request-source": "web",
            }
        ).json()
        products = data["entities"]["product"]
        for item in products:
            products[item]["butiksnamn"] = "Ica"
            products[item]["vecka"] = week
            products[item]["end_date"] = end_date

            yield products[item]
        
    return get_ica()