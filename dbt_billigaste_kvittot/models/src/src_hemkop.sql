with 
    stg_hemkop as (select * from {{ source('billigaste_kvittot_db', 'stg_hemkop') }}),
    stg_hemkop_promotion as (select * from {{ source('billigaste_kvittot_db', 'stg_hemkop_promotion') }})


SELECT 
    butiksnamn as store, --
    vecka as week, --
    hp.price__value as promotion_price, --
    h.price_unit as unit, --
    h.price_value as ordinary_price, --
    h.name as product_name, --
    h.google_analytics_category,
    str_split(h.google_analytics_category, '|')[1] AS category,
    str_split(h.google_analytics_category, '|')[2] AS category_group,
    h.image__url as image_url, --
    h.product_line2 as description, --
    h.display_volume as product_unit, --
    h.manufacturer as brand, --
    COALESCE(str_split(hp.redeem_limit_label, ' ')[2], '0') AS max_quantity,
    hp.qualifying_count as qualification_quantity, --
    h.code as promotion_id, --
    h.end_date as end_date --
FROM stg_hemkop_promotion hp
INNER JOIN stg_hemkop h
    ON hp._dlt_parent_id = h._dlt_id
WHERE hp.text_label != 'Alltid bra pris!'
    AND hp.text_label != 'Gäller endast online'
ORDER BY h.vecka ASC