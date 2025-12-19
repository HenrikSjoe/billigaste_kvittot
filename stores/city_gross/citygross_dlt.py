import dlt
from dlt.sources.filesystem import filesystem
import datetime
import requests

week = datetime.date.today().isocalendar()[1]
url = "https://www.citygross.se/api/v1/Loop54/category/2930/products?breadcrumb=Matvaror%20%3E%20Veckans%20erbjudanden&categoryName=Veckans%20erbjudanden&currentWeekDiscountOnly=true&skip=0&take=500"

@dlt.source
def citygross_source():
    @dlt.resource(write_disposition="append", table_name="City_gross")
    def get_citygross():
        data = requests.get(url).json()
        for item in data["items"]:
            item["butiksnamn"] = "City Gross"
            item["vecka"] = week

            yield item


    return get_citygross()

