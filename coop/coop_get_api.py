import requests
import json
import datetime
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("COOP_API_KEY")
vecka = datetime.date.today().isocalendar()[1]

url = "https://external.api.coop.se/dke/offers/252700?api-version=v1&clustered=true"

headers = {
    "ocp-apim-subscription-key": api_key
}

response = requests.get(url, headers=headers)
data = response.json()

with open(f'coop/data/coop_erbjudanden_v{vecka}.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=4)

print(response.status_code)