from pathlib import Path
from datetime import date
from flask import Flask, render_template, request
import duckdb
import datetime

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR.parent / "database" / "billigaste_kvittot_db.duckdb"
#DB_PATH = Path("/mnt/data/billigaste_kvittot.duckdb")

app = Flask(__name__)

def safe_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None

STORE_LOGOS = {
    "City Gross": "city_gross.png",
    "Coop": "coop.png",
    "Hemköp": "hemkop.png",
    "Willys": "willys.png",
}


def get_products(filters):
    con = duckdb.connect(DB_PATH, read_only=True)
    today = date.today().isoformat()

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
        image_url
    FROM marts.marts_all_stores
    WHERE promotion_price IS NOT NULL
      AND end_date >= ?
    """

    params = [today]

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

    df = con.execute(query, params).fetchdf()
    con.close()

    products = df.to_dict("records")

    for p in products:
        # ---- Typ-säkring ----
        p["promotion_price"] = safe_float(p.get("promotion_price"))
        p["ordinary_price"] = safe_float(p.get("ordinary_price"))
        p["qualification_quantity"] = int(p.get("qualification_quantity") or 1)
        p["max_quantity"] = int(p.get("max_quantity") or 0)
        p["product_unit"] = str(p.get("product_unit"))

        # ---- Promo text (X för Y) ----
        if p["qualification_quantity"] > 1 and p["promotion_price"] is not None:
            p["promo_text"] = (
                f"{p['qualification_quantity']} för "
                f"{p['promotion_price']:.2f}".replace(".", ",")
                + " kr"
            )
        else:
            p["promo_text"] = None

        # ---- Formatterade priser ----
        if p["promotion_price"] is not None:
            p["promotion_price_fmt"] = (
                f"{p['promotion_price']:.2f}".replace(".", ",")
            )
        else:
            p["promotion_price_fmt"] = None

        if p["ordinary_price"] is not None:
            p["ordinary_price_fmt"] = (
                f"{p['ordinary_price']:.2f}".replace(".", ",")
            )
        else:
            p["ordinary_price_fmt"] = None

        # ---- Butikslogga ----
        p["store_logo"] = STORE_LOGOS.get(p.get("store"), "")

    return products


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
        week = datetime.date.today().isocalendar()[1],
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)