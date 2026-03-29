from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3, random

app = Flask(__name__)
app.secret_key = "secret123"

def db():
    return sqlite3.connect("database.db")

def init_db():
    con = db()
    cur = con.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS shipments(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT,
        sender TEXT,
        receiver TEXT,
        status TEXT,
        location TEXT,
        delivery fee
    )
    """)

    con.commit()
    con.close()

init_db()

# HOME
@app.route("/")
def home():
    return render_template("index.html")

# REGISTER
@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        u = request.form.get("username")
        p = request.form.get("password")

        con = db()
        con.execute("INSERT INTO users(username,password) VALUES (?,?)",(u,p))
        con.commit()
        con.close()

        return redirect("/login")

    return render_template("register.html")

# LOGIN
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # 🔥 TEMP ADMIN LOGIN (guaranteed to work)
        if username == "admin" and password == "admin123":
            session["user"] = "admin"
            return redirect("/dashboard")
        else:
            return "Invalid login"

    return render_template("login.html")

# DASHBOARD
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/login")

    con = db()
    shipments = con.execute("SELECT * FROM shipments").fetchall()
    con.close()

    return render_template("dashboard.html", shipments=shipments)

# CREATE SHIPMENT
@app.route("/create", methods=["POST"])
def create():
    if "user" not in session:
        return redirect("/login")

    code = "AMX" + str(random.randint(100000,999999))

    sender = request.form.get("sender")
    receiver = request.form.get("receiver")
    location = request.form.get("location")
   delivery_fee = request.form.get("delivery_fee")

    try:
        con = db()
        con.execute("""
INSERT INTO shipments(code,sender,receiver,status,location,delivery_fee)
VALUES (?,?,?,?,?,?)
""",(code,sender,receiver,"In Transit",location,delivery_fee))
        con.commit()
        con.close()
    except Exception as e:
        return f"CREATE ERROR: {e}"

    return redirect("/dashboard")

# TRACK REDIRECT
@app.route("/track", methods=["POST"])
def track_redirect():
    code = request.form.get("code")
    return redirect(url_for("track", code=code))

# TRACK PAGE
@app.route("/track/<code>")
def track(code):
    con = db()
    shipment = con.execute(
        "SELECT * FROM shipments WHERE code=?",
        (code.strip(),)
    ).fetchone()
    con.close()

    if not shipment:
        return "Tracking code not found"

    return render_template("track.html", s=shipment)

# ABOUT
@app.route("/about")
def about():
    return render_template("about.html")

# FAQ
@app.route("/faq")
def faq():
    return render_template("faq.html")

# ❌ REMOVE app.run()
