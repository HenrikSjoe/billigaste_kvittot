from pathlib import Path
from flask import Flask, render_template, request
import duckdb

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR.parent / "database" / "billigaste_kvittot_db.duckdb"

# Point Flask at the directory that holds index.html and static assets
app = Flask(
    __name__,
    template_folder=str(BASE_DIR),
    static_folder=str(BASE_DIR),
)


def get_products(filters):
    con = duckdb.connect(DB_PATH, read_only=True)

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
        category,
        category_group,
        end_date,
        image_url
    FROM marts.marts_all_stores
    WHERE promotion_price IS NOT NULL
    """

    params = []

    if filters["stores"]:
        query += " AND store IN ({})".format(
            ",".join(["?"] * len(filters["stores"]))
        )
        params.extend(filters["stores"])

    if filters["brand"] and filters["brand"] != "Alla":
        query += " AND brand = ?"
        params.append(filters["brand"])

    if filters["search"]:
        query += " AND LOWER(product_name) LIKE ?"
        params.append(f"%{filters['search'].lower()}%")

    query += " ORDER BY promotion_price ASC LIMIT 200"

    df = con.execute(query, params).fetchdf()
    con.close()

    return df.to_dict("records")


def get_brands():
    con = duckdb.connect(DB_PATH, read_only=True)
    brands = con.execute("""
        SELECT DISTINCT brand
        FROM marts.marts_all_stores
        WHERE brand IS NOT NULL
        ORDER BY brand
    """).fetchdf()["brand"].tolist()
    con.close()
    return ["Alla"] + brands


@app.route("/")
def index():
    filters = {
        "stores": request.args.getlist("store"),
        "brand": request.args.get("brand"),
        "search": request.args.get("search", "").strip(),
    }

    products = get_products(filters)
    brands = get_brands()

    return render_template(
        "index.html",
        products=products,
        brands=brands,
        filters=filters,
        product_count=len(products),
    )


if __name__ == "__main__":
    app.run(debug=True)
