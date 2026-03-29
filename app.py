from flask import Flask, render_template, request, redirect, session
import sqlite3, random, string

app = Flask(__name__)
app.secret_key = "secret123"

def db():
    return sqlite3.connect("database.db")

# AUTO CREATE TABLES
def init_db():
    con = db()
    cur = con.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY,
        username TEXT,
        password TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS shipments(
        id INTEGER PRIMARY KEY,
        code TEXT,
        sender TEXT,
        receiver TEXT,
        status TEXT,
        location TEXT,
        lat REAL,
        lng REAL
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
        u = request.form["username"]
        p = request.form["password"]

        con = db()
        con.execute("INSERT INTO users(username,password) VALUES (?,?)",(u,p))
        con.commit()
        con.close()

        return redirect("/login")

    return render_template("register.html")

# LOGIN
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        u = request.form["username"]
        p = request.form["password"]

        con = db()
        user = con.execute("SELECT * FROM users WHERE username=? AND password=?",(u,p)).fetchone()
        con.close()

        if user:
            session["user"] = u
            return redirect("/dashboard")

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
    code = "AMX" + str(random.randint(100000,999999))

    sender = request.form["sender"]
    receiver = request.form["receiver"]
    location = request.form["location"]

    lat = float(request.form["lat"])
    lng = float(request.form["lng"])

    con = db()
    con.execute("""
    INSERT INTO shipments(code,sender,receiver,status,location,lat,lng)
    VALUES (?,?,?,?,?,?,?)
    """,(code,sender,receiver,"In Transit",location,lat,lng))
    con.commit()
    con.close()

    return redirect("/dashboard")

# TRACK
@app.route("/track/<code>")
def track(code):
    con = db()
    shipment = con.execute("SELECT * FROM shipments WHERE code=?",(code.strip(),)).fetchone()
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

app.run()
