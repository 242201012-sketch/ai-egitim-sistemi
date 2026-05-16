from flask import (
    Flask,
    render_template_string,
    request,
    redirect,
    session,
    jsonify
)

import sqlite3
import requests
import random
import os

from datetime import datetime
from sqlite3 import OperationalError, IntegrityError

# =========================================================
# APP
# =========================================================

app = Flask(__name__)
app.secret_key = "SUPER_SECRET_KEY_123"

DATABASE = "game.db"

# =========================================================
# DATABASE
# =========================================================

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():

    try:

        conn = get_db()
        cursor = conn.cursor()

        # USERS
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            xp INTEGER DEFAULT 0,
            level INTEGER DEFAULT 1,
            hp INTEGER DEFAULT 100,
            coins INTEGER DEFAULT 100,
            role TEXT DEFAULT 'user',
            last_daily TEXT
        )
        """)

        # INVENTORY
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventory(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            item_name TEXT,
            rarity TEXT
        )
        """)

        # QUIZ
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS quiz_scores(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            score INTEGER
        )
        """)

        conn.commit()
        conn.close()

    except OperationalError as e:
        print(f"DB ERROR: {e}")

init_db()

# =========================================================
# HTML
# =========================================================

HTML = """

<!DOCTYPE html>
<html>

<head>

<title>🔥 FULL RPG SYSTEM</title>

<style>

body{
    background:#0f172a;
    color:white;
    font-family:Arial;
    padding:30px;
}

.card{
    background:#1e293b;
    padding:20px;
    border-radius:20px;
    margin-bottom:20px;
}

input{
    width:90%;
    padding:12px;
    margin-top:10px;
    border:none;
    border-radius:10px;
}

button{
    padding:12px;
    margin-top:10px;
    border:none;
    border-radius:10px;
    background:lime;
    font-weight:bold;
    cursor:pointer;
}

.bar{
    width:100%;
    background:#334155;
    border-radius:20px;
    overflow:hidden;
}

.fill{
    height:25px;
    background:lime;
}

li{
    margin-bottom:10px;
}

.admin{
    color:red;
}

</style>

</head>

<body>

<h1>🔥 FULL AI RPG SYSTEM</h1>

{% if not logged_in %}

<div class="card">

<h2>Register</h2>

<form method="POST" action="/register">

<input type="text" name="username" placeholder="Username" required>

<input type="password" name="password" placeholder="Password" required>

<button type="submit">Register</button>

</form>

</div>

<div class="card">

<h2>Login</h2>

<form method="POST" action="/login">

<input type="text" name="username" placeholder="Username" required>

<input type="password" name="password" placeholder="Password" required>

<button type="submit">Login</button>

</form>

</div>

{% else %}

<div class="card">

<h2>👤 {{ user['username'] }}</h2>

<p>🔥 Level: {{ user['level'] }}</p>
<p>⭐ XP: {{ user['xp'] }}</p>
<p>💰 Coins: {{ user['coins'] }}</p>
<p>❤️ HP: {{ user['hp'] }}</p>

<div class="bar">
<div class="fill" style="width: {{xp_percent}}%"></div>
</div>

<a href="/daily">
<button>🎁 Daily Reward</button>
</a>

<a href="/boss">
<button>🔥 Boss Battle</button>
</a>

<a href="/quiz">
<button>🧠 Quiz</button>
</a>

<a href="/logout">
<button>🚪 Logout</button>
</a>

</div>

<div class="card">

<h2>🤖 AI Teacher</h2>

<form method="POST" action="/ask_ai">

<input type="text" name="question" placeholder="AI Question..." required>

<button type="submit">Ask AI</button>

</form>

{% if answer %}
<hr>
<p>{{answer}}</p>
{% endif %}

</div>

<div class="card">

<h2>🎒 Inventory</h2>

<ul>

{% for item in inventory %}

<li>
{{item['item_name']}} - {{item['rarity']}}
</li>

{% endfor %}

</ul>

</div>

{% if user['role'] == 'admin' %}

<div class="card">

<h2 class="admin">🛠 ADMIN PANEL</h2>

<p>Total Users: {{total_users}}</p>

<p>Total Inventory Items: {{total_items}}</p>

</div>

{% endif %}

{% endif %}

</body>
</html>

"""

# =========================================================
# HELPERS
# =========================================================

def get_user(username):

    try:

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE username=?",
            (username,)
        )

        user = cursor.fetchone()

        conn.close()

        return user

    except OperationalError:
        return None

def get_inventory(username):

    try:

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM inventory WHERE username=?",
            (username,)
        )

        items = cursor.fetchall()

        conn.close()

        return items

    except OperationalError:
        return []

# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():

    if "username" not in session:

        return render_template_string(
            HTML,
            logged_in=False
        )

    username = session["username"]

    user = get_user(username)

    if user is None:
        session.clear()
        return redirect("/")

    inventory = get_inventory(username)

    xp_percent = user["xp"] % 100

    total_users = 0
    total_items = 0

    try:

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM users")
        total_users = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM inventory")
        total_items = cursor.fetchone()[0]

        conn.close()

    except OperationalError:
        pass

    return render_template_string(
        HTML,
        logged_in=True,
        user=user,
        inventory=inventory,
        xp_percent=xp_percent,
        total_users=total_users,
        total_items=total_items,
        answer=None
    )

# =========================================================
# REGISTER
# =========================================================

@app.route("/register", methods=["POST"])
def register():

    username = request.form.get("username", "").strip()
    password = request.form.get("password", "").strip()

    if len(username) < 3:
        return "Username too short"

    if len(password) < 3:
        return "Password too short"

    try:

        conn = get_db()
        cursor = conn.cursor()

        role = "admin" if username.lower() == "efe" else "user"

        cursor.execute("""
        INSERT INTO users(
            username,
            password,
            xp,
            level,
            hp,
            coins,
            role
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            username,
            password,
            0,
            1,
            100,
            100,
            role
        ))

        conn.commit()
        conn.close()

        return redirect("/")

    except IntegrityError:
        return "Username already exists"

    except OperationalError as e:
        return f"Database error: {e}"

