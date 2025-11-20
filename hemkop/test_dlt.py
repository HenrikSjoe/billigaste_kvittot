import dlt
import requests

def get_hemkop_data(page, size=1000):
    url = "https://www.hemkop.se/search/campaigns"
    params = {
        "page": page,
        "size": size
    }
    response = requests.get(url, params=params)
    response.raise_for_status()

    return response.json().get("potentialPromotions", [])

@dlt.resource(
    name="hemkop_erbjudanden",
    table_name="hemkop_erbjudanden",
    primary_key="id",
    write_disposition="merge"
)
def hemkop_campaigns():
    page = 0
    size = 1000

    while True:
        data = get_hemkop_data(page, size)
        if not data:
            break

        for item in data:
            yield item
        
        if len(data) < size:
            break

        page += 1

@dlt.source
def hemkop_source():
    return hemkop_campaigns()

pipeline = dlt.pipeline(
    pipeline_name="hemkop_erbjudanden_pipeline",
    destination="duckdb",
    dataset_name="hemkop_erbjudanden_dataset"
)

pipeline.run(hemkop_source())