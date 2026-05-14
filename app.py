from flask import (
    Flask,
    render_template,
    request,
    redirect,
    session,
    jsonify
)

from openai import OpenAI

from openai.types.chat import (
    ChatCompletionSystemMessageParam
)

import sqlite3
import random
import os

from datetime import datetime

# ==================================================
# FLASK
# ==================================================

app = Flask(__name__)

app.secret_key = "super_secret_key"

DATABASE = "database.db"

# OPENAI CLIENT
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
ADMIN_PASSWORD = "1234"


# ==================================================
# DATABASE
# ==================================================

def init_db():
    conn = sqlite3.connect(
        DATABASE
    )

    cursor = conn.cursor()

    cursor.execute("""

        CREATE TABLE IF NOT EXISTS users (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            username TEXT UNIQUE,

            score INTEGER DEFAULT 0,

            last_reward TEXT
        )

    """)

    conn.commit()

    conn.close()


init_db()

# ==================================================
# QUESTIONS
# ==================================================

QUESTIONS = [

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
            "Python nedir?",

        "options": [

            "Programlama dili",

            "Tarayıcı",

            "Oyun",

            "Robot"
        ],

        "answer":
            "Programlama dili"
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
    }

]


# ==================================================
# RANDOM QUESTION
# ==================================================

def get_question():
    return random.choice(
        QUESTIONS
    )


# ==================================================
# LEVEL SYSTEM
# ==================================================

def get_level(score):
    if score >= 500:

        return "Diamond 💎"

    elif score >= 300:

        return "Platinum 🏆"

    elif score >= 150:

        return "Gold 🥇"

    elif score >= 50:

        return "Silver 🥈"

    return "Bronze 🥉"


# ==================================================
# ACHIEVEMENTS
# ==================================================

def get_achievements(score):
    achievements = []

    if score >= 50:
        achievements.append(
            "Beginner 🚀"
        )

    if score >= 150:
        achievements.append(
            "Quiz Master 🧠"
        )

    if score >= 300:
        achievements.append(
            "Legend 👑"
        )

    return achievements


# ==================================================
# DAILY REWARD
# ==================================================

def give_daily_reward(username):
    conn = sqlite3.connect(
        DATABASE
    )

    cursor = conn.cursor()

    cursor.execute(

        """
        SELECT last_reward
        FROM users
        WHERE username = ?
        """,

        (username,)
    )

    result = cursor.fetchone()

    today = datetime.now().strftime(
        "%Y-%m-%d"
    )

    if result and result[0] == today:
        conn.close()

        return False

    cursor.execute(

        """
        UPDATE users
        SET score = score + 50,
            last_reward = ?
        WHERE username = ?
        """,

        (
            today,
            username
        )
    )

    conn.commit()

    conn.close()

    return True


# ==================================================
# ANSWER SYSTEM
# ==================================================

def evaluate_answer(

        user_answer,
        correct_answer

):
    if (
            user_answer
            ==
            correct_answer
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


# ==================================================
# LOGIN
# ==================================================

@app.route(
    "/login",
    methods=["GET", "POST"]
)
def login():
    if request.method == "POST":

        username = (
            request.form.get(
                "username"
            )
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


# ==================================================
# HOME
# ==================================================

@app.route("/")
def home():
    if "username" not in session:
        return redirect(
            "/login"
        )

    give_daily_reward(
        session["username"]
    )

    question_data = (
        get_question()
    )

    conn = sqlite3.connect(
        DATABASE
    )

    cursor = conn.cursor()

    cursor.execute(

        """
        SELECT score
        FROM users
        WHERE username = ?
        """,

        (session["username"],)
    )

    user = cursor.fetchone()

    conn.close()

    score = user[0]

    level = get_level(
        score
    )

    achievements = (
        get_achievements(
            score
        )
    )

    return render_template(

        "index.html",

        question=
        question_data[
            "question"
        ],

        options=
        question_data[
            "options"
        ],

        correct_answer=
        question_data[
            "answer"
        ],

        score=score,

        level=level,

        achievements=
        achievements
    )


# ==================================================
# ANSWER
# ==================================================

@app.route(
    "/answer",
    methods=["POST"]
)
def answer():
    user_answer = (
        request.form.get(
            "answer"
        )
    )

    correct_answer = (
        request.form.get(
            "correct_answer"
        )
    )

    feedback, gained_score = (
        evaluate_answer(

            user_answer,

            correct_answer
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
        WHERE username = ?
        """,

        (

            gained_score,

            session[
                "username"
            ]
        )
    )

    conn.commit()

    cursor.execute(

        """
        SELECT score
        FROM users
        WHERE username = ?
        """,

        (session["username"],)
    )

    updated_user = (
        cursor.fetchone()
    )

    conn.close()

    total_score = (
        updated_user[0]
    )

    level = get_level(
        total_score
    )

    achievements = (
        get_achievements(
            total_score
        )
    )

    return jsonify({

        "feedback":
            feedback,

        "gained_score":
            gained_score,

        "total_score":
            total_score,

        "level":
            level,

        "achievements":
            achievements
    })


# ==================================================
# LEADERBOARD
# ==================================================

@app.route(
    "/leaderboard"
)
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


# ==================================================
# ADMIN PANEL
# ==================================================

@app.route("/admin")
def admin():
    password = request.args.get(
        "password"
    )

    if password != ADMIN_PASSWORD:
        return "ACCESS DENIED"

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

        "admin.html",

        users=users
    )


# ==================================================
# LOGOUT
# ==================================================

@app.route("/logout")
def logout():
    session.clear()

    return redirect(
        "/login"
    )


# ==================================================
# START
# ==================================================

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
# update