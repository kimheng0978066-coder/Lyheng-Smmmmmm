import telebot
from telebot import types
from bakong_khqr import KHQR
import sqlite3
import threading
import time
import os
import shutil

# =========================================
# CONFIG
# =========================================

BOT_TOKEN = "8957337087:AAG6HaBuZCetA5VAZtkXJZEPSfDxK3B24LU"

# GET TOKEN:
# https://developer.bakong.nbc.gov.kh/
BAKONG_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJkYXRhIjp7ImlkIjoiNTUxNmFhYjBkY2RiNDZkZiJ9LCJpYXQiOjE3Nzk5NzA1ODksImV4cCI6MTc4Nzc0NjU4OX0.3YQkq6xPsC6-bY5dV0dxFY-h8xcJgwdZiwRz-G1ibMc"

ADMIN_ID = 8697847759
GROUP_ID = -1003981921256

BANK_ACCOUNT = "sokkhem_mov@trmc"
MERCHANT_NAME = "LYHENG SMM BOT"
PHONE_NUMBER = "0884139775"

# =========================================
# BOT
# =========================================

bot = telebot.TeleBot(BOT_TOKEN)
khqr = KHQR(BAKONG_TOKEN)

# =========================================
# DATABASE
# =========================================

conn = sqlite3.connect(
    "bot.db",
    check_same_thread=False
)

cursor = conn.cursor()

# USERS
cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    balance REAL DEFAULT 0,
    banned INTEGER DEFAULT 0
)
""")

# ORDERS
cursor.execute("""
CREATE TABLE IF NOT EXISTS orders(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    service TEXT,
    package TEXT,
    link TEXT,
    price REAL,
    quantity INTEGER,
    status TEXT,
    order_api_id TEXT,
    created_at TEXT
)
""")

conn.commit()

# =========================================
# FIX OLD DATABASE
# =========================================

fix_queries = [

"""
ALTER TABLE users
ADD COLUMN username TEXT
""",

"""
ALTER TABLE users
ADD COLUMN balance REAL DEFAULT 0
""",

"""
ALTER TABLE users
ADD COLUMN banned INTEGER DEFAULT 0
""",

"""
ALTER TABLE orders
ADD COLUMN service TEXT
""",

"""
ALTER TABLE orders
ADD COLUMN package TEXT
""",

"""
ALTER TABLE orders
ADD COLUMN link TEXT
""",

"""
ALTER TABLE orders
ADD COLUMN price REAL
""",

"""
ALTER TABLE orders
ADD COLUMN quantity INTEGER
""",

"""
ALTER TABLE orders
ADD COLUMN status TEXT
""",

"""
ALTER TABLE orders
ADD COLUMN order_api_id TEXT
""",

"""
ALTER TABLE orders
ADD COLUMN created_at TEXT
"""

]

for query in fix_queries:

    try:

        cursor.execute(query)
        conn.commit()

    except:
        pass

# =========================================
# PACKAGES
# =========================================

BOOST_PACKAGES = {

    "📊 300-800 Like = $0.99": {
        "price": 0.99,
        "quantity": 800
    },

    "📊 600-1.6K Like = $1.50": {
        "price": 1.50,
        "quantity": 1600
    },

    "📊 827-2.1K Like = $2.00": {
        "price": 2.00,
        "quantity": 2100
    },

    "📊 1.1K-4.2K Like = $3.00": {
        "price": 3.00,
        "quantity": 4200
    },

    "📊 2K-5.6K Like = $5.00": {
        "price": 5.00,
        "quantity": 5600
    }

}

# =========================================
# MENUS
# =========================================

def main_menu(is_admin=False):

    markup = types.ReplyKeyboardMarkup(
        resize_keyboard=True
    )

    markup.row("👤 គណនី", "🛒 សេវាកម្ម")
    markup.row("💳 ដាក់ប្រាក់", "📦 ប្រវត្តិបញ្ជាទិញ")
    markup.row("🆘 Support")

    if is_admin:
        markup.row("🛠 Admin Panel")

    return markup

def services_menu():

    markup = types.ReplyKeyboardMarkup(
        resize_keyboard=True
    )

    markup.row("🎵 TikTok Services")
    markup.row("🏠 Main Menu")

    return markup

def tiktok_menu():

    markup = types.ReplyKeyboardMarkup(
        resize_keyboard=True
    )

    markup.row("🔥 TikTok Boost Khmer")
    markup.row("❤️ TikTok Like")
    markup.row("👁 TikTok View")
    markup.row("👥 TikTok Follow")

    markup.row("⬅️ Back To Services")
    markup.row("🏠 Main Menu")

    return markup

def boost_menu():

    markup = types.ReplyKeyboardMarkup(
        resize_keyboard=True
    )

    for package in BOOST_PACKAGES:
        markup.row(package)

    markup.row("⬅️ Back To TikTok")
    markup.row("🏠 Main Menu")

    return markup

def admin_menu():

    markup = types.ReplyKeyboardMarkup(
        resize_keyboard=True
    )

    markup.row("➕ Add Balance")
    markup.row("➖ Remove Balance")

    markup.row("🚫 Ban User")
    markup.row("✅ Unban User")

    markup.row("📦 All Orders")

    markup.row("🏠 Main Menu")

    return markup

# =========================================
# START
# =========================================

@bot.message_handler(commands=['start'])
def start(message):

    user_id = message.from_user.id
    username = message.from_user.username

    cursor.execute("""
    INSERT OR IGNORE INTO users(
        user_id,
        username
    )
    VALUES(?,?)
    """, (
        user_id,
        username
    ))

    conn.commit()

    cursor.execute("""
    SELECT banned
    FROM users
    WHERE user_id=?
    """, (user_id,))

    banned = cursor.fetchone()[0]

    if banned == 1:

        bot.send_message(
            message.chat.id,
            "🚫 គណនីរបស់អ្នកត្រូវបានបិទ"
        )
        return

    bot.send_message(
        message.chat.id,
"""
🙏 សូមស្វាគមន៍មកកាន់ SMM BOT

