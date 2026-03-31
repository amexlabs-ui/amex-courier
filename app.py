from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3
import random
import os

app = Flask(__name__)
app.secret_key = "amex-secret-key"

DB_PATH = "/data/database.db" if os.path.isdir("/data") else "database.db"


# ---------------- DATABASE HELPER ----------------
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return render_template("dashboard.html", shipments=shipments, error=error_if_any)


def ensure_column(conn, table_name, column_name, column_type):
    cols = conn.execute(f"PRAGMA table_info({table_name})").fetchall()
    names = [c["name"] for c in cols]
    if column_name not in names:
        conn.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}")


def init_db():
    conn = get_db()

    conn.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        role TEXT DEFAULT 'customer'
    )
    """)

    conn.execute("""
    CREATE TABLE IF NOT EXISTS shipments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tracking_code TEXT UNIQUE,
        sender TEXT,
        receiver TEXT,
        status TEXT,
        location TEXT
    )
    """)

    conn.execute("""
    CREATE TABLE IF NOT EXISTS history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tracking_code TEXT,
        status TEXT,
        location TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Safe schema upgrades
    ensure_column(conn, "shipments", "delivery_address", "TEXT")
    ensure_column(conn, "shipments", "weight", "TEXT")
    ensure_column(conn, "shipments", "delivery_fee", "TEXT")
    ensure_column(conn, "shipments", "description", "TEXT")

    admin = conn.execute(
        "SELECT * FROM users WHERE username = ?",
        ("admin",)
    ).fetchone()

    if not admin:
        conn.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            ("admin", "admin123", "admin")
        )

    conn.commit()
    conn.close()


init_db()


# ---------------- HELPERS ----------------
def generate_tracking_code():
    conn = get_db()
    while True:
        code = "AMX" + str(random.randint(100000, 999999))
        exists = conn.execute(
            "SELECT 1 FROM shipments WHERE tracking_code = ?",
            (code,)
        ).fetchone()
        if not exists:
            conn.close()
            return code


def get_status_class(status):
    if not status:
        return "processing"

    s = status.strip().lower()
    mapping = {
        "processing": "processing",
        "in transit": "in-transit",
        "out for delivery": "out-for-delivery",
        "delivered": "delivered",
        "cancelled": "cancelled",
        "canceled": "cancelled",
        "delayed": "delayed",
    }
    return mapping.get(s, "processing")


# ---------------- ROUTES ----------------
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if not username or not password:
            return render_template("register.html", error="Please fill in all fields.")

        conn = get_db()
        existing = conn.execute(
            "SELECT * FROM users WHERE username = ?",
            (username,)
        ).fetchone()

        if existing:
            conn.close()
            return render_template("register.html", error="Username already exists.")

        conn.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            (username, password, "customer")
        )
        conn.commit()
        conn.close()

        return redirect("/login")

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        conn = get_db()
        user = conn.execute(
            "SELECT * FROM users WHERE username = ? AND password = ?",
            (username, password)
        ).fetchone()
        conn.close()

        if not user:
            return render_template("login.html", error="Invalid username or password.")

        session["user_id"] = user["id"]
        session["username"] = user["username"]
        session["role"] = user["role"]

        if user["role"] == "admin":
            return redirect("/dashboard")

        return redirect("/")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@app.route("/dashboard")
def dashboard():
    if session.get("role") != "admin":
        return redirect("/login")

    conn = get_db()
    shipments = conn.execute(
        "SELECT * FROM shipments ORDER BY id DESC"
    ).fetchall()
    conn.close()

    return render_template(
        "dashboard.html",
        shipments=shipments,
        get_status_class=get_status_class
    )


# CREATE ROUTE SAVES INTO tracking_code
@app.route("/create", methods=["POST"])
def create():
    if session.get("role") != "admin":
        return redirect("/login")

    try:
        tracking_code = generate_tracking_code()

        sender = request.form.get("sender", "").strip()
        receiver = request.form.get("receiver", "").strip()
        status = request.form.get("status", "Processing").strip()
        location = request.form.get("location", "").strip()
        delivery_address = request.form.get("delivery_address", "").strip()
        weight = request.form.get("weight", "").strip()
        delivery_fee = request.form.get("delivery_fee", "").strip()
        description = request.form.get("description", "").strip()

        if not sender or not receiver or not location:
            conn = get_db()
            shipments = conn.execute("SELECT * FROM shipments ORDER BY id DESC").fetchall()
            conn.close()
            return render_template(
                "dashboard.html",
                shipments=shipments,
                get_status_class=get_status_class,
                error="Sender, receiver, and current location are required."
            )

        conn = get_db()

        conn.execute("""
            INSERT INTO shipments (
                tracking_code, sender, receiver, status, location,
                delivery_address, weight, delivery_fee, description
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            tracking_code, sender, receiver, status, location,
            delivery_address, weight, delivery_fee, description
        ))

        conn.execute("""
            INSERT INTO history (tracking_code, status, location)
            VALUES (?, ?, ?)
        """, (tracking_code, status, location))

        conn.commit()
        conn.close()

        return redirect("/dashboard")

    except Exception as e:
        conn = get_db()
        shipments = conn.execute("SELECT * FROM shipments ORDER BY id DESC").fetchall()
        conn.close()
        return render_template(
            "dashboard.html",
            shipments=shipments,
            get_status_class=get_status_class,
            error=f"Create error: {e}"
        )


@app.route("/update/<tracking_code>", methods=["POST"])
def update(tracking_code):
    if session.get("role") != "admin":
        return redirect("/login")

    try:
        status = request.form.get("status", "").strip()
        location = request.form.get("location", "").strip()

        if not status or not location:
            return redirect("/dashboard")

        conn = get_db()
        conn.execute("""
            UPDATE shipments
            SET status = ?, location = ?
            WHERE tracking_code = ?
        """, (status, location, tracking_code))

        conn.execute("""
            INSERT INTO history (tracking_code, status, location)
            VALUES (?, ?, ?)
        """, (tracking_code, status, location))

        conn.commit()
        conn.close()

        return redirect("/dashboard")

    except Exception as e:
        conn = get_db()
        shipments = conn.execute("SELECT * FROM shipments ORDER BY id DESC").fetchall()
        conn.close()
        return render_template(
            "dashboard.html",
            shipments=shipments,
            get_status_class=get_status_class,
            error=f"Update error: {e}"
        )


# HOMEPAGE FORM POSTS HERE
@app.route("/track", methods=["POST"])
def track_redirect():
    code = request.form.get("code", "").strip().upper()
    if not code:
        return redirect("/")
    return redirect(url_for("track_code", code=code))


@app.route("/track/<code>")
def track_code(code):
    code = code.strip().upper()

    conn = get_db()

    shipment = conn.execute("""
        SELECT * FROM shipments
        WHERE UPPER(TRIM(tracking_code)) = ?
    """, (code,)).fetchone()

    history = conn.execute("""
        SELECT * FROM history
        WHERE UPPER(TRIM(tracking_code)) = ?
        ORDER BY id DESC
    """, (code,)).fetchall()

    conn.close()

    return render_template(
        "track.html",
        shipment=shipment,
        history=history,
        get_status_class=get_status_class
    )


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/faq")
def faq():
    return render_template("faq.html")
