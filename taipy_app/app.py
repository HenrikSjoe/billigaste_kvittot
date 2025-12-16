"""
Billigaste Kvittot - Taipy Application
A price comparison app for Swedish groceries
"""

import duckdb
import pandas as pd
from taipy.gui import Gui, notify

# Database connection
DB_PATH = "../database/billigaste_kvittot_db.duckdb"

# Global data
all_products_df = pd.DataFrame()
filtered_products_df = pd.DataFrame()
brands_list = []

# State variables
store_hemkop = True
store_coop = True
store_willys = True
store_citygross = True
selected_brand = "Alla märken"
search_text = ""
search_tags = []
cart_items = []
cart_count = 0
product_count = 0


def load_data():
    """Load all products from DuckDB"""
    global all_products_df, filtered_products_df, brands_list

    conn = duckdb.connect(DB_PATH, read_only=True)

    # Load all products
    query = """
    SELECT
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
    FROM marts.marts_all_stores
    WHERE promotion_price IS NOT NULL
    ORDER BY promotion_price ASC
    """

    all_products_df = conn.execute(query).fetchdf()
    filtered_products_df = all_products_df.copy()

    # Get unique brands, sorted
    brands = all_products_df['brand'].dropna().unique().tolist()
    brands_list = ["Alla märken"] + sorted(brands)

    conn.close()

    return all_products_df


def filter_products(state):
    """Filter products based on selected stores, brand, and search tags"""
    # Start with all products view (not a copy, use filtering directly)
    mask = pd.Series([True] * len(all_products_df))

    # Filter by stores
    selected_stores = []
    if state.store_hemkop:
        selected_stores.append("Hemköp")
    if state.store_coop:
        selected_stores.append("Coop")
    if state.store_willys:
        selected_stores.append("Willys")
    if state.store_citygross:
        selected_stores.append("City Gross")

    if selected_stores:
        mask &= all_products_df['store'].isin(selected_stores)

    # Filter by brand
    if state.selected_brand != "Alla märken":
        mask &= all_products_df['brand'] == state.selected_brand

    # Filter by search tags (only search in product_name for performance)
    if state.search_tags:
        for tag in state.search_tags:
            mask &= all_products_df['product_name'].str.contains(tag, case=False, na=False)

    state.filtered_products_df = all_products_df[mask].head(1000)  # Limit to 1000 results
    state.product_count = mask.sum()


def on_store_change(state):
    """Called when store checkboxes change"""
    filter_products(state)


def on_brand_change(state):
    """Called when brand dropdown changes"""
    filter_products(state)


def on_search(state):
    """Called when user presses Enter in search field"""
    if state.search_text.strip():
        tag = state.search_text.strip()
        if tag not in state.search_tags:
            state.search_tags.append(tag)
            state.search_text = ""
            filter_products(state)


def remove_tag(state, var_name, payload):
    """Remove a search tag"""
    tag_index = payload.get("index")
    if tag_index is not None and 0 <= tag_index < len(state.search_tags):
        removed_tag = state.search_tags.pop(tag_index)
        notify(state, "info", f"Tog bort sökning: {removed_tag}")
        filter_products(state)


def clear_search(state):
    """Clear all search tags"""
    state.search_tags = []
    state.search_text = ""
    filter_products(state)
    notify(state, "success", "Alla söktermer har rensats!")


def add_to_cart(state, var_name, payload):
    """Add product to cart"""
    product_id = payload.get("id")

    # Find product in filtered dataframe
    if product_id is not None:
        product = state.filtered_products_df.iloc[product_id]

        # Add to cart
        state.cart_items.append({
            "store": product["store"],
            "brand": product["brand"],
            "product_name": product["product_name"],
            "price": product["promotion_price"],
            "unit": product["unit"],
            "product_unit": product["product_unit"],
        })

        state.cart_count = len(state.cart_items)
        notify(state, "success", f"Lade till {product['product_name']} i varukorgen!")


# Taipy page layout
page = """
<|container|
# 🛒 Billigaste Kvittot

<|layout|columns=1fr 4fr|gap=20px|

<|part|class_name=sidebar|
## 🏪 Butiker
<|{store_hemkop}|toggle|label=Hemköp|on_change=on_store_change|>
<|{store_coop}|toggle|label=Coop|on_change=on_store_change|>
<|{store_willys}|toggle|label=Willys|on_change=on_store_change|>
<|{store_citygross}|toggle|label=City Gross|on_change=on_store_change|>

---

## 🏷️ Varumärke
<|{selected_brand}|selector|lov={brands_list}|dropdown|on_change=on_brand_change|>
|>

<|part|class_name=main-content|
<|layout|columns=1fr auto|gap=20px|

<|part|
## 🔍 Sök produkter
<|{search_text}|input|label=Sök efter produkt, märke, eller kategori|on_action=on_search|>

<|layout|columns=1fr auto|gap=10px|
<|part|
**Aktiva söktermer:** <|{search_tags}|>
|>
<|part|
<|Rensa söktermer|button|on_action=clear_search|>
|>
|>
|>

<|part|class_name=cart-icon|
🛒 <|{cart_count}|>
|>

|>

---

**Produkter: <|{product_count}|>**

<|{filtered_products_df}|table|page_size=25|page_size_options=10;25;50|columns=store;brand;product_name;promotion_price;unit;product_unit|width[store]=10%;width[brand]=15%;width[product_name]=35%;width[promotion_price]=10%;width[unit]=10%;width[product_unit]=10%|>

|>
|>
|>

<style>
.sidebar {
    background-color: #f5f5f5;
    padding: 20px;
    border-radius: 8px;
}

.main-content {
    padding: 20px;
}


.cart-icon {
    font-size: 24px;
    position: relative;
    display: flex;
    align-items: center;
    gap: 5px;
}

.cart-badge {
    background-color: #f44336;
    color: white;
    border-radius: 50%;
    padding: 2px 8px;
    font-size: 14px;
    font-weight: bold;
    min-width: 20px;
    text-align: center;
}
</style>
"""


if __name__ == "__main__":
    # Load initial data
    print("Loading data from DuckDB...")
    load_data()
    print(f"Loaded {len(all_products_df)} products")
    print(f"Found {len(brands_list)} brands")

    # Set initial product count
    product_count = len(filtered_products_df)

    # Create and run the GUI
    gui = Gui(page)
    gui.run(
        title="Billigaste Kvittot",
        port=5001,
        dark_mode=False,
        use_reloader=False,
        debug=False
    )
