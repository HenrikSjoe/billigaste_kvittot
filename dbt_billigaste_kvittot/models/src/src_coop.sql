with
    stg_coop as (select * from {{ source('billigaste_kvittot_db', 'stg_coop') }}),
    stg_coop_cluster as (select * from {{ source('billigaste_kvittot_db', 'stg_coop_cluster') }}),
    stg_coop_limitations as (select * from {{ source('billigaste_kvittot_db', 'stg_coop_cluster') }})

select
butiksnamn as store,
vecka as week,
coalesce (c.content__brand, 'Okänd') as brand,
coalesce(co.content__title, c.content__title) as product_name,
coalesce(c.content__description, co.content__description) as description,
cast(coalesce(c.price_information__ordinary_price,co.price_information__ordinary_price)as string) as ordanary_price_with_null,
coalesce(ordanary_price_with_null,'Saknar ordinarie pris') as ordinary_price,
coalesce(c.price_information__discount_value, co.price_information__discount_value) as campain_price_with_null,
coalesce (campain_price_with_null, c.price_information__discount_value__v_double) as promotion_price,
coalesce(c.price_information__unit, c.price_information__deal_type) as coalesce_unit,
case
  when coalesce_unit = 'förp' then 'kr/st'
  when coalesce_unit = 'port' then 'kr/st'
  when coalesce_unit = 'port.' then 'kr/st'
  when coalesce_unit = 'styckpris' then 'kr/st'
  when coalesce_unit = 'pris' then 'kr/st'
  when coalesce_unit = 'proc' then 'kr/st'
  when coalesce_unit = 'st' then 'kr/st'
  when coalesce_unit = 'kg' then 'kr/kg'
end as unit,
c.content__amount_information as product_unit,
coalesce(c.price_information__minimum_amount, 1) as qualification_quantity,
cl.value as max_quantity,
c.category_group as category,
c.category_team__name as category_group,
c.campaign_end_date as end_date,
concat('https:', c.content__image_url) as image_url,
c.eag_id as promotion_id,
from stg_coop c
left join staging.coop__cluster_interior_offers co on co._dlt_parent_id = c._dlt_id
left join staging.coop__content__limitations cl on cl._dlt_parent_id = c._dlt_id
order by vecka desc