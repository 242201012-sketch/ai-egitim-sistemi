from flask import Flask, render_template, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3


app = Flask(__name__)

app.secret_key = "SUPER_SECRET_KEY"

# DATABASE
def get_db():
    conn = sqlite3.connect("game.db")
    conn.row_factory = sqlite3.Row
    return conn

# CREATE TABLE
def init_db():

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        xp INTEGER DEFAULT 0,
        level INTEGER DEFAULT 1,
        score INTEGER DEFAULT 0
    )
    """)

    conn.commit()
    conn.close()

init_db()

# HOME
@app.route("/")
def home():

    if "user_id" not in session:
        return redirect("/login")

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM users WHERE id=?",
        (session["user_id"],)
    )

    user = cursor.fetchone()

    conn.close()

    if user is None:
        session.clear()
        return redirect("/login")

    return render_template(
        "index.html",
        user=user
    )

# REGISTER
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        hashed_password = generate_password_hash(password)

        try:

            conn = get_db()
            cursor = conn.cursor()

            cursor.execute("""
            INSERT INTO users
            (username, password)
            VALUES (?, ?)
            """, (username, hashed_password))

            conn.commit()
            conn.close()

            return redirect("/login")

        except sqlite3.IntegrityError:
            return "Bu kullanıcı zaten var."

    return render_template("register.html")

# LOGIN
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE username=?",
            (username,)
        )

        user = cursor.fetchone()

        conn.close()

        if user:

            if check_password_hash(
                user["password"],
                password
            ):

                session["user_id"] = user["id"]

                return redirect("/")

        return "Hatalı kullanıcı adı veya şifre"

    return render_template("login.html")

# LOGOUT
@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")

@app.route("/boss")
def boss():

    return """
    <h1>🔥 Boss Battle Yakında!</h1>
    """

@app.route("/leaderboard")
def leaderboard():

    return """
    <h1>🏆 Leaderboard Yakında!</h1>
    """

# START
if __name__ == "__main__":
    app.run(debug=True)

