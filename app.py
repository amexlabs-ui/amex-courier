from flask import Flask, render_template, request, redirect
import sqlite3
import random

app = Flask(__name__)

DB = "database.db"

# ---------- DATABASE INIT ----------
def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS shipments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tracking TEXT,
        sender TEXT,
        receiver TEXT,
        address TEXT,
        weight TEXT,
        fee TEXT,
        status TEXT,
        location TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()

# ---------- HOME ----------
@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        code = request.form.get("tracking", "").strip().upper()
        return redirect(f"/track/{code}")

    return render_template("index.html")

# ---------- TRACK ----------
@app.route("/track")
def track_redirect():
    code = request.args.get("code", "").strip()
    return redirect(f"/track/{code}")
    
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("SELECT * FROM shipments WHERE tracking_code=?", (code,))
    shipment = cur.fetchone()

    conn.close()

    if not shipment:
        return "Tracking code not found", 404

    return render_template("track.html", shipment=shipment)

# ---------------- REGISTER ----------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        conn = sqlite3.connect(DB)
        c = conn.cursor()
        try:
            c.execute("INSERT INTO users (username, password) VALUES (?, ?)",
                      (request.form["username"], request.form["password"]))
            conn.commit()
        except:
            pass
        conn.close()
        return redirect("/login")
    return render_template("register.html")

# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        if username == "admin" and password == "admin123":
            session["admin"] = True
            return redirect("/dashboard")

        conn = sqlite3.connect(DB)
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = c.fetchone()
        conn.close()

        if user:
            session["user_id"] = user[0]
            return redirect("/user-dashboard")

    return render_template("login.html")
    
# ---------- ADMIN DASHBOARD ----------
@app.route("/admin", methods=["GET", "POST"])
def admin():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    if request.method == "POST":
        tracking = "AMX" + str(random.randint(100000, 999999))
        sender = request.form["sender"]
        receiver = request.form["receiver"]
        address = request.form["address"]
        weight = request.form["weight"]
        fee = request.form["fee"]
        status = request.form["status"]
        location = request.form["location"]

        cur.execute("""
INSERT INTO shipments (
    tracking_code, sender, receiver, status,
    location, delivery_address
) VALUES (?, ?, ?, ?, ?, ?)
""", (
    tracking_code, sender, receiver, status,
    location, delivery_address
))
        
        conn.commit()

    c.execute("SELECT * FROM shipments ORDER BY id DESC")
    shipments = c.fetchall()

    conn.close()

    return render_template("admin.html", shipments=shipments)

# ---------- RUN ----------
if __name__ == "__main__":
    app.run(debug=True)