✨ សូមជ្រើសមុខងារខាងក្រោម
""",
        reply_markup=main_menu(
            user_id == ADMIN_ID
        )
    )

# =========================================
# ACCOUNT
# =========================================

@bot.message_handler(func=lambda m: m.text == "👤 គណនី")
def account(message):

    cursor.execute("""
    SELECT username,balance
    FROM users
    WHERE user_id=?
    """, (message.from_user.id,))

    user = cursor.fetchone()

    bot.send_message(
        message.chat.id,
f"""
👤 គណនីរបស់អ្នក

🆔 ID: {message.from_user.id}
📛 Username: @{user[0]}
💰 Balance: ${round(user[1],2)}
"""
    )

# =========================================
# SERVICES
# =========================================

@bot.message_handler(func=lambda m: m.text == "🛒 សេវាកម្ម")
def services(message):

    bot.send_message(
        message.chat.id,
        "🛒 សូមជ្រើសសេវាកម្ម",
        reply_markup=services_menu()
    )

# =========================================
# TIKTOK SERVICES
# =========================================

@bot.message_handler(func=lambda m: m.text == "🎵 TikTok Services")
def tiktok_services(message):

    bot.send_message(
        message.chat.id,
        "🎵 TikTok Services",
        reply_markup=tiktok_menu()
    )

# =========================================
# BOOST MENU
# =========================================

@bot.message_handler(func=lambda m: m.text == "🔥 TikTok Boost Khmer")
def boost(message):

    bot.send_message(
        message.chat.id,
"""
🔥 TikTok Boost Khmer

📊 300-800 Like = $0.99
📊 600-1.6K Like = $1.50
📊 827-2.1K Like = $2.00
📊 1.1K-4.2K Like = $3.00
📊 2K-5.6K Like = $5.00
""",
        reply_markup=boost_menu()
    )

# =========================================
# BUY PACKAGE
# =========================================

@bot.message_handler(func=lambda m: m.text in BOOST_PACKAGES)
def buy_package(message):

    package_name = message.text

    package = BOOST_PACKAGES[package_name]

    price = package["price"]
    quantity = package["quantity"]

    cursor.execute("""
    SELECT balance
    FROM users
    WHERE user_id=?
    """, (message.from_user.id,))

    balance = cursor.fetchone()[0]

    if balance < price:

        bot.send_message(
            message.chat.id,
f"""
❌ គណនីរបស់អ្នកមិនគ្រប់គ្រាន់ទេ

💰 តម្លៃ: ${price}
💵 Balance: ${round(balance,2)}

