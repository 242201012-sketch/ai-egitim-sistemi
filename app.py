from flask import (
    Flask,
    render_template,
    request,
    redirect,
    session
)

import os

app = Flask(__name__)

app.secret_key = "secret123"


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


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get("username")

        session["username"] = username

        return redirect("/")

    return render_template("login.html")


@app.route("/answer", methods=["POST"])
def answer():

    user_answer = request.form.get("answer")

    score = 0

    feedback = "Yanlış"

    if user_answer == "4":

        score = 10

        feedback = "Doğru cevap ✅"

    return {
        "feedback": feedback,
        "score": score
    }


if __name__ == "__main__":

    port = int(os.environ.get("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port
    )