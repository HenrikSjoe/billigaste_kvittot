with 
    stg_citygross as (select * from {{ source('billigaste_kvittot_db', 'stg_citygross') }}),
    stg_citygross_image as (select * from {{ source('billigaste_kvittot_db', 'stg_citygross_image') }})

select 
    cg.butiksnamn as store,
    cg.vecka as week,
    cg.product_store_details__prices__active_promotion__value as promotion_price,
    cg.product_store_details__prices__ordinary_price__price as ordinary_price,
    cg.descriptive_size as product_unit,
    cg.name as product_name,
    cg.category as category_group,
    cg.super_category as category,
    concat('https://www.citygross.se/images/products/', cgi.url) as image_url,
    cg.description,
    cg.brand,
    cg.product_store_details__prices__active_promotion__min_quantity as qualification_quantity,
    cg.product_store_details__prices__active_promotion__to as end_date,
    cg.product_store_details__prices__active_promotion__max_applied_per_receipt as max_quantity,
    cg.product_store_details__prices__active_promotion__name as promotion_id,
    cg.country_of_origin,
    case 
        when cg.product_store_details__prices__current_price__unit = 'KGM' THEN 'kr/kg'
        when cg.product_store_details__prices__current_price__unit = 'PCE' THEN 'kr/st'
    end as unit
from stg_citygross cg 
left join stg_citygross_image cgi on cgi._dlt_parent_id = cg._dlt_id