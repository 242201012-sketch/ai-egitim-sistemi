from flask import (
    Flask,
    render_template,
    request,
    redirect,
    session,
    jsonify
)

import sqlite3
import random
import os

# FLASK
app = Flask(__name__)

app.secret_key = "super_secret_key"

# DATABASE
DATABASE = "database.db"


# DATABASE INIT
def init_db():

    conn = sqlite3.connect(
        DATABASE
    )

    cursor = conn.cursor()

    # USERS
    cursor.execute("""

        CREATE TABLE IF NOT EXISTS users (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            username TEXT UNIQUE,

            score INTEGER DEFAULT 0

        )

    """)

    conn.commit()

    conn.close()


# INIT DATABASE
init_db()


# OFFLINE AI QUESTION SYSTEM
questions = [

    {
        "question":
        "Türkiye'nin başkenti neresidir?",

        "options": [

            "İstanbul",

            "Ankara",

            "İzmir",

            "Bursa"
        ],

        "answer":
        "Ankara"
    },

    {
        "question":
        "5 x 5 kaçtır?",

        "options": [

            "10",

            "15",

            "20",

            "25"
        ],

        "answer":
        "25"
    },

    {
        "question":
        "Dünyanın en büyük okyanusu hangisidir?",

        "options": [

            "Atlas",

            "Hint",

            "Pasifik",

            "Arktik"
        ],

        "answer":
        "Pasifik"
    },

    {
        "question":
        "Python hangi tür bir dildir?",

        "options": [

            "Programlama",

            "Müzik",

            "Oyun",

            "Tarayıcı"
        ],

        "answer":
        "Programlama"
    }

]


# RANDOM QUESTION
def get_random_question():

    return random.choice(
        questions
    )


# ANSWER EVALUATION
def evaluate_answer(

    correct_answer,
    user_answer

):

    if (
        correct_answer.lower()
        ==
        user_answer.lower()
    ):

        return (
            "Doğru cevap ✅",
            10
        )

    return (

        f"Yanlış ❌ "
        f"Doğru cevap: "
        f"{correct_answer}",

        0
    )


# LOGIN
@app.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    if request.method == "POST":

        username = request.form.get(
            "username"
        )

        if not username:

            return redirect(
                "/login"
            )

        conn = sqlite3.connect(
            DATABASE
        )

        cursor = conn.cursor()

        cursor.execute(

            """
            INSERT OR IGNORE INTO users (
                username
            )
            VALUES (?)
            """,

            (username,)
        )

        conn.commit()

        conn.close()

        session["username"] = (
            username
        )

        return redirect("/")

    return render_template(
        "login.html"
    )


# HOME
@app.route("/")
def home():

    if "username" not in session:

        return redirect(
            "/login"
        )

    question_data = (
        get_random_question()
    )

    return render_template(

        "index.html",

        question=
        question_data["question"],

        options=
        question_data["options"],

        correct_answer=
        question_data["answer"]
    )


# ANSWER
@app.route(
    "/answer",
    methods=["POST"]
)
def answer():

    user_answer = request.form.get(
        "answer"
    )

    correct_answer = request.form.get(
        "correct_answer"
    )

    feedback, score = (
        evaluate_answer(

            correct_answer,

            user_answer
        )
    )

    conn = sqlite3.connect(
        DATABASE
    )

    cursor = conn.cursor()

    cursor.execute(

        """
        UPDATE users
        SET score = score + ?
        WHERE username=?
        """,

        (

            score,

            session["username"]
        )
    )

    conn.commit()

    conn.close()

    return jsonify({

        "feedback": feedback,

        "score": score
    })


# LEADERBOARD
@app.route("/leaderboard")
def leaderboard():

    conn = sqlite3.connect(
        DATABASE
    )

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

    return redirect(
        "/login"
    )


# START
if __name__ == "__main__":

    port = int(

        os.environ.get(

            "PORT",

            5000
        )
    )

    app.run(

        host="0.0.0.0",

        port=port,

        debug=True
    )