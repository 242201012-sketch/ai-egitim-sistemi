from flask import (
    Flask,
    render_template,
    request,
    redirect,
    session
)




import sqlite3
import os

# =========================================================
# APP
# =========================================================

app = Flask(__name__)

app.secret_key = "SUPER_SECRET_KEY"

DATABASE = "game.db"

# =========================================================
# DATABASE
# =========================================================

def get_db():

    conn = sqlite3.connect(DATABASE)

    conn.row_factory = sqlite3.Row

    return conn


def init_db():

    conn = get_db()

    cursor = conn.cursor()

    # USERS

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        username TEXT UNIQUE,

        password TEXT,

        score INTEGER DEFAULT 0,

        xp INTEGER DEFAULT 0,

        level INTEGER DEFAULT 1,

        coins INTEGER DEFAULT 0

    )
    """)

    # INVENTORY

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS inventory(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        user_id INTEGER,

        item_name TEXT,

        quantity INTEGER DEFAULT 1

    )
    """)

    # SHOP

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS shop(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        item_name TEXT,

        price INTEGER

    )
    """)

    conn.commit()

    # SHOP ITEMS

    cursor.execute(
        "SELECT * FROM shop"
    )

    items = cursor.fetchall()

    if len(items) == 0:

        default_items = [

            ("XP Potion", 100),

            ("Boss Ticket", 250),

            ("AI Crystal", 500),

            ("Epic Sword", 1000)

        ]

        cursor.executemany(
            """
            INSERT INTO shop
            (
                item_name,
                price
            )
            VALUES (?, ?)
            """,
            default_items
        )

    conn.commit()

    conn.close()


init_db()

# =========================================================
# XP SYSTEM
# =========================================================

def add_xp(user_id, gained_xp):

    conn = get_db()

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT xp, level
        FROM users
        WHERE id=?
        """,
        (user_id,)
    )

    user = cursor.fetchone()

    if user is None:

        conn.close()

        return

    current_xp = user["xp"]

    current_level = user["level"]

    new_xp = current_xp + gained_xp

    required_xp = current_level * 100

    while new_xp >= required_xp:

        new_xp -= required_xp

        current_level += 1

        required_xp = current_level * 100

    cursor.execute(
        """
        UPDATE users
        SET xp=?, level=?
        WHERE id=?
        """,
        (
            new_xp,
            current_level,
            user_id
        )
    )

    conn.commit()

    conn.close()

# =========================================================
# COIN SYSTEM
# =========================================================

def add_coins(user_id, amount):

    conn = get_db()

    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE users
        SET coins = coins + ?
        WHERE id=?
        """,
        (
            amount,
            user_id
        )
    )

    conn.commit()

    conn.close()

# =========================================================
# INVENTORY SYSTEM
# =========================================================

def add_item(user_id, item_name):

    conn = get_db()

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM inventory
        WHERE user_id=? AND item_name=?
        """,
        (
            user_id,
            item_name
        )
    )

    item = cursor.fetchone()

    if item:

        cursor.execute(
            """
            UPDATE inventory
            SET quantity = quantity + 1
            WHERE id=?
            """,
            (item["id"],)
        )

    else:

        cursor.execute(
            """
            INSERT INTO inventory
            (
                user_id,
                item_name,
                quantity
            )
            VALUES (?, ?, ?)
            """,
            (
                user_id,
                item_name,
                1
            )
        )

    conn.commit()

    conn.close()


# =========================================================
# ACHIEVEMENT SYSTEM
# app.py içine EKLE
# add_item() fonksiyonunun ALTINA koy
# =========================================================

def init_achievement_system():

    conn = get_db()

    cursor = conn.cursor()

    # ACHIEVEMENTS

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS achievements(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        title TEXT,

        description TEXT,

        reward INTEGER
    )
    """)

    # USER ACHIEVEMENTS

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_achievements(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        user_id INTEGER,

        achievement_id INTEGER
    )
    """)

    conn.commit()

    # DEFAULT ACHIEVEMENTS

    cursor.execute(
        "SELECT * FROM achievements"
    )

    achievements = cursor.fetchall()

    if len(achievements) == 0:

        default_achievements = [

            (
                "First Login",
                "İlk giriş yapıldı",
                50
            ),

            (
                "Level 5",
                "Level 5 oldun",
                250
            ),

            (
                "XP Master",
                "500 XP kazandın",
                500
            ),

            (
                "Boss Slayer",
                "Boss savaşı tamamlandı",
                300
            ),

            (
                "Rich Player",
                "1000 coin toplandı",
                400
            )

        ]

        cursor.executemany(
            """
            INSERT INTO achievements
            (
                title,
                description,
                reward
            )
            VALUES (?, ?, ?)
            """,
            default_achievements
        )

    conn.commit()

    conn.close()


