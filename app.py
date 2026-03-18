from flask import Flask, render_template, request, redirect, session
import sqlite3, random, os

app = Flask(__name__)
app.secret_key = "secret123"

if not os.path.exists("database.db"):
    import create_db


def generate_tracking():
    return "AMX" + str(random.randint(100000,999999))


# HOME
@app.route("/")
def home():
    return render_template("index.html")


# -------- ADMIN LOGIN --------
@app.route("/admin-secret-login", methods=["GET","POST"])
def admin_login():
    if request.method == "POST":
        conn = sqlite3.connect("database.db")
        c = conn.cursor()

        c.execute("SELECT * FROM admin WHERE username=? AND password=?",
                  (request.form["username"], request.form["password"]))

        admin = c.fetchone()
        conn.close()

        if admin:
            session["admin"] = True
            return redirect("/dashboard")

    return render_template("admin_login.html")


# -------- DASHBOARD --------
@app.route("/dashboard")
def dashboard():
    if not session.get("admin"):
        return redirect("/admin-secret-login")

    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("SELECT * FROM shipments")
    data = c.fetchall()
    conn.close()

    return render_template("dashboard.html", data=data)


# -------- CREATE SHIPMENT --------
@app.route("/create", methods=["POST"])
def create():
    if not session.get("admin"):
        return redirect("/admin-secret-login")

    tracking = generate_tracking()

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("INSERT INTO shipments(tracking,status,location) VALUES(?,?,?)",
              (tracking,
               request.form["status"],
               request.form["location"]))

    conn.commit()
    conn.close()

    return redirect("/dashboard")


# -------- UPDATE SHIPMENT --------
@app.route("/update/<tracking>", methods=["POST"])
def update(tracking):
    if not session.get("admin"):
        return redirect("/admin-secret-login")

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("""
    UPDATE shipments
    SET status=?, location=?
    WHERE tracking=?
    """,
    (request.form["status"],
     request.form["location"],
     tracking))

    conn.commit()
    conn.close()

    return redirect("/dashboard")


# -------- TRACK --------
@app.route("/track", methods=["POST"])
def track():
    code = request.form["tracking"]

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("SELECT * FROM shipments WHERE tracking=?", (code,))
    result = c.fetchone()
    conn.close()

    return render_template("tracking.html", result=result)


if __name__ == "__main__":
    app.run()
