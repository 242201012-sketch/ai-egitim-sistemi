from openai import OpenAI
from openai.types.chat import (
    ChatCompletionSystemMessageParam,
    ChatCompletionUserMessageParam
)

client = OpenAI(api_key="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")


def evaluate_answer(
    question: str,
    correct_answer: str,
    user_answer: str
) -> str:

    messages: list[
        ChatCompletionSystemMessageParam
        | ChatCompletionUserMessageParam
    ] = [

        ChatCompletionSystemMessageParam(
            role="system",
            content="""
            Öğrenci cevabını değerlendir.

            Şunları belirt:

            - Doğru / Kısmen Doğru / Yanlış
            - Kısa açıklama
            - Eksik olduğu nokta

            Maksimum 3 cümle yaz.
            """
        ),

        ChatCompletionUserMessageParam(
            role="user",
            content=f"""
            Soru:
            {question}

            Doğru cevap:
            {correct_answer}

            Öğrenci cevabı:
            {user_answer}
            """
        )
    ]

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=messages
    )

    return response.choices[0].message.content or "Geri bildirim alınamadı."


def generate_ai_question(level: str = "easy") -> str:

    messages: list[
        ChatCompletionSystemMessageParam
    ] = [

        ChatCompletionSystemMessageParam(
            role="system",
            content=f"""
            {level} seviyesinde
            1 adet çoktan seçmeli soru üret.

            Format:

            Soru: ...

            A) ...
            B) ...
            C) ...
            D) ...

            Doğru: A
            """
        )
    ]

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=messages
    )

    return response.choices[0].message.content or "Soru üretilemedi."

from flask import (
    Flask,
    render_template,
    session, redirect,
)

import os



app = Flask(__name__)


def create_graph():
    pass


@app.route("/")
def index():

    if "username" not in session:

        return redirect("/login")

    graph_exists = os.path.exists(
        "static/graph.png"
    )

    global ai_question_data

    ai_question_data = generate_ai_question(
        "easy"
    )

    create_graph()

    return render_template(

        "index.html",

        question=ai_question_data["question"],

        options=ai_question_data["options"],

        username=session["username"],

        graph_exists=graph_exists
    )


if __name__ == "__main__":

    port = int(os.environ.get("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port
    )