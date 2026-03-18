from flask import Flask, render_template, request, redirect, session
import sqlite3, random, os

app = Flask(__name__)
app.secret_key = "secret123"

if not os.path.exists("database.db"):
    import create_db

def gen_tracking():
    return "AMX" + str(random.randint(1000000,9999999))


@app.route("/")
def home():
    return render_template("index.html")


# AUTH

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        conn = sqlite3.connect("database.db")
        c = conn.cursor()

        c.execute("SELECT * FROM users WHERE username=? AND password=?",
                  (request.form["username"], request.form["password"]))

        user = c.fetchone()
        conn.close()

        if user:
            session["role"] = user[4]
            if user[4] == "admin":
                return redirect("/dashboard")

    return render_template("login.html")


# DASHBOARD

@app.route("/dashboard")
def dashboard():
    if session.get("role") != "admin":
        return redirect("/login")

    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("SELECT * FROM shipments")
    data = c.fetchall()
    conn.close()

    return render_template("dashboard.html", data=data)


# CREATE SHIPMENT

@app.route("/create", methods=["GET","POST"])
def create():
    if session.get("role") != "admin":
        return redirect("/login")

    if request.method == "POST":
        tracking = gen_tracking()

        conn = sqlite3.connect("database.db")
        c = conn.cursor()

        c.execute("INSERT INTO shipments VALUES(NULL,?,?,?,?,?)",
                  (tracking,
                   "Processing",
                   request.form["location"],
                   request.form["lat"],
                   request.form["lng"]))

        conn.commit()
        conn.close()

        return redirect("/dashboard")

    return render_template("create.html")


# UPDATE

@app.route("/update/<tracking>", methods=["POST"])
def update(tracking):
    if session.get("role") != "admin":
        return redirect("/login")

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("""
    UPDATE shipments 
    SET location=?, status=?, lat=?, lng=?
    WHERE tracking=?
    """,
    (request.form["location"],
     request.form["status"],
     request.form["lat"],
     request.form["lng"],
     tracking))

    conn.commit()
    conn.close()

    return redirect("/dashboard")


# TRACK

@app.route("/track", methods=["POST"])
def track():
    code = request.form["tracking"]

    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("SELECT * FROM shipments WHERE tracking=?", (code,))
    data = c.fetchone()
    conn.close()

    return render_template("tracking.html", data=data)


if __name__ == "__main__":
    app.run()