# =========================================================
# LOGIN
# =========================================================

@app.route("/login", methods=["POST"])
def login():

    username = request.form.get("username", "").strip()
    password = request.form.get("password", "").strip()

    try:

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("""
        SELECT * FROM users
        WHERE username=? AND password=?
        """, (
            username,
            password
        ))

        user = cursor.fetchone()

        conn.close()

        if user is None:
            return "Wrong username or password"

        session["username"] = username

        return redirect("/")

    except OperationalError as e:
        return f"DB ERROR: {e}"

# =========================================================
# LOGOUT
# =========================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")

# =========================================================
# DAILY REWARD
# =========================================================

@app.route("/daily")
def daily():

    if "username" not in session:
        return redirect("/")

    username = session["username"]

    try:

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE username=?",
            (username,)
        )

        user = cursor.fetchone()

        if user is None:
            session.clear()
            return redirect("/")

        today = datetime.now().strftime("%Y-%m-%d")

        if user["last_daily"] == today:
            conn.close()
            return "Daily already claimed"

        reward = random.randint(50, 150)

        cursor.execute("""
        UPDATE users
        SET coins = coins + ?,
            last_daily = ?
        WHERE username=?
        """, (
            reward,
            today,
            username
        ))

        conn.commit()
        conn.close()

        return redirect("/")

    except OperationalError as e:
        return f"DB ERROR: {e}"

# =========================================================
# BOSS BATTLE
# =========================================================

@app.route("/boss")
def boss():

    if "username" not in session:
        return redirect("/")

    username = session["username"]

    rarities = [
        "Common",
        "Rare",
        "Epic",
        "Legendary"
    ]

    items = [
        "Dragon Sword",
        "Cyber Armor",
        "AI Crystal",
        "Shadow Blade",
        "Quantum Staff"
    ]

    xp_gain = random.randint(20, 80)
    coin_gain = random.randint(10, 60)

    item = random.choice(items)
    rarity = random.choice(rarities)

    try:

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("""
        UPDATE users
        SET xp = xp + ?,
            coins = coins + ?
        WHERE username=?
        """, (
            xp_gain,
            coin_gain,
            username
        ))

        cursor.execute("""
        INSERT INTO inventory(
            username,
            item_name,
            rarity
        )
        VALUES (?, ?, ?)
        """, (
            username,
            item,
            rarity
        ))

        cursor.execute(
            "SELECT xp FROM users WHERE username=?",
            (username,)
        )

        xp = cursor.fetchone()["xp"]

        level = (xp // 100) + 1

        cursor.execute("""
        UPDATE users
        SET level=?
        WHERE username=?
        """, (
            level,
            username
        ))

        conn.commit()
        conn.close()

        return f"""
        <body style='background:black;color:white;font-family:Arial;padding:40px'>
        <h1>🔥 BOSS DEFEATED</h1>

        <p>XP +{xp_gain}</p>
        <p>Coins +{coin_gain}</p>

        <h2>🎁 Loot</h2>

        <p>{item} ({rarity})</p>

        <a href='/'>
        <button>Back</button>
        </a>

        </body>
        """

    except OperationalError as e:
        return f"DB ERROR: {e}"

# =========================================================
# QUIZ
# =========================================================

@app.route("/quiz")
def quiz():

    questions = [
        "Python kim tarafından geliştirildi?",
        "HTML neyin kısaltmasıdır?",
        "CSS ne işe yarar?",
        "Flask hangi dil frameworküdür?"
    ]

    return jsonify({
        "question": random.choice(questions)
    })

# =========================================================
# AI SYSTEM (OLLAMA)
# =========================================================

@app.route("/ask_ai", methods=["POST"])
def ask_ai():

    if "username" not in session:
        return redirect("/")

    question = request.form.get("question", "").strip()

    username = session["username"]

    user = get_user(username)

    if user is None:
        session.clear()
        return redirect("/")

    inventory = get_inventory(username)

    xp_percent = user["xp"] % 100

    answer = ""

    try:

        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3",
                "prompt": question,
                "stream": False
            },
            timeout=120
        )

        if response.status_code != 200:
            answer = f"AI HTTP ERROR: {response.status_code}"

        else:

            data = response.json()

            answer = data.get(
                "response",
                "AI cevap üretemedi"
            )

    except requests.exceptions.ConnectionError:
        answer = "Ollama server çalışmıyor"

    except requests.exceptions.Timeout:
        answer = "AI timeout"

    except requests.exceptions.RequestException as e:
        answer = f"AI REQUEST ERROR: {e}"

    return render_template_string(
        HTML,
        logged_in=True,
        user=user,
        inventory=inventory,
        xp_percent=xp_percent,
        total_users=0,
        total_items=0,
        answer=answer
    )

# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":

    port = int(os.environ.get("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port,
        debug=True
    )