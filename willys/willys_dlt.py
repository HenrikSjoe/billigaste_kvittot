import dlt
from dlt.sources.filesystem import filesystem
from pathlib import Path
import datetime
import requests

vecka = datetime.date.today().isocalendar()[1]
url = 'https://www.willys.se/search/campaigns/online?q=2110&type=PERSONAL_GENERAL&page=0&size=1000'


working_directory = Path(__file__).parent
db_path = Path(__file__).parents[1] / "database/billigaste_kvittot_db.duckdb"

@dlt.resource(write_disposition="replace", table_name="willys")
def get_data():
    data = requests.get(url).json()
    for item in data["results"]:
        item["butiksnamn"] = "willys"
        item["vecka"] = vecka

        yield item

def run_pipeline():
    pipeline = dlt.pipeline(
        pipeline_name="willys_pipeline",
        destination= dlt.destinations.duckdb(db_path),
        dataset_name="staging",
    )


    load_info = pipeline.run(get_data())

if __name__ == "__main__":
    run_pipeline()