import dlt
from dlt.sources.filesystem import filesystem
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

@dlt.source
def coop_source():
    @dlt.resource(write_disposition="merge",primary_key="eagId" ,table_name="Coop")
    def get_coop():
        data = requests.get(url, headers=headers).json()
        for item in data:
            item["butiksnamn"] = "Coop"
            item["vecka"] = week

            yield item
    
    return get_coop

