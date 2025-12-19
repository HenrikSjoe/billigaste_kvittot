import dlt
from dlt.sources.filesystem import filesystem
import datetime
import requests

week = datetime.date.today().isocalendar()[1]
today = datetime.date.today()
end_date = today + datetime.timedelta(days=(6 - today.weekday()))

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
    "?filters=boolean%3DonOffer&sort=favorite"
)

r2 = session.get(
    api_url,
    headers={
        "Referer": "https://handlaprivatkund.ica.se/",
        "Origin": "https://handlaprivatkund.ica.se",
        "ecom-request-source": "web",
    }
)


def ica_source():
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
        "?filters=boolean%3DonOffer&sort=favorite"
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

        print(products[item])
        break

if __name__ == "__main__":
    ica_source()