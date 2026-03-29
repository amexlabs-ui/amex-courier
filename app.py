from flask import Flask, render_template, request, redirect, session
import sqlite3, random

app = Flask(__name__)
app.secret_key = "secret123"

DB = "database.db"

# ================= DATABASE =================
def init_db():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS shipments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tracking_code TEXT,
        sender TEXT,
        receiver TEXT,
        status TEXT,
        location TEXT,
        delivery_address TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()

# ================= ROUTES =================

@app.route("/")
def home():
    return render_template("index.html")

# -------- REGISTER --------
@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect(DB)
        cur = conn.cursor()
        cur.execute("INSERT INTO users (username,password) VALUES (?,?)",(username,password))
        conn.commit()
        conn.close()

        return redirect("/login")

    return render_template("register.html")

# -------- LOGIN --------
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect(DB)
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username=? AND password=?",(username,password))
        user = cur.fetchone()
        conn.close()

        if user:
            session["user"] = username
            return redirect("/dashboard")
        else:
            return "Invalid credentials"

    return render_template("login.html")

# -------- DASHBOARD --------
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/login")

    return render_template("admin.html")

# -------- CREATE SHIPMENT --------
@app.route("/create", methods=["POST"])
def create():
    try:
        tracking = "AMX" + str(random.randint(100000,999999))

        sender = request.form["sender"]
        receiver = request.form["receiver"]
        status = request.form["status"]
        location = request.form["location"]
        address = request.form["delivery_address"]

        conn = sqlite3.connect(DB)
        cur = conn.cursor()

        cur.execute("""
        INSERT INTO shipments 
        (tracking_code,sender,receiver,status,location,delivery_address)
        VALUES (?,?,?,?,?,?)
        """,(tracking,sender,receiver,status,location,address))

        conn.commit()
        conn.close()

        return f"Tracking Code Created: {tracking}"

    except Exception as e:
        return f"ERROR: {str(e)}"

# -------- TRACK --------
@app.route("/track")
def track_redirect():
    code = request.args.get("code").strip()
    return redirect(f"/track/{code}")

@app.route("/track/<code>")
def track(code):
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("SELECT * FROM shipments WHERE tracking_code=?", (code,))
    data = cur.fetchone()
    conn.close()

    if not data:
        return "Tracking not found"

    return render_template("track.html", data=data)

# -------- ABOUT --------
@app.route("/about")
def about():
    return render_template("about.html")

# -------- FAQ --------
@app.route("/faq")
def faq():
    return render_template("faq.html")

# ================= RUN =================
if __name__ == "__main__":
    app.run(debug=True)
