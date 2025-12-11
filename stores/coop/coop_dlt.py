import dlt
from dlt.sources.filesystem import filesystem
from pathlib import Path
import datetime
import requests
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("COOP_API_KEY")

week = datetime.date.today().isocalendar()[1]
url = "https://external.api.coop.se/dke/offers/252700?api-version=v1&clustered=true"
headers = {
    "ocp-apim-subscription-key": api_key
}

db_path = Path(__file__).parents[2] / "database/billigaste_kvittot_db.duckdb"

@dlt.resource(write_disposition="merge",primary_key="eagId" ,table_name="Coop")
def get_data():
    data = requests.get(url, headers=headers).json()
    for item in data:
        item["butiksnamn"] = "Coop"
        item["vecka"] = week

        yield item

def coop_pipeline():
    pipeline = dlt.pipeline(
        pipeline_name="coop_pipeline",
        destination= dlt.destinations.duckdb(db_path),
        dataset_name="staging",
    )


    load_info = pipeline.run(get_data())

if __name__ == "__main__":
    coop_pipeline()