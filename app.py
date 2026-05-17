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



```python id="v9m3qt"
# =========================================================
# FULL COIN + INVENTORY + SHOP SYSTEM
# app.py içine ekle
# =========================================================

# =========================================================
# DATABASE UPGRADE
# =========================================================

def init_extra_tables():

    conn = get_db()

    cursor = conn.cursor()

    # USERS COINS

    try:

        cursor.execute("""
        ALTER TABLE users
        ADD COLUMN coins INTEGER DEFAULT 0
        """)

    except:
        pass

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

    # DEFAULT ITEMS

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


init_extra_tables()

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
# INVENTORY ADD
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
# SHOP PAGE
# =========================================================

@app.route("/shop")
def shop():

    if "user_id" not in session:

        return redirect("/login")

    conn = get_db()

    cursor = conn.cursor()

    # ITEMS

    cursor.execute(
        "SELECT * FROM shop"
    )

    items = cursor.fetchall()

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

    conn.close()

    html = f"""

    <h1>🛒 SHOP</h1>

    <h2>
        💰 Coin:
        {user['coins']}
    </h2>

    <hr>

    """

    for item in items:

        html += f"""

        <div style='margin-bottom:20px;'>

            <h3>
                {item['item_name']}
            </h3>

            <p>
                💰 {item['price']} Coin
            </p>

            <a href='/buy/{item['id']}'>
                Satın Al
            </a>

        </div>

        """

    return html

# =========================================================
# BUY ITEM
# =========================================================

@app.route("/buy/<int:item_id>")
def buy(item_id):

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

    # ITEM

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
        <a href='/shop'>Shop</a>
        """

    # COIN DÜŞ

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

    # ENVANTERE EKLE

    add_item(
        session["user_id"],
        item["item_name"]
    )

    return f"""

    <h1>
        ✅ {item['item_name']} satın alındı
    </h1>

    <a href='/shop'>
        Shop'a dön
    </a>

    """

# =========================================================
# INVENTORY PAGE
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

    html = """

    <h1>🎒 Inventory</h1>

    <hr>

    """

    if len(items) == 0:

        html += "<p>Envanter boş</p>"

    for item in items:

        html += f"""

        <div style='margin-bottom:20px;'>

            <h3>
                {item['item_name']}
            </h3>

            <p>
                Adet:
                {item['quantity']}
            </p>

        </div>

        """

    return html



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

    # LEVEL SYSTEM

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
                level
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                username,
                password,
                0,
                0,
                1
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
# XP TEST
# =========================================================

@app.route("/gain_xp")
def gain_xp():

    if "user_id" not in session:

        return redirect("/login")

    add_xp(
        session["user_id"],
        25
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
# BOSS BATTLE
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

    return """
    <h1>🔥 Boss'a saldırdın!</h1>
    <p>+50 XP kazandın</p>

    <a href='/'>
        Ana Sayfa
    </a>
    """

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

