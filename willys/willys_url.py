import requests
import json
import datetime

get_response = requests.get('https://www.willys.se/search/campaigns/online?q=2110&type=PERSONAL_GENERAL&page=0&size=1000')

data = get_response.json()  # Konvertera text till Python-objekt

vecka = datetime.date.today().isocalendar()[1]

with open(f'willys/data/willys_erbjudanden_v{vecka}.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=4)  # Skriver "pretty" JSON


print(get_response.status_code)