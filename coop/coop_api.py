import requests
import json
import datetime

vecka = datetime.date.today().isocalendar()[1]

url = "https://external.api.coop.se/dke/offers/categories/offers/252700"

querystring = {"api-version":"v1","clustered":"true"}

payload = ""
headers = {
    "accept": "application/json, text/plain, */*",
    "accept-language": "sv-SE,sv;q=0.8",
    "ocp-apim-subscription-key": "3804fe145c4e4629ab9b6c755d2e3cfb",
    "origin": "https://www.coop.se",
    "priority": "u=1, i",
    "referer": "https://www.coop.se/",
    "sec-ch-ua": '"Not;A=Brand";v="99", "Brave";v="139", "Chromium";v="139"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "sec-gpc": "1",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36"
}


response = requests.request("GET", url, data=payload, headers=headers, params=querystring)
data = response.json()


with open(f'coop/data/coop_erbjudanden_v{vecka}.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=4)

print(response.status_code)