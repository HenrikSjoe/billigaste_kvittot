with src_coop as (select * from {{ ref('src_coop') }})

select 
    store,
    week,
    brand,
    product_name,
    description,
    ordinary_price,
    promotion_price,
    unit,
    product_unit,
    qualification_quantity,
    max_quantity,
    category,
    category_group,
    end_date,
    image_url,
    promotion_id
from src_coop