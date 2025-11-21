import dlt
from dlt.sources.filesystem import filesystem
import json
import os 
from pathlib import Path
from flatten_json import flatten


working_directory = Path(__file__).parent
data_path = Path(__file__).parent / "data/city_gross_erbjudanden_v47.json"
db_path = Path(__file__).parent / "database/citygross_pipeline.duckdb"

@dlt.resource(write_disposition="merge", table_name="City_gross")
def get_data():
    with open(data_path) as f:
        data = json.load(f)
    
    for item in data["items"]:
        #flat = flatten(item, separator="__")
        yield item

def run_pipeline():
    pipeline = dlt.pipeline(
        pipeline_name="citygross_pipeline",
        destination= dlt.destinations.duckdb(db_path),
        dataset_name="staging",
    )


    load_info = pipeline.run(get_data())

if __name__ == "__main__":
    #os.chdir(working_directory)
    run_pipeline()