init_achievement_system()

# =========================================================
# CHECK ACHIEVEMENT
# =========================================================

def has_achievement(user_id, achievement_title):

    conn = get_db()

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT ua.id
        FROM user_achievements ua

        JOIN achievements a
        ON ua.achievement_id = a.id

        WHERE ua.user_id=? AND a.title=?
        """,
        (
            user_id,
            achievement_title
        )
    )

    result = cursor.fetchone()

    conn.close()

    return result is not None

# =========================================================
# GIVE ACHIEVEMENT
# =========================================================

def give_achievement(user_id, achievement_title):

    if has_achievement(user_id, achievement_title):

        return

    conn = get_db()

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM achievements
        WHERE title=?
        """,
        (achievement_title,)
    )

    achievement = cursor.fetchone()

    if achievement is None:

        conn.close()

        return

    # ACHIEVEMENT EKLE

    cursor.execute(
        """
        INSERT INTO user_achievements
        (
            user_id,
            achievement_id
        )
        VALUES (?, ?)
        """,
        (
            user_id,
            achievement["id"]
        )
    )

    # REWARD COIN

    cursor.execute(
        """
        UPDATE users
        SET coins = coins + ?
        WHERE id=?
        """,
        (
            achievement["reward"],
            user_id
        )
    )

    conn.commit()

    conn.close()

# =========================================================
# ACHIEVEMENT ENGINE
# =========================================================

def check_achievements(user_id):

    conn = get_db()

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM users
        WHERE id=?
        """,
        (user_id,)
    )

    user = cursor.fetchone()

    conn.close()

    if user is None:

        return

    # LEVEL 5

    if user["level"] >= 5:

        give_achievement(
            user_id,
            "Level 5"
        )

    # XP MASTER

    if user["xp"] >= 500:

        give_achievement(
            user_id,
            "XP Master"
        )

    # RICH PLAYER

    if user["coins"] >= 1000:

        give_achievement(
            user_id,
            "Rich Player"
        )

# =========================================================
# ACHIEVEMENTS PAGE
# =========================================================

@app.route("/achievements")
def achievements():

    if "user_id" not in session:

        return redirect("/login")

    conn = get_db()

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            a.title,
            a.description,
            a.reward

        FROM user_achievements ua

        JOIN achievements a
        ON ua.achievement_id = a.id

        WHERE ua.user_id=?
        """,
        (session["user_id"],)
    )

    achievements = cursor.fetchall()

    conn.close()

    return render_template(
        "achievements.html",
        achievements=achievements
    )



# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():

    if "user_id" not in session:

        return redirect("/login")

    conn = get_db()

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM users
        WHERE id=?
        """,
        (session["user_id"],)
    )

    user = cursor.fetchone()

    conn.close()

    if user is None:

        session.clear()

        return redirect("/login")

    xp_percent = int(
        (user["xp"] / (user["level"] * 100)) * 100
    )

    return render_template(
        "index.html",
        user=user,
        xp_percent=xp_percent
    )

# =========================================================
# REGISTER
# =========================================================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "GET":

        return render_template("register.html")

    username = request.form["username"]

    password = request.form["password"]

    conn = get_db()

    cursor = conn.cursor()

    try:

        cursor.execute(
            """
            INSERT INTO users
            (
                username,
                password,
                score,
                xp,
                level,
                coins
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                username,
                password,
                0,
                0,
                1,
                0
            )
        )

        conn.commit()

        return redirect("/login")

    except Exception as e:

        return f"KAYIT HATASI: {e}"

    finally:

        conn.close()

