import dlt
from dlt.sources.filesystem import filesystem
from pathlib import Path
import datetime
import requests

week = datetime.date.today().isocalendar()[1]
today = datetime.date.today()
end_date = today + datetime.timedelta(days=(6 - today.weekday()))
url = "https://www.hemkop.se/search/campaigns?page=0&size=1000"

db_path = Path(__file__).parents[2] / "database/billigaste_kvittot_db.duckdb"


@dlt.source
def hemkop_source():
    @dlt.resource(write_disposition="append", table_name="hemkop")
    def get_hemkop():
        data = requests.get(url).json()
        for item in data["results"]:
            item["butiksnamn"] = "Hemköp"
            item["vecka"] = week
            item["end_date"] = end_date

            yield item

    return get_hemkop()