from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    redirect,
    session
)

from openai import OpenAI

import sqlite3
import os
import re

app = Flask(__name__)

app.secret_key = "secret123"

# OPENAI CLIENT
client = OpenAI(
    api_key=os.getenv("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")
)

# SCORE
score = 0

ai_question_data = {

    "question": "",

    "options": [],

    "answer": ""
}

def generate_ai_question(level="easy"):

    response = client.chat.completions.create(

        model="gpt-4.1-mini",

        messages=[

            {
                "role": "system",

                "content":

                f"""
                {level} seviyesinde
                1 adet çoktan seçmeli soru üret.

                ŞU FORMATTA ÜRET:

                Soru: ...

                A) ...
                B) ...
                C) ...
                D) ...

                Doğru: A

                SADECE BU FORMATI KULLAN.
                """
            }
        ]
    )

    text = response.choices[0].message.content

    question_match = re.search(

        r"Soru:(.*?)(A\))",

        text,

        re.S
    )

    options = re.findall(

        r"([A-D]\).*?)\n",

        text
    )

    answer_match = re.search(

        r"Doğru:\s*([A-D])",

        text
    )

    question = ""

    if question_match:

        question = question_match.group(1).strip()

    correct_answer = ""

    if answer_match:

        correct_answer = answer_match.group(1)

    return {

        "question": question,

        "options": options,

        "answer": correct_answer
    }



# REGISTER
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]

        password = request.form["password"]

        conn = sqlite3.connect("database.db")

        cursor = conn.cursor()

        try:

            cursor.execute(

                "INSERT INTO users (username, password) VALUES (?, ?)",

                (username, password)
            )

            conn.commit()

            conn.close()

            return redirect("/login")

        except:

            conn.close()

            return "Kullanıcı zaten var"

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

            "SELECT * FROM users WHERE username=? AND password=?",

            (username, password)
        )

        user = cursor.fetchone()

        conn.close()

        if user:

            session["username"] = username

            session["score"] = user[3]

            return redirect("/")

        return "Hatalı giriş"

    return render_template("login.html")


# LOGOUT
@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")


# HOME
@app.route("/")
def index():

    global ai_question_data

    if "username" not in session:

        return redirect("/login")

    if ai_question_data == "":

        ai_question_data = generate_ai_question()

    return render_template(

        "index.html",

        question=ai_question_data["question"],
        options=ai_question_data["options"]
    )


# ANSWER
@app.route("/answer", methods=["POST"])
def answer():

    global score
    global ai_question_data

    user_answer = request.form.get("answer", "")

    question = ai_question_data

    correct_answer = ai_question_data["answer"]

    feedback = evaluate_answer(

        question,
        correct_answer,
        user_answer
    )

    feedback_lower = feedback.lower()

    if "doğru" in feedback_lower:

        score += 10

        conn = sqlite3.connect("database.db")

        cursor = conn.cursor()

        cursor.execute(

            "UPDATE users SET score = score + 10 WHERE username=?",

            (session["username"],)
        )

        conn.commit()

        conn.close()

    elif "kısmen" in feedback_lower:

        score += 5

        conn = sqlite3.connect("database.db")

        cursor = conn.cursor()

        cursor.execute(

            "UPDATE users SET score = score + 5 WHERE username=?",

            (session["username"],)
        )

        conn.commit()

        conn.close()

    # NEW AI QUESTION
    if score < 20:
        level = "easy"

    elif score < 50:
        level = "medium"

    else:
        level = "hard"

    ai_question_data = generate_ai_question(level)

    return jsonify({

        "feedback": feedback,

        "score": score,

        "next_question": ai_question_data
    })


# LEADERBOARD
@app.route("/leaderboard")
def leaderboard():

    conn = sqlite3.connect("database.db")

    cursor = conn.cursor()

    cursor.execute("""

        SELECT username, score

        FROM users

        ORDER BY score DESC

    """)

    users = cursor.fetchall()

    conn.close()

    return render_template(

        "leaderboard.html",

        users=users
    )


# START
init_db()

if __name__ == "__main__":

    app.run(debug=True)