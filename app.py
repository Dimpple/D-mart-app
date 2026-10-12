import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-only-change-me")

DB_PATH = "/app/data/dmart.db"


def get_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_database():
    with get_db() as conn:
        with open("database/init.sql", encoding="utf-8") as file:
            conn.executescript(file.read())


@app.route("/")
def index():
    with get_db() as conn:
        items = conn.execute(
            "SELECT id, name, price, stock FROM items ORDER BY id"
        ).fetchall()

    cart = session.get("cart", {})
    cart_items = []
    total = 0.0

    with get_db() as conn:
        for item_id, quantity in cart.items():
            item = conn.execute(
                "SELECT id, name, price FROM items WHERE id = ?",
                (int(item_id),)
            ).fetchone()

            if item:
                subtotal = item["price"] * quantity
                cart_items.append({
                    "id": item["id"],
                    "name": item["name"],
                    "price": item["price"],
                    "quantity": quantity,
                    "subtotal": subtotal
                })
                total += subtotal

    bill = session.pop("last_bill", None)

    return render_template(
        "index.html",
        items=items,
        cart_items=cart_items,
        total=total,
        bill=bill
    )


@app.route("/add", methods=["POST"])
def add_to_cart():
    item_id = request.form.get("item_id", type=int)
    quantity = request.form.get("quantity", type=int)

    if not item_id or not quantity or quantity < 1:
        return "Enter a valid item and quantity.", 400

    with get_db() as conn:
        item = conn.execute(
            "SELECT id, stock FROM items WHERE id = ?",
            (item_id,)
        ).fetchone()

    if not item:
        return "Item not found.", 404

    cart = session.get("cart", {})
    current_quantity = cart.get(str(item_id), 0)

    if current_quantity + quantity > item["stock"]:
        return "Requested quantity exceeds available stock.", 400

    cart[str(item_id)] = current_quantity + quantity
    session["cart"] = cart

    return redirect(url_for("index"))


@app.route("/remove/<int:item_id>", methods=["POST"])
def remove_from_cart(item_id):
    cart = session.get("cart", {})
    cart.pop(str(item_id), None)
    session["cart"] = cart
    return redirect(url_for("index"))


@app.route("/checkout", methods=["POST"])
def checkout():
    cart = session.get("cart", {})
    bill_items = []
    total = 0.0

    with get_db() as conn:
        for item_id, quantity in cart.items():
            item = conn.execute(
                "SELECT id, name, price, stock FROM items WHERE id = ?",
                (int(item_id),)
            ).fetchone()

            if not item or quantity > item["stock"]:
                return "An item is unavailable or stock has changed.", 400

            subtotal = item["price"] * quantity
            bill_items.append({
                "name": item["name"],
                "price": item["price"],
                "quantity": quantity,
                "subtotal": subtotal
            })
            total += subtotal

        # Deduct stock only when the bill is generated.
        for item_id, quantity in cart.items():
            conn.execute(
                "UPDATE items SET stock = stock - ? WHERE id = ?",
                (quantity, int(item_id))
            )

    session["last_bill"] = {
        "items": bill_items,
        "total": total
    }
    session["cart"] = {}

    return redirect(url_for("index"))


if __name__ == "__main__":
    initialize_database()
    app.run(host="0.0.0.0", port=5000, debug=False)
