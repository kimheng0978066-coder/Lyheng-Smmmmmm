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

BOT_TOKEN = "YOUR_BOT_TOKEN"

# BAKONG TOKEN
# https://developer.bakong.nbc.gov.kh/
BAKONG_TOKEN = "YOUR_BAKONG_TOKEN"

ADMIN_ID = 123456789
GROUP_ID = -1002492238609

BANK_ACCOUNT = "yourname@bank"
MERCHANT_NAME = "SMM BOT"
PHONE_NUMBER = "088123456"

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

# USERS TABLE
cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    balance REAL DEFAULT 0,
    banned INTEGER DEFAULT 0
)
""")

# ORDERS TABLE
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

        print("✅ DATABASE FIXED")

    except Exception as e:

        print("FIX:", e)

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
# MENU
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

📌 Available Packages

📊 300-800 Like = $0.99
📊 600-1.6K Like = $1.50
📊 827-2.1K Like = $2.00
📊 1.1K-4.2K Like = $3.00
📊 2K-5.6K Like = $5.00
""",
        reply_markup=boost_menu()
    )

# =========================================
# BUY BOOST
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

💰 Package Price: ${price}
💵 Balance: ${round(balance,2)}

🙏 សូមបញ្ចូលទឹកប្រាក់
"""
        )
        return

    msg = bot.send_message(
        message.chat.id,
"""
🔗 សូមផ្ញើ Link Video TikTok
"""
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

    # SEND GROUP
    bot.send_message(
        GROUP_ID,
f"""
📦 NEW ORDER

🆔 Order ID:
{order_id}

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

    # SUCCESS
    bot.send_message(
        message.chat.id,
f"""
✅ ការបញ្ជាទិញជោគជ័យ

📦 Package:
{package_name}

💰 Price:
${price}

📌 Status:
Pending

🙏 សូមអរគុណ
"""
    )

# =========================================
# ORDER HISTORY
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
💳 ដាក់ប្រាក់

🙏 សូមបញ្ចូលចំនួនទឹកប្រាក់
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
            "❌ ចំនួនទឹកប្រាក់មិនត្រឹមត្រូវ"
        )
        return

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

💰 Amount:
${amount}

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

                    bot.delete_message(
                        chat_id,
                        message_id
                    )

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

                bot.send_message(
                    chat_id,
f"""
🎉 ការបង់ប្រាក់ជោគជ័យ

💰 Amount:
${amount}

💳 Balance បានបន្ថែម
"""
                )

                break

            time.sleep(5)

        except Exception as e:

            print("CHECK ERROR:", e)
            time.sleep(5)

# =========================================
# SUPPORT
# =========================================

@bot.message_handler(func=lambda m: m.text == "🆘 Support")
def support(message):

    bot.send_message(
        message.chat.id,
"""
🆘 Support

📩 Telegram:
@yourusername
"""
    )

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
# RUN
# =========================================

print("BOT RUNNING...")
bot.infinity_polling()
