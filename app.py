from flask import Flask
import sqlite3
import os

app = Flask(__name__)

DB_NAME = "database.db"


# =========================
# DATABASE CONNECTION
# =========================

def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


# =========================
# DATABASE RESET + CREATE
# =========================

def reset_database():

    conn = get_db()
    cursor = conn.cursor()

    # ESKI TABLOYU SIL
    cursor.execute("DROP TABLE IF EXISTS users")

    # YENI TABLO
    cursor.execute("""
    CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        score INTEGER DEFAULT 0,
        xp INTEGER DEFAULT 0,
        level INTEGER DEFAULT 1
    )
    """)

    # TEST USER
    cursor.execute("""
    INSERT INTO users
    (username, score, xp, level)
    VALUES (?, ?, ?, ?)
    """, ("Efe", 0, 0, 1))

    conn.commit()
    conn.close()


# =========================
# HOME
# =========================

@app.route("/")
def home():

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users LIMIT 1")
    user = cursor.fetchone()

    username = user["username"]
    score = user["score"]
    xp = user["xp"]
    level = user["level"]

    conn.close()

    return f"""
    <!DOCTYPE html>

    <html>

    <head>

        <title>AI Eğitim Sistemi</title>

        <style>

            body {{
                background: #111827;
                color: white;
                font-family: Arial;
                text-align: center;
                padding: 40px;
            }}

            .card {{
                background: #1f2937;
                padding: 30px;
                border-radius: 20px;
                width: 500px;
                margin: auto;
            }}

            button {{
                padding: 12px 20px;
                border: none;
                border-radius: 10px;
                background: #2563eb;
                color: white;
                cursor: pointer;
                font-size: 16px;
            }}

            .xpbar {{
                width: 100%;
                background: #374151;
                height: 30px;
                border-radius: 20px;
                overflow: hidden;
                margin-top: 20px;
            }}

            .xpfill {{
                height: 100%;
                width: {xp % 100}%;
                background: limegreen;
            }}

        </style>

    </head>

    <body>

        <div class="card">

            <h1>🔥 AI Eğitim Sistemi</h1>

            <h2>{username}</h2>

            <h3>Score: {score}</h3>

            <h3>XP: {xp}</h3>

            <h3>Level: {level}</h3>

            <div class="xpbar">
                <div class="xpfill"></div>
            </div>

            <br><br>

            <a href="/addxp">
                <button>+50 XP</button>
            </a>

        </div>

    </body>

    </html>
    """


# =========================
# XP
# =========================

@app.route("/addxp")
def addxp():

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE users
    SET xp = xp + 50
    """)

    cursor.execute("""
    UPDATE users
    SET level = CAST((xp / 100) AS INTEGER) + 1
    """)

    conn.commit()
    conn.close()

    return """
    <h1>XP Eklendi</h1>

    <a href="/">
        <button>Geri Dön</button>
    </a>
    """


# =========================
# START
# =========================

if __name__ == "__main__":

    # DATABASE'I SIFIRDAN OLUŞTUR
    reset_database()

    port = int(os.environ.get("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port
    )