import telebot
import json
import random
import os
import time

TOKEN = "8359797506:AAEd2dpPEULaKt9kJ-LoOQqRaN0a7bqeM-c"
ADMIN_ID = 1706616766
CHANNEL_USERNAME = "YUSU_F24"

bot = telebot.TeleBot(TOKEN)
DATA_FILE = "data.json"

# تحميل البيانات
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r") as f:
        data = json.load(f)
else:
    data = {"users": {}, "banned": []}

def save():
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

def add_user(uid, ref=None):
    uid = str(uid)
    if uid not in data["users"]:
        data["users"][uid] = {
            "points": 0,
            "level": 1,
            "last_daily": 0,
            "warnings": 0,
            "messages": 0
        }
        if ref and ref in data["users"]:
            data["users"][ref]["points"] += 5
        save()

def check_level(uid):
    user = data["users"][uid]
    if user["points"] >= user["level"] * 50:
        user["level"] += 1
        bot.send_message(uid, f"🎉 مبروك! وصلت لفل {user['level']}")
        save()

# تحقق اشتراك
def check_subscription(user_id):
    if user_id == ADMIN_ID:
        return True
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

# مضاد سبام
last_msg = {}

# ألعاب
guess_games = {}
fast_game = False

# START
@bot.message_handler(commands=["start"])
def start(msg):
    uid = str(msg.from_user.id)

    if not check_subscription(msg.from_user.id):
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(
            telebot.types.InlineKeyboardButton(
                "📢 اشترك بالقناة",
                url=f"https://t.me/{CHANNEL_USERNAME.replace('@','')}"
            )
        )
        markup.add(
            telebot.types.InlineKeyboardButton(
                "✅ تحقق من الاشتراك",
                callback_data="check_sub"
            )
        )
        bot.send_message(msg.chat.id,
                         "⚠️ يجب الاشتراك بالقناة لاستخدام البوت",
                         reply_markup=markup)
        return

    if uid in data["banned"]:
        return

    ref = None
    if len(msg.text.split()) > 1:
        ref = msg.text.split()[1]

    add_user(uid, ref)

    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("💰 نقاطي", "🎮 تخمين")
    markup.add("⚡ أسرع زر", "🎁 يومي")
    markup.add("🛒 متجر", "🔗 رابط الدعوة")
    markup.add("🏆 الترتيب", "📊 المستخدمين")

    if msg.from_user.id == ADMIN_ID:
        markup.add("👑 لوحة الأدمن")

    bot.send_message(msg.chat.id,
                     "👑 أهلاً بك في البوت النهائي 🔥",
                     reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "check_sub")
def callback_check(call):
    if check_subscription(call.from_user.id):
        bot.answer_callback_query(call.id, "✅ تم التحقق")
        start(call.message)
    else:
        bot.answer_callback_query(call.id, "❌ لم تشترك بعد")

# استقبال الصور
@bot.message_handler(content_types=['photo'])
def photo(msg):
    bot.send_message(msg.chat.id, "📸 صورة جميلة 😍")

# جميع الرسائل النصية
@bot.message_handler(func=lambda m: True, content_types=['text'])
def all_messages(msg):
    global fast_game
    uid = str(msg.from_user.id)

    if uid in data["banned"]:
        return

    if not check_subscription(msg.from_user.id):
        return

    now = time.time()
    if uid in last_msg and now - last_msg[uid] < 1:
        return
    last_msg[uid] = now

    if uid in data["users"]:
        data["users"][uid]["messages"] += 1

    text = msg.text

    if text == "💰 نقاطي":
        user = data["users"][uid]
        bot.send_message(msg.chat.id,
                         f"💰 نقاطك: {user['points']}\n🎖 لفل: {user['level']}")

    elif text == "🎮 تخمين":
        guess_games[msg.from_user.id] = random.randint(1, 5)
        bot.send_message(msg.chat.id, "خمنت رقم بين 1 و5؟")

    elif text.isdigit() and msg.from_user.id in guess_games:
        if int(text) == guess_games[msg.from_user.id]:
            data["users"][uid]["points"] += 10
            check_level(uid)
            bot.send_message(msg.chat.id, "🎉 صح! +10 نقاط")
        else:
            bot.send_message(msg.chat.id,
                             f"❌ غلط، كان {guess_games[msg.from_user.id]}")
        del guess_games[msg.from_user.id]

    elif text == "⚡ أسرع زر":
        fast_game = True
        bot.send_message(msg.chat.id,
                         "أول واحد يكتب (فزت) ياخذ 15 نقطة!")

    elif text == "فزت" and fast_game:
        data["users"][uid]["points"] += 15
        check_level(uid)
        bot.send_message(msg.chat.id,
                         f"🏆 {msg.from_user.first_name} فاز +15")
        fast_game = False

    elif text == "🎁 يومي":
        now = time.time()
        if now - data["users"][uid]["last_daily"] > 86400:
            data["users"][uid]["points"] += 20
            data["users"][uid]["last_daily"] = now
            bot.send_message(msg.chat.id, "🎁 +20 نقاط")
        else:
            bot.send_message(msg.chat.id, "⏳ تعال بكرا")

    elif text == "🛒 متجر":
        bot.send_message(msg.chat.id,
                         "🛒 متجر:\nلقب مميز = 100 نقطة")

    elif text == "🔗 رابط الدعوة":
        link = f"https://t.me/{bot.get_me().username}?start={uid}"
        bot.send_message(msg.chat.id, f"رابطك:\n{link}")

    elif text == "🏆 الترتيب":
        sorted_users = sorted(
            data["users"].items(),
            key=lambda x: x[1]["points"],
            reverse=True
        )[:10]
        t = "🏆 أفضل اللاعبين:\n\n"
        for i, u in enumerate(sorted_users, 1):
            t += f"{i}- {u[0]} | {u[1]['points']}\n"
        bot.send_message(msg.chat.id, t)

    elif text == "📊 المستخدمين":
        bot.send_message(msg.chat.id,
                         f"👥 العدد: {len(data['users'])}")

    elif text == "👑 لوحة الأدمن" and msg.from_user.id == ADMIN_ID:
        bot.send_message(msg.chat.id,
                         "/stats\n/top\n/broadcast نص\n/warn ID\n/ban ID\n/unban ID")

    elif "مرحبا" in text:
        bot.reply_to(msg, "أهلاً 👋")
    elif "كيفك" in text:
        bot.reply_to(msg, "تمام 😎")

    save()

# أوامر الأدمن
@bot.message_handler(commands=["stats"])
def stats(msg):
    if msg.from_user.id != ADMIN_ID:
        return
    total_points = sum(u["points"] for u in data["users"].values())
    total_msgs = sum(u["messages"] for u in data["users"].values())
    bot.send_message(msg.chat.id,
                     f"👥 {len(data['users'])}\n💰 {total_points}\n💬 {total_msgs}")

@bot.message_handler(commands=["broadcast"])
def broadcast(msg):
    if msg.from_user.id != ADMIN_ID:
        return
    text = msg.text.replace("/broadcast ", "")
    for u in data["users"]:
        try:
            bot.send_message(u, text)
        except:
            pass

@bot.message_handler(commands=["ban"])
def ban(msg):
    if msg.from_user.id != ADMIN_ID:
        return
    uid = msg.text.split()[1]
    data["banned"].append(uid)
    save()

@bot.message_handler(commands=["unban"])
def unban(msg):
    if msg.from_user.id != ADMIN_ID:
        return
    uid = msg.text.split()[1]
    if uid in data["banned"]:
        data["banned"].remove(uid)
        save()

bot.infinity_polling(none_stop=True)

