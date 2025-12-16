from pathlib import Path
import dlt
import dagster as dg
from dagster_dlt import DagsterDltResource, dlt_assets
from dagster_dbt import DbtCliResource, DbtProject, dbt_assets
from stores.city_gross.citygross_dlt import citygross_source
from stores.willys.willys_dlt import willys_source
from stores.hemkop.hemkop_dlt import hemkop_source
from stores.coop.coop_dlt import coop_source

# --- SETUP ---
db_path = Path(__file__).parents[1] / "database/billigaste_kvittot_db.duckdb"
dbt_project_directory = Path(__file__).parents[1] / "dbt_billigaste_kvittot"
profiles_dir = Path(__file__).parents[1] 

dbt_project = DbtProject(
    project_dir=dbt_project_directory,
    profiles_dir=profiles_dir
)
dbt_project.prepare_if_dev()

dlt_resource = DagsterDltResource()
dbt_resource = DbtCliResource(project_dir=dbt_project)

# --- DLT ASSETS (DATA INGESTION) ---

@dlt_assets(
    dlt_source=citygross_source(),
    dlt_pipeline=dlt.pipeline(pipeline_name="citygross_pipeline", destination=dlt.destinations.duckdb(db_path), dataset_name="staging"),
    group_name='promotion_data',
)
def citygross_load(context: dg.AssetExecutionContext, dlt: DagsterDltResource):
    yield from dlt.run(context=context)

@dlt_assets(
    dlt_source=coop_source(),
    dlt_pipeline=dlt.pipeline(pipeline_name="coop_pipeline", destination=dlt.destinations.duckdb(db_path), dataset_name="staging"),
    group_name='promotion_data',
)
def coop_load(context: dg.AssetExecutionContext, dlt: DagsterDltResource):
    yield from dlt.run(context=context)

@dlt_assets(
    dlt_source=hemkop_source(),
    dlt_pipeline=dlt.pipeline(pipeline_name="hemkop_pipeline", destination=dlt.destinations.duckdb(db_path), dataset_name="staging"),
    group_name='promotion_data',
)
def hemkop_load(context: dg.AssetExecutionContext, dlt: DagsterDltResource):
    yield from dlt.run(context=context)

@dlt_assets(
    dlt_source=willys_source(),
    dlt_pipeline=dlt.pipeline(pipeline_name="willys_pipeline", destination=dlt.destinations.duckdb(db_path), dataset_name="staging"),
    group_name='promotion_data',
)
def willys_load(context: dg.AssetExecutionContext, dlt: DagsterDltResource):
    yield from dlt.run(context=context)

# --- DBT ASSETS (TRANSFORMATION) ---

@dbt_assets(manifest=dbt_project.manifest_path)
def dbt_models(context: dg.AssetExecutionContext, dbt: DbtCliResource):
    yield from dbt.cli(["build"], context=context).stream()

# --- JOBB (Ett per butik + ett för DBT) ---

job_citygross = dg.define_asset_job("job_citygross", selection=[citygross_load])
job_coop = dg.define_asset_job("job_coop", selection=[coop_load])
job_hemkop = dg.define_asset_job("job_hemkop", selection=[hemkop_load])
job_willys = dg.define_asset_job("job_willys", selection=[willys_load])

job_dbt = dg.define_asset_job("job_dbt", selection=[dbt_models])

# --- SCHEDULES (Tidsförskjutna för att undvika DuckDB-krockar) ---

# Vi sprider ut dem med 15 minuters mellanrum. 
# Om alla startar 06:00 exakt samtidigt kommer databasen låsa sig.

schedule_citygross = dg.ScheduleDefinition(job=job_citygross, cron_schedule="0 5 * * 1")   # 06:00
schedule_coop = dg.ScheduleDefinition(job=job_coop, cron_schedule="5 5 * * 1")          # 06:15
schedule_hemkop = dg.ScheduleDefinition(job=job_hemkop, cron_schedule="10 5 * * 1")      # 06:30
schedule_willys = dg.ScheduleDefinition(job=job_willys, cron_schedule="15 5 * * 1")      # 06:45

# --- SENSOR (Kör DBT efter att något av butiksjobben är klart) ---

@dg.run_status_sensor(
    run_status=dg.DagsterRunStatus.SUCCESS,
    request_job=job_dbt,
)
def trigger_dbt_after_store_updates(context):
    # Lista på jobb som ska trigga en uppdatering av DBT-modellerna
    store_jobs = ["job_citygross", "job_coop", "job_hemkop", "job_willys"]
    
    if context.dagster_run.job_name in store_jobs:
        return dg.RunRequest()

# --- DEFINITIONS ---

defs = dg.Definitions(
    assets=[citygross_load, willys_load, coop_load, hemkop_load, dbt_models],
    resources={
        "dlt": dlt_resource,
        "dbt": dbt_resource,
    },
    jobs=[job_citygross, job_coop, job_hemkop, job_willys, job_dbt],
    schedules=[schedule_citygross, schedule_coop, schedule_hemkop, schedule_willys],
    sensors=[trigger_dbt_after_store_updates],
)