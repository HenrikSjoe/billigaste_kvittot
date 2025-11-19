import requests
import json
import datetime

get_response = requests.get('https://www.hemkop.se/search/campaigns?page=0&size=1000')

data = get_response.json()

vecka = datetime.date.today().isocalendar()[1]

with open(f'hemkop/data/hemkop_erbjudanden_v{vecka}.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=4)


print(get_response.status_code)