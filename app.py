from flask import Flask, render_template_string, request, redirect, session
import sqlite3
import random
import string

app = Flask(__name__)
app.secret_key = "secret123"


# ---------------- DB INIT ----------------
def init_db():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS shipments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tracking_code TEXT,
        sender TEXT,
        receiver TEXT,
        status TEXT,
        location TEXT,
        weight TEXT,
        fee TEXT,
        description TEXT,
        delivery_address TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tracking_code TEXT,
        status TEXT,
        location TEXT
    )
    """)

    c.execute("INSERT OR IGNORE INTO users (id, username, password) VALUES (1, 'admin', 'admin123')")

    conn.commit()
    conn.close()


init_db()


# ---------------- GENERATE TRACKING ----------------
def generate_code():
    return "AMX" + ''.join(random.choices(string.digits, k=6))


# ---------------- HOME ----------------
@app.route("/", methods=["GET", "POST"])
def home():
    shipment = None

    if request.method == "POST":
        code = request.form["tracking"]
        conn = sqlite3.connect("database.db")
        c = conn.cursor()

        c.execute("SELECT * FROM shipments WHERE tracking_code=?", (code,))
        shipment = c.fetchone()

        c.execute("SELECT status, location FROM history WHERE tracking_code=?", (code,))
        history = c.fetchall()

        conn.close()

        if shipment:
            return render_template_string("""
            <h2>Tracking: {{s[1]}}</h2>
            <p>Status: {{s[4]}}</p>
            <p>Location: {{s[5]}}</p>
            <p>Sender: {{s[2]}}</p>
            <p>Receiver: {{s[3]}}</p>
            <p>Weight: {{s[6]}}</p>
            <p>Fee: {{s[7]}}</p>
            <p>Delivery Address: {{s[9]}}</p>

            <h3>History</h3>
            {% for h in history %}
                <p>{{h[0]}} - {{h[1]}}</p>
            {% endfor %}
            """, s=shipment, history=history)

    return """
    <h1>Amex Courier</h1>
    <form method="POST">
        <input name="tracking" placeholder="Enter tracking code">
        <button>Track</button>
    </form>
    <a href="/login">Admin Login</a>
    """


# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        u = request.form["username"]
        p = request.form["password"]

        conn = sqlite3.connect("database.db")
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (u, p))
        user = c.fetchone()
        conn.close()

        if user:
            session["user"] = u
            return redirect("/admin")

    return """
    <h2>Login</h2>
    <form method="POST">
        <input name="username">
        <input name="password" type="password">
        <button>Login</button>
    </form>
    """


# ---------------- ADMIN ----------------
@app.route("/admin", methods=["GET", "POST"])
def admin():
    if "user" not in session:
        return redirect("/login")

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    if request.method == "POST":
        sender = request.form["sender"]
        receiver = request.form["receiver"]
        status = request.form["status"]
        location = request.form["location"]
        weight = request.form["weight"]
        fee = request.form["fee"]
        desc = request.form["desc"]
        address = request.form["address"]

        code = generate_code()

        try:
            c.execute("""
            INSERT INTO shipments 
            (tracking_code, sender, receiver, status, location, weight, fee, description, delivery_address)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (code, sender, receiver, status, location, weight, fee, desc, address))

            c.execute("INSERT INTO history (tracking_code, status, location) VALUES (?, ?, ?)",
                      (code, status, location))

            conn.commit()

        except Exception as e:
            return f"ERROR: {e}"

    c.execute("SELECT * FROM shipments")
    data = c.fetchall()
    conn.close()

    return render_template_string("""
    <h2>Admin Dashboard</h2>

    <form method="POST">
        <input name="sender" placeholder="Sender"><br>
        <input name="receiver" placeholder="Receiver"><br>
        <input name="status" placeholder="Status"><br>
        <input name="location" placeholder="Location"><br>
        <input name="weight" placeholder="Weight"><br>
        <input name="fee" placeholder="Fee"><br>
        <input name="desc" placeholder="Description"><br>
        <input name="address" placeholder="Delivery Address"><br>
        <button>Create Shipment</button>
    </form>

    <h3>All Shipments</h3>
    {% for d in data %}
        <p>{{d[1]}} - {{d[4]}} - {{d[5]}}</p>
    {% endfor %}
    """, data=data)


# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)
