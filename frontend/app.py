from pathlib import Path
from datetime import date
from flask import Flask, render_template, request, session, redirect, url_for
import duckdb
import datetime
import os
import hashlib

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR.parent / "database" / "billigaste_kvittot_db.duckdb"
#DB_PATH = Path("/mnt/data/billigaste_kvittot.duckdb")

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-prod")

def safe_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def make_product_id(store, product_name, brand):
    """Skapa ett unikt produkt-ID baserat på butik och produktnamn."""
    key = f"{store}:{product_name}:{brand}"
    return hashlib.md5(key.encode()).hexdigest()[:12]

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
        promotion_id,
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

    if filters["brands"]:
        query += " AND brand IN ({})".format(
            ",".join(["?"] * len(filters["brands"]))
        )
        params.extend(filters["brands"])

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

        # ---- Unikt produkt-ID ----
        p["product_id"] = make_product_id(p["store"], p["product_name"], p["brand"])

    return products


def get_brands(stores=None):
    con = duckdb.connect(DB_PATH, read_only=True)

    if stores:
        query = """
            SELECT DISTINCT brand
            FROM marts.marts_all_stores
            WHERE brand IS NOT NULL
              AND store IN ({})
            ORDER BY brand
        """.format(",".join(["?"] * len(stores)))
        brands = con.execute(query, stores).fetchdf()["brand"].tolist()
    else:
        brands = con.execute("""
            SELECT DISTINCT brand
            FROM marts.marts_all_stores
            WHERE brand IS NOT NULL
            ORDER BY brand
        """).fetchdf()["brand"].tolist()

    con.close()
    return brands


@app.route("/")
def index():
    filters = {
        "stores": request.args.getlist("store"),
        "brands": request.args.getlist("brand"),
        "search": request.args.get("search", "").strip(),
    }

    products = get_products(filters)
    brands = get_brands(filters["stores"])

    return render_template(
        "index.html",
        products=products,
        brands=brands,
        filters=filters,
        product_count=len(products),
        week = datetime.date.today().isocalendar()[1],
        cart_count=len(session.get("cart", [])),
    )


@app.route("/cart/add/<product_id>")
def cart_add(product_id):
    """Lägg till en produkt i varukorgen."""
    if "cart" not in session:
        session["cart"] = []

    # Kolla om produkten redan finns i korgen
    if product_id not in session["cart"]:
        session["cart"] = session["cart"] + [product_id]

    # Redirect tillbaka till föregående sida
    return redirect(request.referrer or url_for("index"))


@app.route("/cart/remove/<product_id>")
def cart_remove(product_id):
    """Ta bort en produkt från varukorgen."""
    if "cart" in session:
        cart = session["cart"]
        if product_id in cart:
            cart.remove(product_id)
            session["cart"] = cart

    return redirect(request.referrer or url_for("cart"))


@app.route("/cart/clear")
def cart_clear():
    """Töm varukorgen."""
    session["cart"] = []
    session.modified = True
    return redirect(url_for("index"))


@app.route("/cart")
def cart():
    """Visa varukorgen grupperad per butik."""
    cart_ids = session.get("cart", [])

    if not cart_ids:
        return render_template(
            "cart.html",
            cart_by_store={},
            total=0,
            cart_count=0,
        )

    # Hämta alla produkter och filtrera på product_id
    con = duckdb.connect(DB_PATH, read_only=True)
    today = date.today().isoformat()
    query = """
    SELECT store, brand, product_name, promotion_price, unit, image_url
    FROM marts.marts_all_stores
    WHERE promotion_price IS NOT NULL
      AND end_date >= ?
    """
    df = con.execute(query, [today]).fetchdf()
    con.close()

    all_products = df.to_dict("records")

    # Filtrera produkter som finns i varukorgen
    products = []
    for p in all_products:
        p["product_id"] = make_product_id(p["store"], p["product_name"], p["brand"])
        if p["product_id"] in cart_ids:
            products.append(p)

    # Gruppera per butik
    cart_by_store = {}
    total = 0
    for p in products:
        store = p["store"]
        if store not in cart_by_store:
            cart_by_store[store] = {"products": [], "subtotal": 0}
        cart_by_store[store]["products"].append(p)
        price = p["promotion_price"] or 0
        cart_by_store[store]["subtotal"] += price
        total += price

    # Sortera efter totalsumma (lägst först)
    cart_by_store = dict(sorted(cart_by_store.items(), key=lambda x: x[1]["subtotal"]))

    return render_template(
        "cart.html",
        cart_by_store=cart_by_store,
        total=total,
        cart_count=len(cart_ids),
        store_logos=STORE_LOGOS,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)