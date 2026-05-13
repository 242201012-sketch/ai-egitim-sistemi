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
import os
import re

app = Flask(__name__)

app.secret_key = "secret123"


# OPENAI CLIENT
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)


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


# AI QUESTION GENERATOR
def generate_ai_question():

    try:

        messages: list[
            ChatCompletionSystemMessageParam
        ] = [

            ChatCompletionSystemMessageParam(

                role="system",

                content="""
                1 adet kolay seviyede
                çoktan seçmeli soru üret.

                Format:

                Soru: ...

                A) ...
                B) ...
                C) ...
                D) ...

                Doğru: B
                """
            )
        ]

        response = client.chat.completions.create(

            model="gpt-4.1-mini",

            messages=messages
        )

        text = (
            response
            .choices[0]
            .message
            .content
        )

        if text is None:

            raise ValueError(
                "AI response is empty"
            )

        question_match = re.search(
            r"Soru:(.*?)(A\))",
            text,
            re.S
        )

        options = re.findall(
            r"[A-D]\)\s.*",
            text
        )

        answer_match = re.search(
            r"Doğru:\s*([A-D])",
            text
        )

        question = "Soru oluşturulamadı."

        if question_match:

            question = (
                question_match
                .group(1)
                .strip()
            )

        correct_answer = "B"

        if answer_match:

            correct_answer = (
                answer_match.group(1)
            )

        return {

            "question": question,

            "options": options,

            "answer": correct_answer
        }

    except Exception as error:

        print("AI ERROR:", error)

        return {

            "question":
            "2 + 2 kaç eder?",

            "options": [
                "A) 3",
                "B) 4",
                "C) 5",
                "D) 22"
            ],

            "answer": "B"
        }


# HOME
@app.route("/")
def home():

    if "username" not in session:

        return redirect("/login")

    ai_question = generate_ai_question()

    question = ai_question["question"]

    options = ai_question["options"]

    session["correct_answer"] = (
        ai_question["answer"]
    )

    return render_template(

        "index.html",

        username=session["username"],

        question=question,

        options=options
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

            return (
                "Kullanıcı adı gerekli"
            )

        conn = sqlite3.connect(
            "database.db"
        )

        cursor = conn.cursor()

        cursor.execute(

            """
            SELECT * FROM users
            WHERE username=?
            """,

            (username,)
        )

        user = cursor.fetchone()

        if not user:

            cursor.execute(

                """
                INSERT INTO users (
                    username
                )
                VALUES (?)
                """,

                (username,)
            )

            conn.commit()

        conn.close()

        session["username"] = username

        return redirect("/")

    return render_template(
        "login.html"
    )


# ANSWER
@app.route(
    "/answer",
    methods=["POST"]
)
def answer():

    if "username" not in session:

        return jsonify({

            "feedback":
            "Giriş yapmalısınız.",

            "score": 0
        })

    user_answer = request.form.get(
        "answer"
    )

    correct_answer = session.get(
        "correct_answer"
    )

    score = 0

    feedback = "Yanlış ❌"

    if not user_answer:

        return jsonify({

            "feedback":
            "Cevap boş olamaz.",

            "score": 0
        })

    selected_letter = user_answer[0]

    if selected_letter == correct_answer:

        feedback = "Doğru cevap ✅"

        conn = sqlite3.connect(
            "database.db"
        )

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

        updated_score = (
            cursor.fetchone()
        )

        conn.close()

        if updated_score:

            score = updated_score[0]

    else:

        conn = sqlite3.connect(
            "database.db"
        )

        cursor = conn.cursor()

        cursor.execute(

            """
            SELECT score
            FROM users
            WHERE username=?
            """,

            (session["username"],)
        )

        current_score = (
            cursor.fetchone()
        )

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

    conn = sqlite3.connect(
        "database.db"
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

    return redirect("/login")


# INIT DATABASE
init_db()


# START APP
if __name__ == "__main__":

    port = int(
        os.environ.get("PORT", 5000)
    )

    app.run(

        host="0.0.0.0",

        port=port
    )