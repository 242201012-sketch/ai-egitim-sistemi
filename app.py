from flask import Flask, render_template, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

app = Flask(__name__)
app.secret_key = "supersecretkey"

# DATABASE
def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        role TEXT DEFAULT 'student'
    )
    """)

    conn.commit()
    conn.close()

init_db()

# HOME
@app.route("/")
def home():
    return render_template("index.html")

# REGISTER
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        hashed_password = generate_password_hash(password)

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        try:
            cursor.execute(
                "INSERT INTO users(username,password) VALUES(?,?)",
                (username, hashed_password)
            )

            conn.commit()

        except:
            return "Kullanıcı zaten mevcut"

        conn.close()

        return redirect("/login")

    return render_template("register.html")

# LOGIN
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE username=?",
            (username,)
        )

        user = cursor.fetchone()

        conn.close()

        if user and check_password_hash(user[2], password):

            session["user"] = user[1]
            session["role"] = user[3]

            if user[3] == "admin":
                return redirect("/admin")

            return redirect("/student")

        else:
            return "Hatalı kullanıcı adı veya şifre"

    return render_template("login.html")

# STUDENT PANEL
@app.route("/student")
def student():

    if "user" not in session:
        return redirect("/login")

    return render_template(
        "student_dashboard.html",
        username=session["user"]
    )

# ADMIN PANEL
@app.route("/admin")
def admin():

    if "user" not in session:
        return redirect("/login")

    if session["role"] != "admin":
        return "Yetkisiz erişim"

    return render_template(
        "admin_dashboard.html",
        username=session["user"]
    )

# LOGOUT
@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
