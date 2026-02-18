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
            telebot.types
