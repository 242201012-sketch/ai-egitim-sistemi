from flask import Flask
import sqlite3
import os

app = Flask(__name__)

DB_NAME = "database.db"


# ---------------- DATABASE ---------------- #

def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def setup_database():
    conn = get_db()
    cursor = conn.cursor()

    # Ana tablo
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT
    )
    """)

    conn.commit()

    # Kolon kontrol sistemi
    cursor.execute("PRAGMA table_info(users)")
    columns = [col[1] for col in cursor.fetchall()]

    if "score" not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN score INTEGER DEFAULT 0")

    if "xp" not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN xp INTEGER DEFAULT 0")

    if "level" not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN level INTEGER DEFAULT 1")

    conn.commit()

    # Kullanıcı var mı kontrol et
    cursor.execute("SELECT * FROM users WHERE username = ?", ("Efe",))
    user = cursor.fetchone()

    if user is None:
        cursor.execute("""
        INSERT INTO users (username, score, xp, level)
        VALUES (?, ?, ?, ?)
        """, ("Efe", 0, 0, 1))

    conn.commit()
    conn.close()


# ---------------- LEVEL SYSTEM ---------------- #

def calculate_level(xp):
    return (xp // 100) + 1


# ---------------- ROUTES ---------------- #

@app.route("/")
def home():

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE username = ?", ("Efe",))
    user = cursor.fetchone()

    # Güvenlik kontrolü
    if user is None:
        return """
        <h1>KULLANICI BULUNAMADI</h1>
        """

    username = user["username"]
    score = user["score"]
    xp = user["xp"]
    level = user["level"]

    html = f"""
    <html>
    <head>
        <title>AI Eğitim Sistemi</title>

        <style>
            body {{
                background: #111;
                color: white;
                font-family: Arial;
                text-align: center;
                padding-top: 50px;
            }}

            .card {{
                width: 500px;
                margin: auto;
                background: #222;
                padding: 30px;
                border-radius: 20px;
            }}

            .bar {{
                width: 100%;
                background: #444;
                height: 30px;
                border-radius: 20px;
                overflow: hidden;
            }}

            .fill {{
                height: 100%;
                width: {xp % 100}%;
                background: lime;
            }}

            button {{
                padding: 15px;
                border: none;
                border-radius: 10px;
                background: cyan;
                font-size: 18px;
                cursor: pointer;
                margin-top: 20px;
            }}
        </style>
    </head>

    <body>

        <div class="card">

            <h1>🔥 AI Eğitim Sistemi</h1>

            <h2>Kullanıcı: {username}</h2>

            <h2>🏆 Score: {score}</h2>

            <h2>⚡ XP: {xp}</h2>

            <h2>🔥 Level: {level}</h2>

            <div class="bar">
                <div class="fill"></div>
            </div>

            <br>

            <form action="/add_xp">
                <button>XP KAZAN</button>
            </form>

        </div>

    </body>
    </html>
    """

    conn.close()

    return html


@app.route("/add_xp")
def add_xp():

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE users
    SET xp = xp + 25,
        score = score + 10
    WHERE username = ?
    """, ("Efe",))

    conn.commit()

    # Yeni level hesapla
    cursor.execute("SELECT xp FROM users WHERE username = ?", ("Efe",))
    xp = cursor.fetchone()["xp"]

    level = calculate_level(xp)

    cursor.execute("""
    UPDATE users
    SET level = ?
    WHERE username = ?
    """, (level, "Efe"))

    conn.commit()
    conn.close()

    return """
    <script>
    window.location.href = "/";
    </script>
    """


# ---------------- START ---------------- #

setup_database()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)