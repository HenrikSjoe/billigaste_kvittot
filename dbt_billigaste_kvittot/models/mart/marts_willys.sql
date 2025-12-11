with src_willys as (select * from {{ ref('src_willys') }})

select 
    store,
    week,
    COALESCE(brand,'Okänt') as brand,
    product_name,
    description,
    round(ordinary_price, 2) as ordinary_price,
    round(promotion_price, 2) as promotion_price,
    unit,
    product_unit,
    COALESCE(qualification_quantity,1) as qualification_quantity,
    max_quantity,
    category,
    category_group,
    end_date,
    image_url,
    promotion_id
from src_willys