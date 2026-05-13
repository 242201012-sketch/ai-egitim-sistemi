from flask import (
    Flask,
    render_template,
    request,
    redirect,
    session,
    jsonify
)

import sqlite3
import os

app = Flask(__name__)

app.secret_key = "secret123"


# DATABASE
def init_db():

    conn = sqlite3.connect("database.db")

    cursor = conn.cursor()

    cursor.execute("""

        CREATE TABLE IF NOT EXISTS users (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            username TEXT UNIQUE,

            score INTEGER DEFAULT 0

        )

    """)

    conn.commit()

    conn.close()


# HOME
@app.route("/")
def home():

    if "username" not in session:

        return redirect("/login")

    question = "2 + 2 kaç eder?"

    options = [
        "3",
        "4",
        "5",
        "22"
    ]

    return render_template(

        "index.html",

        username=session["username"],

        question=question,

        options=options
    )


# LOGIN
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get("username")

        if not username:

            return "Kullanıcı adı gerekli"

        conn = sqlite3.connect("database.db")

        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE username=?",
            (username,)
        )

        user = cursor.fetchone()

        if not user:

            cursor.execute(
                """
                INSERT INTO users (username)
                VALUES (?)
                """,
                (username,)
            )

            conn.commit()

        conn.close()

        session["username"] = username

        return redirect("/")

    return render_template("login.html")


# ANSWER
@app.route("/answer", methods=["POST"])
def answer():

    if "username" not in session:

        return jsonify({
            "feedback": "Giriş yapmalısınız.",
            "score": 0
        })

    user_answer = request.form.get("answer")

    score = 0

    feedback = "Yanlış ❌"

    if user_answer == "4":

        feedback = "Doğru cevap ✅"

        conn = sqlite3.connect("database.db")

        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE users
            SET score = score + 10
            WHERE username=?
            """,
            (session["username"],)
        )

        conn.commit()

        cursor.execute(
            """
            SELECT score
            FROM users
            WHERE username=?
            """,
            (session["username"],)
        )

        updated_score = cursor.fetchone()

        conn.close()

        if updated_score:

            score = updated_score[0]

    else:

        conn = sqlite3.connect("database.db")

        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT score
            FROM users
            WHERE username=?
            """,
            (session["username"],)
        )

        current_score = cursor.fetchone()

        conn.close()

        if current_score:

            score = current_score[0]

    return jsonify({

        "feedback": feedback,

        "score": score
    })


# LEADERBOARD
@app.route("/leaderboard")
def leaderboard():

    conn = sqlite3.connect("database.db")

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT username, score
        FROM users
        ORDER BY score DESC
        """
    )

    users = cursor.fetchall()

    conn.close()

    return render_template(
        "leaderboard.html",
        users=users
    )


# LOGOUT
@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")


# INIT DATABASE
init_db()


# START APP
if __name__ == "__main__":

    port = int(os.environ.get("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port
    )