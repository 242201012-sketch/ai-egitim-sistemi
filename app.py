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

from datetime import datetime

# ==================================================
# FLASK
# ==================================================

app = Flask(__name__)

app.secret_key = "super_secret_key"

DATABASE = "database.db"

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

            level INTEGER DEFAULT 1,

            xp INTEGER DEFAULT 0,

            last_reward TEXT
        )

    """)

    conn.commit()

    conn.close()

# ==================================================
# INIT DB
# ==================================================

init_db()

# ==================================================
# QUESTIONS
# ==================================================

QUESTIONS = [

    {
        "question":
        "Python nedir?",

        "options": [

            "Programlama Dili",

            "Tarayıcı",

            "Oyun",

            "İşletim Sistemi"
        ],

        "answer":
        "Programlama Dili"
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
        "Türkiye'nin başkenti?",

        "options": [

            "İstanbul",

            "Ankara",

            "İzmir",

            "Bursa"
        ],

        "answer":
        "Ankara"
    }

]

# ==================================================
# BOSS SYSTEM
# ==================================================

BOSS = {

    "name":
    "AI TITAN 🤖",

    "max_hp":
    500,

    "hp":
    500
}

PLAYER_MAX_HP = 100

# ==================================================
# PLAYER HP
# ==================================================

@app.before_request
def create_player_hp():

    if "player_hp" not in session:

        session["player_hp"] = (
            PLAYER_MAX_HP
        )

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

def calculate_level(xp):

    return max(
        1,
        xp // 100 + 1
    )

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

        return

    cursor.execute(

        """
        UPDATE users
        SET score = score + 50,
            xp = xp + 50,
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

# ==================================================
# LOGIN
# ==================================================

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

# ==================================================
# HOME
# ==================================================

@app.route("/")
def home():

    try:

        if "username" not in session:

            return redirect(
                "/login"
            )

        username = session[
            "username"
        ]

        give_daily_reward(
            username
        )

        conn = sqlite3.connect(
            DATABASE
        )

        cursor = conn.cursor()

        cursor.execute(

            """
            SELECT score, level, xp
            FROM users
            WHERE username = ?
            """,

            (username,)
        )

        user = cursor.fetchone()

        conn.close()

        # ===============================
        # NONE ERROR FIX
        # ===============================

        if user is None:

            score = 0
            level = 1
            xp = 0

        else:

            score = user[0]
            level = user[1]
            xp = user[2]

        question_data = (
            get_question()
        )

        achievements = (
            get_achievements(
                score
            )
        )

        progress = min(
            100,
            xp % 100
        )

        return render_template(

            "index.html",

            username=username,

            score=score,

            level=level,

            xp=xp,

            progress=progress,

            achievements=
            achievements,

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
            ]
        )

    except Exception as e:

        return f"""

        <h1>SERVER ERROR</h1>

        <p>{str(e)}</p>

        """

# ==================================================
# ANSWER
# ==================================================

@app.route(
    "/answer",
    methods=["POST"]
)
def answer():

    if "username" not in session:

        return jsonify({

            "error":
            "Login required"
        })

    user_answer = request.form.get(
        "answer"
    )

    correct_answer = request.form.get(
        "correct_answer"
    )

    if user_answer == correct_answer:

        gained_score = 10
        gained_xp = 20

        result = "Correct ✅"

    else:

        gained_score = 0
        gained_xp = 0

        result = (
            f"Wrong ❌ "
            f"Correct: {correct_answer}"
        )

    conn = sqlite3.connect(
        DATABASE
    )

    cursor = conn.cursor()

    username = session[
        "username"
    ]

    cursor.execute(

        """
        SELECT xp
        FROM users
        WHERE username = ?
        """,

        (username,)
    )

    current_user = (
        cursor.fetchone()
    )

    current_xp = (
        current_user[0]
        if current_user
        else 0
    )

    new_xp = (
        current_xp
        +
        gained_xp
    )

    new_level = (
        calculate_level(
            new_xp
        )
    )

    cursor.execute(

        """
        UPDATE users
        SET score = score + ?,
            xp = ?,
            level = ?
        WHERE username = ?
        """,

        (
            gained_score,
            new_xp,
            new_level,
            username
        )
    )

    conn.commit()

    conn.close()

    return jsonify({

        "result":
        result,

        "xp":
        new_xp,

        "level":
        new_level
    })

# ==================================================
# BOSS PAGE
# ==================================================

@app.route("/boss")
def boss():

    if "username" not in session:

        return redirect(
            "/login"
        )

    question_data = (
        get_question()
    )

    return render_template(

        "boss.html",

        boss_name=
        BOSS["name"],

        boss_hp=
        BOSS["hp"],

        boss_max_hp=
        BOSS["max_hp"],

        player_hp=
        session["player_hp"],

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
        ]
    )

# ==================================================
# BOSS ANSWER
# ==================================================

@app.route(
    "/boss_answer",
    methods=["POST"]
)
def boss_answer():

    user_answer = request.form.get(
        "answer"
    )

    correct_answer = request.form.get(
        "correct_answer"
    )

    if user_answer == correct_answer:

        damage = random.randint(
            25,
            50
        )

        BOSS["hp"] -= damage

        if BOSS["hp"] < 0:

            BOSS["hp"] = 0

        return jsonify({

            "result":
            f"Critical Hit ⚔️ -{damage}",

            "boss_hp":
            BOSS["hp"],

            "player_hp":
            session["player_hp"]
        })

    damage = random.randint(
        5,
        20
    )

    session["player_hp"] -= damage

    if session["player_hp"] < 0:

        session["player_hp"] = 0

    return jsonify({

        "result":
        f"Boss Hit 💥 -{damage}",

        "boss_hp":
        BOSS["hp"],

        "player_hp":
        session["player_hp"]
    })

# ==================================================
# LEADERBOARD
# ==================================================

@app.route("/leaderboard")
def leaderboard():

    conn = sqlite3.connect(
        DATABASE
    )

    cursor = conn.cursor()

    cursor.execute(

        """
        SELECT username, score, level
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
# LOGOUT
# ==================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(
        "/login"
    )

# ==================================================
# START APP
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