# =========================================================
# LOGIN
# =========================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "GET":

        return render_template("login.html")

    username = request.form["username"]

    password = request.form["password"]

    conn = get_db()

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM users
        WHERE username=? AND password=?
        """,
        (
            username,
            password
        )
    )

    user = cursor.fetchone()

    conn.close()

    if user is None:

        return """
        <h1>❌ Kullanıcı Bulunamadı</h1>
        <a href='/login'>Tekrar Dene</a>
        """

    session["user_id"] = user["id"]

    return redirect("/")

# =========================================================
# LOGOUT
# =========================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")

# =========================================================
# DAILY REWARD
# =========================================================

@app.route("/daily")
def daily():

    if "user_id" not in session:

        return redirect("/login")

    add_xp(
        session["user_id"],
        100
    )

    add_coins(
        session["user_id"],
        50
    )

    return """
    <h1>🔥 Günlük Ödül!</h1>

    <p>+100 XP</p>

    <p>+50 Coin</p>

    <a href='/'>
        Ana Sayfa
    </a>
    """

# =========================================================
# GAIN XP
# =========================================================

@app.route("/gain_xp")
def gain_xp():

    if "user_id" not in session:

        return redirect("/login")

    add_xp(
        session["user_id"],
        25
    )

    add_coins(
        session["user_id"],
        10
    )

    return redirect("/")

# =========================================================
# LEADERBOARD
# =========================================================

@app.route("/leaderboard")
def leaderboard():

    conn = get_db()

    cursor = conn.cursor()

    cursor.execute("""
    SELECT username, xp, level
    FROM users
    ORDER BY level DESC, xp DESC
    LIMIT 10
    """)

    users = cursor.fetchall()

    conn.close()

    return render_template(
        "leaderboard.html",
        users=users
    )

# =========================================================
# BOSS
# =========================================================

@app.route("/boss")
def boss():

    if "user_id" not in session:

        return redirect("/login")

    return render_template("boss.html")

# =========================================================
# BOSS ATTACK
# =========================================================

@app.route("/boss_attack", methods=["POST"])
def boss_attack():

    if "user_id" not in session:

        return redirect("/login")

    add_xp(
        session["user_id"],
        50
    )

    add_coins(
        session["user_id"],
        25
    )

    return """
    <h1>🔥 Boss'a saldırdın!</h1>

    <p>+50 XP</p>

    <p>+25 Coin</p>

    <a href='/'>
        Ana Sayfa
    </a>
    """

# =========================================================
# PROFILE PAGE
# app.py içine ekle
# =========================================================

@app.route("/profile")
def profile():

    if "user_id" not in session:

        return redirect("/login")

    conn = get_db()

    cursor = conn.cursor()

    # USER

    cursor.execute(
        """
        SELECT *
        FROM users
        WHERE id=?
        """,
        (session["user_id"],)
    )

    user = cursor.fetchone()

    # INVENTORY

    cursor.execute(
        """
        SELECT *
        FROM inventory
        WHERE user_id=?
        """,
        (session["user_id"],)
    )

    inventory = cursor.fetchall()

    # ACHIEVEMENTS

    cursor.execute(
        """
        SELECT
            a.title,
            a.description,
            a.reward

        FROM user_achievements ua

        JOIN achievements a
        ON ua.achievement_id = a.id

        WHERE ua.user_id=?
        """,
        (session["user_id"],)
    )

    achievements = cursor.fetchall()

    # RANK SYSTEM

    level = user["level"]

    if level >= 50:

        rank = "👑 AI LEGEND"

    elif level >= 40:

        rank = "💎 MASTER"

    elif level >= 30:

        rank = "🔥 DIAMOND"

    elif level >= 20:

        rank = "🥇 GOLD"

    elif level >= 10:

        rank = "🥈 SILVER"

    else:

        rank = "🥉 BRONZE"

    conn.close()

    return render_template(
        "profile.html",
        user=user,
        inventory=inventory,
        achievements=achievements,
        rank=rank
    )




# =========================================================
# SHOP
# =========================================================

@app.route("/shop")
def shop():

    if "user_id" not in session:

        return redirect("/login")

    conn = get_db()

    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM shop"
    )

    items = cursor.fetchall()

    cursor.execute(
        """
        SELECT *
        FROM users
        WHERE id=?
        """,
        (session["user_id"],)
    )

    user = cursor.fetchone()

    conn.close()

    return render_template(
        "shop.html",
        items=items,
        user=user
    )

# =========================================================
# BUY ITEM
# =========================================================

@app.route("/buy/<int:item_id>")
def buy(item_id):

    if "user_id" not in session:

        return redirect("/login")

    conn = get_db()

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM users
        WHERE id=?
        """,
        (session["user_id"],)
    )

    user = cursor.fetchone()

    cursor.execute(
        """
        SELECT *
        FROM shop
        WHERE id=?
        """,
        (item_id,)
    )

    item = cursor.fetchone()

    if item is None:

        conn.close()

        return "Item bulunamadı"

    if user["coins"] < item["price"]:

        conn.close()

        return """
        <h1>❌ Yetersiz Coin</h1>

        <a href='/shop'>
            Shop'a dön
        </a>
        """

    cursor.execute(
        """
        UPDATE users
        SET coins = coins - ?
        WHERE id=?
        """,
        (
            item["price"],
            session["user_id"]
        )
    )

    conn.commit()

    conn.close()

    add_item(
        session["user_id"],
        item["item_name"]
    )

    return redirect("/inventory")

# =========================================================
# INVENTORY
# =========================================================

@app.route("/inventory")
def inventory():

    if "user_id" not in session:

        return redirect("/login")

    conn = get_db()

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM inventory
        WHERE user_id=?
        """,
        (session["user_id"],)
    )

    items = cursor.fetchall()

    conn.close()

    return render_template(
        "inventory.html",
        items=items
    )

# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":

    port = int(
        os.environ.get("PORT", 5000)
    )

    app.run(
        host="0.0.0.0",
        port=port,
        debug=True
    )

