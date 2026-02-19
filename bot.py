import telebot
import random
import datetime
import sqlite3
import time
import re

TOKEN = "8359797506:AAEd2dpPEULaKt9kJ-LoOQqRaN0a7bqeM-c"
bot = telebot.TeleBot(TOKEN)

# ===== قاعدة البيانات =====
conn = sqlite3.connect("bot_v8.db", check_same_thread=False)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    points INTEGER DEFAULT 0,
    coins INTEGER DEFAULT 0,
    messages INTEGER DEFAULT 0,
    last_daily TEXT DEFAULT '',
    vip INTEGER DEFAULT 0
)
""")
conn.commit()

def get_user(uid):
    cur.execute("SELECT * FROM users WHERE user_id=?", (uid,))
    row = cur.fetchone()
    if not row:
        cur.execute("INSERT INTO users (user_id) VALUES (?)", (uid,))
        conn.commit()
        return get_user(uid)
    return row

def add_user(uid, field, value):
    cur.execute(f"UPDATE users SET {field}={field}+? WHERE user_id=?", (value, uid))
    conn.commit()

def set_user(uid, field, value):
    cur.execute(f"UPDATE users SET {field}=? WHERE user_id=?", (value, uid))
    conn.commit()

def get_rank(points):
    if points < 100:
        return "🥉 مبتدئ"
    elif points < 300:
        return "🥈 نشيط"
    elif points < 700:
        return "🥇 محترف"
    else:
        return "👑 أسطورة"

# ===== أنظمة =====
muted = {}
last_messages = {}
bad_words = ["سب", "قليل ادب"]

def is_muted(uid):
    if uid in muted and time.time() < muted[uid]:
        return True
    if uid in muted:
        del muted[uid]
    return False

def anti_spam(uid):
    now = time.time()
    if uid not in last_messages:
        last_messages[uid] = []
    last_messages[uid] = [t for t in last_messages[uid] if now - t < 5]
    last_messages[uid].append(now)
    return len(last_messages[uid]) > 6

def contains_link(text):
    return bool(re.search(r"http[s]?://|www\.", text))

# ===== الأوامر =====
@bot.message_handler(commands=['start'])
def start(msg):
    bot.reply_to(msg, "🤖 بوت يوسف v8.0 Ultra جاهز!")

@bot.message_handler(commands=['profile'])
def profile(msg):
    user = get_user(msg.from_user.id)
    rank = get_rank(user[1])
    vip = "⭐ VIP" if user[5] else "عادي"
    bot.reply_to(msg,
        f"👤 {msg.from_user.first_name}\n"
        f"💎 نقاط: {user[1]}\n"
        f"💰 عملات: {user[2]}\n"
        f"💬 رسائل: {user[3]}\n"
        f"🏆 الرتبة: {rank}\n"
        f"🎖 الحالة: {vip}"
    )

@bot.message_handler(commands=['daily'])
def daily(msg):
    user = get_user(msg.from_user.id)
    today = datetime.date.today().isoformat()
    if user[4] == today:
        bot.reply_to(msg, "🎁 استلمت مكافأتك اليوم بالفعل!")
    else:
        add_user(msg.from_user.id, "points", 30)
        add_user(msg.from_user.id, "coins", 10)
        set_user(msg.from_user.id, "last_daily", today)
        bot.reply_to(msg, "🎉 حصلت على 30 نقطة و10 عملات!")

@bot.message_handler(commands=['top'])
def top(msg):
    cur.execute("SELECT user_id, points FROM users ORDER BY points DESC LIMIT 10")
    rows = cur.fetchall()
    text = "🏆 Top 10:\n"
    for i, r in enumerate(rows, 1):
        text += f"{i}. {r[0]} - {r[1]} نقطة\n"
    bot.reply_to(msg, text)

@bot.message_handler(commands=['shop'])
def shop(msg):
    bot.reply_to(msg,
        "🏪 المتجر:\n"
        "1️⃣ VIP لمدة دائمة = 100 عملة\n"
        "استخدم: /buy 1"
    )

@bot.message_handler(commands=['buy'])
def buy(msg):
    user = get_user(msg.from_user.id)
    if "1" in msg.text:
        if user[2] >= 100:
            add_user(msg.from_user.id, "coins", -100)
            set_user(msg.from_user.id, "vip", 1)
            bot.reply_to(msg, "⭐ أصبحت VIP!")
        else:
            bot.reply_to(msg, "❌ لا تملك عملات كافية.")

@bot.message_handler(commands=['transfer'])
def transfer(msg):
    if msg.reply_to_message:
        try:
            amount = int(msg.text.split()[1])
            sender = get_user(msg.from_user.id)
            if sender[2] >= amount:
                add_user(msg.from_user.id, "coins", -amount)
                add_user(msg.reply_to_message.from_user.id, "coins", amount)
                bot.reply_to(msg, "💸 تم التحويل!")
            else:
                bot.reply_to(msg, "❌ لا تملك عملات كافية.")
        except:
            bot.reply_to(msg, "استخدم:\n/transfer 10 (بالرد)")

@bot.message_handler(commands=['mute'])
def mute(msg):
    if msg.reply_to_message:
        muted[msg.reply_to_message.from_user.id] = time.time() + 60
        bot.reply_to(msg, "🔇 تم الكتم دقيقة.")

# ===== الرسائل =====
@bot.message_handler(func=lambda m: True)
def handle(msg):
    uid = msg.from_user.id

    if is_muted(uid):
        return

    if anti_spam(uid):
        bot.reply_to(msg, "🚫 سبام!")
        return

    text = msg.text.lower()

    if contains_link(text):
        bot.reply_to(msg, "🚫 الروابط غير مسموحة.")
        return

    for word in bad_words:
        if word in text:
            bot.reply_to(msg, "🚫 يرجى احترام القوانين.")
            return

    add_user(uid, "messages", 1)
    add_user(uid, "points", 2)

    if "السلام" in text:
        bot.reply_to(msg, "وعليكم السلام 💙")
        return
    if "ههه" in text:
        bot.reply_to(msg, "😂😂")
        return
    if "حزين" in text:
        bot.reply_to(msg, "😢 لا تزعل يا بطل")
        return

    bot.reply_to(msg, random.choice([
        "🔥 استمر!",
        "👍 جميل",
        "😎 رهيب",
        "💪 ممتاز"
    ]))

print("🚀 بوت يوسف v8.0 يعمل الآن...")
bot.infinity_polling(skip_pending=True)
