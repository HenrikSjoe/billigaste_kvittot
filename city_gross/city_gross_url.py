import requests
import json
import datetime

get_response = requests.get('https://www.citygross.se/api/v1/Loop54/category/2930/products?breadcrumb=Matvaror%20%3E%20Veckans%20erbjudanden&categoryName=Veckans%20erbjudanden&currentWeekDiscountOnly=true&skip=0&take=24')

data = get_response.json()

vecka = datetime.date.today().isocalendar()[1]

with open(f'city_gross/data/city_gross_erbjudanden_v{vecka}.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=4)


print(get_response.status_code)