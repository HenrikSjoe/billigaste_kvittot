with src_city_gross as (select * from {{ ref('src_city_gross') }})

select 
    store,
    week,
    COALESCE(brand,country_of_origin ) as brand,
    product_name,
    description,
    round(ordinary_price, 2) as ordinary_price,
    round(promotion_price, 2) as promotion_price,
    unit,
    product_unit,
    qualification_quantity,
    max_quantity,
    category,
    category_group,
    end_date,
    image_url,
    promotion_id
from src_city_gross