🙏 សូមដាក់ប្រាក់ជាមុន
"""
        )
        return

    msg = bot.send_message(
        message.chat.id,
        "🔗 សូមផ្ញើ Link TikTok"
    )

    bot.register_next_step_handler(
        msg,
        process_order,
        package_name,
        price,
        quantity
    )

# =========================================
# PROCESS ORDER
# =========================================

def process_order(
    message,
    package_name,
    price,
    quantity
):

    link = message.text

    if "tiktok.com" not in link:

        bot.send_message(
            message.chat.id,
            "❌ Link TikTok មិនត្រឹមត្រូវ"
        )
        return

    user_id = message.from_user.id

    cursor.execute("""
    UPDATE users
    SET balance = balance - ?
    WHERE user_id=?
    """, (
        price,
        user_id
    ))

    order_id = f"TT{int(time.time())}"

    cursor.execute("""
    INSERT INTO orders(
        user_id,
        service,
        package,
        link,
        price,
        quantity,
        status,
        order_api_id,
        created_at
    )
    VALUES(?,?,?,?,?,?,?,?,datetime('now'))
    """, (
        user_id,
        "TikTok Boost Khmer",
        package_name,
        link,
        price,
        quantity,
        "Pending",
        order_id
    ))

    conn.commit()

    bot.send_message(
        GROUP_ID,
f"""
📦 NEW ORDER

🆔 {order_id}

👤 USER:
{user_id}

📦 PACKAGE:
{package_name}

🔗 LINK:
{link}

💰 PRICE:
${price}

📌 STATUS:
Pending
"""
    )

    bot.send_message(
        message.chat.id,
f"""
✅ ការបញ្ជាទិញជោគជ័យ

📦 {package_name}

💰 ${price}

📌 Status: Pending

🙏 សូមអរគុណ
"""
    )

# =========================================
# HISTORY
# =========================================

@bot.message_handler(func=lambda m: m.text == "📦 ប្រវត្តិបញ្ជាទិញ")
def history(message):

    cursor.execute("""
    SELECT package,price,status
    FROM orders
    WHERE user_id=?
    ORDER BY id DESC
    LIMIT 10
    """, (message.from_user.id,))

    orders = cursor.fetchall()

    if not orders:

        bot.send_message(
            message.chat.id,
            "📦 មិនទាន់មានប្រវត្តិបញ្ជាទិញ"
        )
        return

    text = "📦 ប្រវត្តិបញ្ជាទិញ\n\n"

    for order in orders:

        text += f"""
📦 {order[0]}
💰 ${order[1]}
📌 {order[2]}

"""

    bot.send_message(
        message.chat.id,
        text
    )

# =========================================
# DEPOSIT
# =========================================

@bot.message_handler(func=lambda m: m.text == "💳 ដាក់ប្រាក់")
def deposit(message):

    msg = bot.send_message(
        message.chat.id,
"""
💳 សូមបញ្ចូលចំនួនទឹកប្រាក់

ឧទាហរណ៍:
1
5
10
"""
    )

    bot.register_next_step_handler(
        msg,
        create_payment
    )

# =========================================
# CREATE PAYMENT
# =========================================

def create_payment(message):

    try:

        amount = float(message.text)

    except:

        bot.send_message(
            message.chat.id,
            "❌ ចំនួនមិនត្រឹមត្រូវ"
        )
        return

    try:

        bill_number = f"INV{int(time.time())}"

        qr = khqr.create_qr(
            bank_account=BANK_ACCOUNT,
            merchant_name=MERCHANT_NAME,
            merchant_city="Phnom Penh",
            amount=amount,
            currency="USD",
            bill_number=bill_number,
            store_label="SMM BOT",
            phone_number=PHONE_NUMBER,
            terminal_label="BOT01",
            static=False,
            expiration=5
        )

        qr_image = khqr.qr_image(qr)

        md5 = khqr.generate_md5(qr)

        sent = bot.send_photo(
            message.chat.id,
            open(qr_image, "rb"),
f"""
💳 ABA KHQR PAYMENT

💰 Amount: ${amount}

⌛ QR មានសុពលភាព 5 នាទី
"""
        )

        threading.Thread(
            target=check_payment,
            args=(
                md5,
                message.chat.id,
                message.from_user.id,
                amount,
                sent.message_id,
                qr_image
            )
        ).start()

    except Exception as e:

        print(e)

        bot.send_message(
            message.chat.id,
"""
❌ PAYMENT ERROR

