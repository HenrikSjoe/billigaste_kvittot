with 
    stg_willys as (select * from {{ source('billigaste_kvittot_db', 'stg_willys') }}),
    stg_willys_promotion as (select * from {{ source('billigaste_kvittot_db', 'stg_willys_promotion') }})


SELECT 
    butiksnamn as store, --
    vecka as week, --
    wp.price__value * coalesce(wp.qualifying_count, 1) as promotion_price, --
    w.price_unit as unit, --
    w.price_value as ordinary_price, --
    w.name as product_name, --
    w.google_analytics_category AS category,
    w.google_analytics_category AS category_group,
    w.image__url as image_url, --
    w.product_line2 as description, --
    w.display_volume as product_unit, --
    COALESCE(([upper (x[1])||x[2:] 
      for x in 
      (w.manufacturer).string_split(' ')]).list_aggr('string_agg',' '), 'Varumärke: Okänt') as brand,
    COALESCE(str_split(wp.redeem_limit_label, ' ')[2], '0') AS max_quantity,
    wp.qualifying_count as qualification_quantity, --
    w.code as promotion_id, --
    w.end_date as end_date --
FROM stg_willys_promotion wp
INNER JOIN stg_willys w
    ON wp._dlt_parent_id = w._dlt_id
WHERE wp.text_label != 'Alltid bra pris!'
    AND wp.text_label != 'Gäller endast online'
ORDER BY w.vecka ASC