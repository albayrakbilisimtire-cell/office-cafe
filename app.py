from flask import Flask, render_template, request, redirect, session, send_file
from werkzeug.utils import secure_filename
from db import get_db
import os
import pandas as pd

app = Flask(__name__)
app.secret_key = "office-cafe"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ---------------- LOGIN ----------------

@app.route("/", methods=["GET", "POST"])
def login():
    if session.get("user_id"):
        if session["role"] == "admin":
            return redirect("/admin")
        elif session["role"] == "cafe":
            return redirect("/kitchen")
        else:
            return redirect("/user")

    if request.method == "POST":
        db = get_db()
        user = db.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (request.form["username"], request.form["password"])
        ).fetchone()

        if user:
            session["user_id"] = user["id"]
            session["role"] = user["role"]
            session["room"] = user["room"]

            if user["role"] == "admin":
                return redirect("/admin")
            elif user["role"] == "cafe":
                return redirect("/kitchen")
            else:
                return redirect("/user")

        return render_template("login.html", error="Hatalı giriş")

    return render_template("login.html")

# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# ---------------- ADMIN ----------------
@app.route("/admin")
def admin():
    if session.get("role") != "admin":
        return redirect("/")
    return render_template("admin_index.html")

@app.route("/admin/orders")
def admin_orders():
    if session.get("role") != "admin":
        return redirect("/")

    db = get_db()
    orders = db.execute("""
        SELECT 
            orders.id,
            users.room,
            products.name AS product,
            orders.option,
            orders.qty,
            orders.status,
            orders.created_at
        FROM orders
        JOIN users ON users.id = orders.user_id
        JOIN products ON products.id = orders.product_id
        ORDER BY orders.created_at DESC
    """).fetchall()

    return render_template("admin_orders.html", orders=orders)

# ---------------- USERS ----------------
@app.route("/admin/users", methods=["GET", "POST"])
def admin_users():
    if session.get("role") != "admin":
        return redirect("/")

    db = get_db()

    if request.method == "POST":
        db.execute(
            "INSERT INTO users (username,password,role,room) VALUES (?,?,?,?)",
            (
                request.form["u"],
                request.form["p"],
                request.form["r"],
                request.form["room"]
            )
        )
        db.commit()

    users = db.execute("SELECT * FROM users").fetchall()
    return render_template("admin_users.html", users=users)


@app.route("/admin/users/delete/<int:id>")
def delete_user(id):
    if session.get("role") != "admin":
        return redirect("/")

    db = get_db()
    db.execute("DELETE FROM users WHERE id=?", (id,))
    db.commit()
    return redirect("/admin/users")


# ---------------- PRODUCTS ----------------
@app.route("/admin/products", methods=["GET", "POST"])
def admin_products():
    if session.get("role") != "admin":
        return redirect("/")

    db = get_db()

    if request.method == "POST":
        name = request.form["name"]
        has_options = 1 if request.form.get("has_options") else 0

        image_path = None
        file = request.files.get("image")
        if file and file.filename:
            filename = secure_filename(file.filename)
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            image_path = f"static/uploads/{filename}"

        cur = db.execute(
            "INSERT INTO products (name, image, has_options) VALUES (?,?,?)",
            (name, image_path, has_options)
        )
        product_id = cur.lastrowid

        if has_options:
            options = request.form.getlist("options[]")
            for opt in options:
                if opt.strip():
                    db.execute(
                        "INSERT INTO product_options (product_id, value) VALUES (?,?)",
                        (product_id, opt.strip())
                    )

        db.commit()

    products = db.execute("SELECT * FROM products").fetchall()
    return render_template("admin_products.html", products=products)


@app.route("/admin/products/delete/<int:id>")
def delete_product(id):
    if session.get("role") != "admin":
        return redirect("/")

    db = get_db()
    db.execute("DELETE FROM products WHERE id=?", (id,))
    db.commit()
    return redirect("/admin/products")


# ---------------- USER ----------------
@app.route("/user")
def user():
    if "user_id" not in session:
        return redirect("/")

    db = get_db()
    products = db.execute("SELECT * FROM products").fetchall()

    product_list = []
    for p in products:
        opts = db.execute(
            "SELECT value FROM product_options WHERE product_id=?",
            (p["id"],)
        ).fetchall()

        product_list.append({
            "id": p["id"],
            "name": p["name"],
            "image": p["image"],
            "options": [o["value"] for o in opts]
        })

    rooms = db.execute(
        "SELECT DISTINCT room FROM users WHERE room IS NOT NULL"
    ).fetchall()

    return render_template(
        "user_index.html",
        products=product_list,
        rooms=rooms
    )


# ---------------- ORDER ----------------
@app.route("/order", methods=["POST"])
def order():
    if "user_id" not in session:
        return redirect("/")

    db = get_db()
    room = request.form.get("room")

    for key, value in request.form.items():
        if key.startswith("qty_") and int(value) > 0:
            _, pid, opt = key.split("_", 2)

            db.execute("""
                INSERT INTO orders (user_id, product_id, option, qty, room)
                VALUES (?,?,?,?,?)
            """, (
                session["user_id"],
                pid,
                opt if opt != "none" else None,
                int(value),
                room
            ))

    db.commit()
    return redirect("/user")

# ---------------- KITCHEN ----------------
@app.route("/kitchen")
def kitchen():
    if session.get("role") != "cafe":
        return redirect("/")

    db = get_db()
    orders = db.execute("""
        SELECT
            orders.id,
            orders.room,
            products.name AS product,
            orders.option,
            orders.qty,
            orders.status,
            orders.created_at
        FROM orders
        JOIN products ON products.id = orders.product_id
        WHERE orders.status != 'teslim edildi'
        ORDER BY orders.created_at ASC
    """).fetchall()

    return render_template("kitchen.html", orders=orders)

@app.route("/order/status/<int:id>/<status>")
def order_status(id, status):
    if session.get("role") != "cafe":
        return redirect("/")

    db = get_db()
    db.execute(
        "UPDATE orders SET status=? WHERE id=?",
        (status, id)
    )
    db.commit()
    return redirect("/kitchen")

@app.route("/kitchen/count")
def kitchen_count():
    db = get_db()
    c = db.execute(
        "SELECT COUNT(*) FROM orders WHERE status!='teslim edildi'"
    ).fetchone()[0]
    return {"count": c}

# ---------------- EXPORT ----------------
@app.route("/admin/export")
def export():
    if session.get("role") != "admin":
        return redirect("/")

    db = get_db()
    df = pd.read_sql("SELECT * FROM orders", db)

    os.makedirs("exports", exist_ok=True)
    path = "exports/orders.xlsx"
    df.to_excel(path, index=False)

    return send_file(path, as_attachment=True)


# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