🔑 សូមពិនិត្យ BAKONG TOKEN
"""
        )

# =========================================
# CHECK PAYMENT
# =========================================

def check_payment(
    md5,
    chat_id,
    user_id,
    amount,
    message_id,
    qr_image
):

    timeout = time.time() + 300

    while True:

        try:

            if time.time() > timeout:

                try:
                    bot.delete_message(chat_id, message_id)
                    os.remove(qr_image)
                except:
                    pass

                bot.send_message(
                    chat_id,
                    "⌛ QR ផុតសុពលភាព"
                )

                break

            result = khqr.check_payment(md5)

            print("RESULT:", result)

            if str(result).upper() == "PAID":

                cursor.execute("""
                UPDATE users
                SET balance = balance + ?
                WHERE user_id=?
                """, (
                    amount,
                    user_id
                ))

                conn.commit()

                try:
                    bot.delete_message(chat_id, message_id)
                    os.remove(qr_image)
                except:
                    pass

                bot.send_message(
                    chat_id,
f"""
🎉 ការបង់ប្រាក់ជោគជ័យ

💰 ${amount}

💳 Balance បានបន្ថែម
"""
                )

                break

            time.sleep(5)

        except Exception as e:

            print("CHECK ERROR:", e)
            time.sleep(5)

# =========================================
# ADMIN PANEL
# =========================================

@bot.message_handler(func=lambda m: m.text == "🛠 Admin Panel")
def admin_panel(message):

    if message.from_user.id != ADMIN_ID:
        return

    bot.send_message(
        message.chat.id,
        "🛠 ADMIN PANEL",
        reply_markup=admin_menu()
    )

# =========================================
# ADD BALANCE
# =========================================

@bot.message_handler(func=lambda m: m.text == "➕ Add Balance")
def add_balance(message):

    if message.from_user.id != ADMIN_ID:
        return

    msg = bot.send_message(
        message.chat.id,
        "📥 USER_ID AMOUNT"
    )

    bot.register_next_step_handler(
        msg,
        process_add_balance
    )

def process_add_balance(message):

    try:

        data = message.text.split()

        user_id = int(data[0])
        amount = float(data[1])

        cursor.execute("""
        UPDATE users
        SET balance = balance + ?
        WHERE user_id=?
        """, (
            amount,
            user_id
        ))

        conn.commit()

        bot.send_message(
            message.chat.id,
            "✅ Balance Added"
        )

    except Exception as e:

        print(e)

# =========================================
# REMOVE BALANCE
# =========================================

@bot.message_handler(func=lambda m: m.text == "➖ Remove Balance")
def remove_balance(message):

    if message.from_user.id != ADMIN_ID:
        return

    msg = bot.send_message(
        message.chat.id,
        "📥 USER_ID AMOUNT"
    )

    bot.register_next_step_handler(
        msg,
        process_remove_balance
    )

def process_remove_balance(message):

    try:

        data = message.text.split()

        user_id = int(data[0])
        amount = float(data[1])

        cursor.execute("""
        UPDATE users
        SET balance = balance - ?
        WHERE user_id=?
        """, (
            amount,
            user_id
        ))

        conn.commit()

        bot.send_message(
            message.chat.id,
            "✅ Balance Removed"
        )

    except Exception as e:

        print(e)

# =========================================
# BACK BUTTONS
# =========================================

@bot.message_handler(func=lambda m: m.text == "⬅️ Back To Services")
def back_services(message):

    bot.send_message(
        message.chat.id,
        "🛒 Services",
        reply_markup=services_menu()
    )

@bot.message_handler(func=lambda m: m.text == "⬅️ Back To TikTok")
def back_tiktok(message):

    bot.send_message(
        message.chat.id,
        "🎵 TikTok Services",
        reply_markup=tiktok_menu()
    )

@bot.message_handler(func=lambda m: m.text == "🏠 Main Menu")
def back_main(message):

    bot.send_message(
        message.chat.id,
        "🏠 Main Menu",
        reply_markup=main_menu(
            message.from_user.id == ADMIN_ID
        )
    )

# =========================================
# AUTO BACKUP
# =========================================

def auto_backup():

    while True:

        try:

            shutil.copy(
                "bot.db",
                "backup_bot.db"
            )

            print("✅ DATABASE BACKUP DONE")

        except Exception as e:

            print("BACKUP ERROR:", e)

        time.sleep(300)

threading.Thread(
    target=auto_backup
).start()

# =========================================
# RUN BOT
# =========================================

print("BOT RUNNING...")
bot.infinity_polling()
