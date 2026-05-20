from flask import Flask, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

app = Flask(__name__)
app.secret_key = "supersecretkey"


# DATABASE OLUŞTUR

conn = sqlite3.connect("users.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT
)
""")

conn.commit()
conn.close()


@app.route("/")
def home():

    if "user" not in session:
        return redirect("/login")

    username = session["user"]

    return f"""
    <!DOCTYPE html>
    <html lang="tr">

    <head>

        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">

        <title>Öğrenci Paneli</title>

        <style>

            *{{
                margin:0;
                padding:0;
                box-sizing:border-box;
                font-family:Arial;
            }}

            body{{
                background:#0f172a;
                color:white;
                display:flex;
            }}

            .sidebar{{
                width:260px;
                height:100vh;
                background:#1e293b;
                padding:30px 20px;
            }}

            .sidebar h1{{
                color:#38bdf8;
                margin-bottom:40px;
            }}

            .sidebar a{{
                display:block;
                color:white;
                text-decoration:none;
                margin-bottom:20px;
                padding:12px;
                border-radius:10px;
                transition:0.3s;
            }}

            .sidebar a:hover{{
                background:#334155;
            }}

            .main{{
                flex:1;
                padding:30px;
            }}

            .topbar{{
                display:flex;
                justify-content:space-between;
                align-items:center;
                margin-bottom:30px;
            }}

            .topbar h2{{
                font-size:35px;
            }}

            .cards{{
                display:grid;
                grid-template-columns:repeat(auto-fit,minmax(220px,1fr));
                gap:20px;
                margin-bottom:40px;
            }}

            .card{{
                background:#1e293b;
                padding:25px;
                border-radius:20px;
            }}

            .card h3{{
                margin-bottom:15px;
                color:#38bdf8;
            }}

            .progress{{
                background:#334155;
                height:12px;
                border-radius:20px;
                overflow:hidden;
                margin-top:10px;
            }}

            .progress div{{
                height:100%;
                background:#38bdf8;
            }}

            .courses{{
                display:grid;
                grid-template-columns:repeat(auto-fit,minmax(280px,1fr));
                gap:20px;
                margin-bottom:40px;
            }}

            .course{{
                background:#1e293b;
                padding:25px;
                border-radius:20px;
            }}

            .course h3{{
                margin-bottom:15px;
                color:#38bdf8;
            }}

            .chat-box{{
                background:#1e293b;
                padding:20px;
                border-radius:20px;
            }}

            .messages{{
                height:250px;
                overflow-y:auto;
                margin-bottom:20px;
            }}

            .message{{
                padding:12px;
                border-radius:10px;
                margin-bottom:10px;
            }}

            .user{{
                background:#2563eb;
            }}

            .bot{{
                background:#334155;
            }}

            .input-area{{
                display:flex;
            }}

            input{{
                flex:1;
                padding:15px;
                border:none;
                border-radius:10px;
                outline:none;
            }}

            button{{
                margin-left:10px;
                padding:15px 25px;
                border:none;
                border-radius:10px;
                background:#38bdf8;
                color:white;
                cursor:pointer;
            }}

        </style>

    </head>

    <body>

        <div class="sidebar">

            <h1>🎓 AI Eğitim</h1>

            <a href="/">🏠 Ana Panel</a>
            <a href="#">📚 Dersler</a>
            <a href="#">📝 Quizler</a>
            <a href="#">📊 İstatistik</a>
            <a href="/logout">🚪 Çıkış Yap</a>

        </div>

        <div class="main">

            <div class="topbar">

                <h2>Hoş Geldin {username} 👋</h2>

            </div>

            <div class="cards">

                <div class="card">
                    <h3>📚 Tamamlanan Ders</h3>
                    <h1>12</h1>
                </div>

                <div class="card">
                    <h3>📝 Quiz Skoru</h3>
                    <h1>89%</h1>
                </div>

                <div class="card">
                    <h3>🔥 Günlük Seri</h3>
                    <h1>7 Gün</h1>
                </div>

            </div>

            <h2 style="margin-bottom:20px;">📘 Dersler</h2>

            <div class="courses">

                <div class="course">

                    <h3>Python Eğitimi</h3>

                    <p>İlerleme: %80</p>

                    <div class="progress">
                        <div style="width:80%;"></div>
                    </div>

                </div>

                <div class="course">

                    <h3>HTML & CSS</h3>

                    <p>İlerleme: %65</p>

                    <div class="progress">
                        <div style="width:65%;"></div>
                    </div>

                </div>

                <div class="course">

                    <h3>Flask Web Geliştirme</h3>

                    <p>İlerleme: %40</p>

                    <div class="progress">
                        <div style="width:40%;"></div>
                    </div>

                </div>

            </div>

            <h2 style="margin-bottom:20px;">🤖 AI Asistan</h2>

            <div class="chat-box">

                <div class="messages" id="messages">

                    <div class="message bot">
                        Merhaba 👋 Sana nasıl yardımcı olabilirim?
                    </div>

                </div>

                <div class="input-area">

                    <input type="text"
                    id="userInput"
                    placeholder="Mesaj yaz...">

                    <button onclick="sendMessage()">
                        Gönder
                    </button>

                </div>

            </div>

        </div>

        <script>

            async function sendMessage(){{

                let input = document.getElementById("userInput");
                let messages = document.getElementById("messages");

                let text = input.value;

                if(text.trim() === "") return;

                messages.innerHTML += `
                    <div class="message user">
                        ${{text}}
                    </div>
                `;

                input.value = "";

                let response = await fetch("/chat",{{
                    method:"POST",
                    headers:{{
                        "Content-Type":"application/json"
                    }},
                    body:JSON.stringify({{
                        message:text
                    }})
                }});

                let data = await response.json();

                messages.innerHTML += `
                    <div class="message bot">
                        ${{data.reply}}
                    </div>
                `;

                messages.scrollTop = messages.scrollHeight;
            }}

        </script>

    </body>

    </html>
    """


# CHATBOT API

@app.route("/chat", methods=["POST"])
def chat():

    user_message = request.json["message"].lower()

    if "python" in user_message:
        reply = "Python güçlü bir programlama dilidir 🐍"

    elif "html" in user_message:
        reply = "HTML web sitelerinin temelidir 🌐"

    elif "css" in user_message:
        reply = "CSS tasarım için kullanılır 🎨"

    elif "merhaba" in user_message:
        reply = "Merhaba 👋"

    else:
        reply = "AI sistemi geliştiriliyor 🚀"

    return {
        "reply": reply
    }


# REGISTER

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        hashed_password = generate_password_hash(password)

        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()

        try:

            cursor.execute(
                "INSERT INTO users(username,password) VALUES(?,?)",
                (username, hashed_password)
            )

            conn.commit()

        except:
            conn.close()
            return "Bu kullanıcı adı zaten mevcut."

        conn.close()

        return redirect("/login")

    return """
    <body style='background:#0f172a;color:white;
    display:flex;justify-content:center;
    align-items:center;height:100vh;font-family:Arial;'>

    <form method='POST'
    style='background:#1e293b;padding:40px;
    border-radius:20px;width:350px;'>

        <h1>Kayıt Ol</h1><br>

        <input name='username'
        placeholder='Kullanıcı Adı'
        style='width:100%;padding:15px;margin-bottom:15px;'>

        <input type='password'
        name='password'
        placeholder='Şifre'
        style='width:100%;padding:15px;margin-bottom:15px;'>

        <button style='width:100%;padding:15px;
        background:#38bdf8;border:none;color:white;'>
            Kayıt Ol
        </button>

        <br><br>

        <a href='/login' style='color:white;'>
            Giriş Yap
        </a>

    </form>

    </body>
    """


# LOGIN

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE username=?",
            (username,)
        )

        user = cursor.fetchone()

        conn.close()

        if user and check_password_hash(user[2], password):

            session["user"] = username

            return redirect("/")

        else:
            return "Kullanıcı adı veya şifre yanlış."

    return """
    <body style='background:#0f172a;color:white;
    display:flex;justify-content:center;
    align-items:center;height:100vh;font-family:Arial;'>

    <form method='POST'
    style='background:#1e293b;padding:40px;
    border-radius:20px;width:350px;'>

        <h1>Giriş Yap</h1><br>

        <input name='username'
        placeholder='Kullanıcı Adı'
        style='width:100%;padding:15px;margin-bottom:15px;'>

        <input type='password'
        name='password'
        placeholder='Şifre'
        style='width:100%;padding:15px;margin-bottom:15px;'>

        <button style='width:100%;padding:15px;
        background:#38bdf8;border:none;color:white;'>
            Giriş Yap
        </button>

        <br><br>

        <a href='/register' style='color:white;'>
            Hesap Oluştur
        </a>

    </form>

    </body>
    """


# LOGOUT

@app.route("/logout")
def logout():

    session.pop("user", None)

    return redirect("/login")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)