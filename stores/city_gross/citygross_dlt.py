import dlt
from dlt.sources.filesystem import filesystem
from pathlib import Path
import datetime
import requests

week = datetime.date.today().isocalendar()[1]
url = "https://www.citygross.se/api/v1/Loop54/category/2930/products?breadcrumb=Matvaror%20%3E%20Veckans%20erbjudanden&categoryName=Veckans%20erbjudanden&currentWeekDiscountOnly=true&skip=0&take=500"

db_path = Path(__file__).parents[2] / "database/billigaste_kvittot_db.duckdb"

@dlt.resource(write_disposition="append", table_name="City_gross")
def get_data():
    data = requests.get(url).json()
    for item in data["items"]:
        item["butiksnamn"] = "City Gross"
        item["vecka"] = week

        yield item

def citygross_pipeline():
    pipeline = dlt.pipeline(
        pipeline_name="citygross_pipeline",
        destination= dlt.destinations.duckdb(db_path),
        dataset_name="staging",
    )


    load_info = pipeline.run(get_data())

if __name__ == "__main__":
    citygross_pipeline()