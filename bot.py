import os
import random
from telebot import TeleBot, types
from apscheduler.schedulers.background import BackgroundScheduler

# === إعدادات البوت ===
TOKEN = "8359797506:AAEd2dpPEULaKt9kJ-LoOQqRaN0a7bqeM-c"
bot = TeleBot(TOKEN)

CHANNEL_LINK = "https://t.me/Y_USUF24"
GROUP_LINK = "https://t.me/YUSU_F24"

# === قاعدة البيانات البسيطة ===
USERS = {}
VIDEOS = []

ADKAR_MORNING = ["ذكر 1 صباحاً", "ذكر 2 صباحاً"]
ADKAR_EVENING = ["ذكر 1 مساءً", "ذكر 2 مساءً"]

QURAN = [
    {"name": "سورة الفاتحة", "text": "بسم الله الرحمن الرحيم...", "audio": "audio1.mp3", "image": "image1.jpg"},
    {"name": "سورة الإخلاص", "text": "قل هو الله أحد...", "audio": "audio2.mp3", "image": "image2.jpg"}
]

RAMADAN_DUA = [
    "اللهم بلغنا رمضان وأعنا على صيامه وقيام ليلة قدره",
    "اللهم اجعل صيامنا فيه صيام الصائمين وقيامنا فيه قيام القائمين",
    "اللهم اجعلنا من عتقاء هذا الشهر الكريم"
]

ANIMATIONS = {
    "video": "anim_video.gif",
    "watch_videos": "anim_watch.gif",
    "adhkar": "anim_adhkar.gif",
    "quran": "anim_quran.gif",
    "ramadan_dua": "anim_dua.gif",
    "ai_chat": "anim_ai.gif"
}

# === واجهة الأزرار الرئيسية ===
def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("📹 أضف رابط فيديو", "🎬 مشاهدة الفيديوهات")
    markup.row("🕋 أذكار اليوم", "📖 القرآن اليوم")
    markup.row("🙏 أدعية رمضان", "🤖 تحدث مع الذكاء الاصطناعي")
    return markup

# === إرسال GIF بأمان ===
def send_animation(chat_id, key):
    path = ANIMATIONS.get(key)
    if path and os.path.exists(path):
        try:
            with open(path, 'rb') as f:
                bot.send_animation(chat_id, f)
        except Exception as e:
            print(f"Error sending animation {key}: {e}")

# === التحقق من الاشتراك (افتراضيًا True) ===
def check_subscription(user_id):
    return True

# === START COMMAND ===
@bot.message_handler(commands=['start'])
def start(message):
    if not check_subscription(message.from_user.id):
        bot.send_message(
            message.chat.id,
            f"يرجى الاشتراك بالقناة: {CHANNEL_LINK}\nوبالمجموعة: {GROUP_LINK}"
        )
        return
    USERS.setdefault(message.from_user.id, {"last_adhkar": 0})
    bot.send_message(message.chat.id, "مرحباً بك! اختر من القائمة:", reply_markup=main_menu())

# === إضافة رابط فيديو ===
@bot.message_handler(func=lambda m: m.text == "📹 أضف رابط فيديو")
def add_video(message):
    send_animation(message.chat.id, "video")
    try:
        msg = bot.send_message(message.chat.id, "أرسل رابط الفيديو من تلغرام:")
        bot.register_next_step_handler(msg, save_video)
    except Exception as e:
        print(f"Add video handler error: {e}")

def save_video(message):
    link = message.text.strip()
    if link.startswith("https://t.me/"):
        VIDEOS.append(link)
        bot.send_message(message.chat.id, "✅ تم إضافة الفيديو بنجاح!")
    else:
        bot.send_message(message.chat.id, "❌ الرابط غير صحيح، حاول مرة أخرى.")

# === مشاهدة الفيديوهات ===
@bot.message_handler(func=lambda m: m.text == "🎬 مشاهدة الفيديوهات")
def watch_videos(message):
    send_animation(message.chat.id, "watch_videos")
    if not VIDEOS:
        bot.send_message(message.chat.id, "لا توجد فيديوهات مخزنة حالياً.")
        return
    for vid in VIDEOS:
        try:
            markup = types.InlineKeyboardMarkup()
            button = types.InlineKeyboardButton("مشاهدة الفيديو", url=vid)
            markup.add(button)
            bot.send_message(message.chat.id, "🎥 فيديو جديد:", reply_markup=markup)
        except Exception as e:
            print(f"Watch video error: {e}")

# === أذكار اليوم ===
@bot.message_handler(func=lambda m: m.text == "🕋 أذكار اليوم")
def send_adhkar(message):
    send_animation(message.chat.id, "adhkar")
    user = USERS.get(message.from_user.id)
    idx = user["last_adhkar"]
    all_adkar = ADKAR_MORNING + ADKAR_EVENING
    if idx < len(all_adkar):
        bot.send_message(message.chat.id, all_adkar[idx])
        USERS[message.from_user.id]["last_adhkar"] += 1
    else:
        bot.send_message(message.chat.id, "✅ تم قراءة كل الأذكار اليوم 🌸")

# === سور القرآن ===
@bot.message_handler(func=lambda m: m.text == "📖 القرآن اليوم")
def send_quran(message):
    send_animation(message.chat.id, "quran")
    ayah = random.choice(QURAN)
    bot.send_message(message.chat.id, f"{ayah['name']}\n\n{ayah['text']}")
    try:
        if os.path.exists(ayah['image']):
            with open(ayah['image'], 'rb') as img:
                bot.send_photo(message.chat.id, img)
        if os.path.exists(ayah['audio']):
            with open(ayah['audio'], 'rb') as audio_file:
                bot.send_audio(message.chat.id, audio_file)
    except Exception as e:
        print(f"Quran send error: {e}")

# === أدعية رمضان ===
@bot.message_handler(func=lambda m: m.text == "🙏 أدعية رمضان")
def send_ramadan_dua(message):
    send_animation(message.chat.id, "ramadan_dua")
    dua = random.choice(RAMADAN_DUA)
    bot.send_message(message.chat.id, f"🤲 دعاء اليوم:\n{dua}")

# === دردشة AI مجانية ===
@bot.message_handler(func=lambda m: m.text == "🤖 تحدث مع الذكاء الاصطناعي")
def chat_ai(message):
    send_animation(message.chat.id, "ai_chat")
    try:
        msg = bot.send_message(message.chat.id, "اكتب سؤالك:")
        bot.register_next_step_handler(msg, ai_response)
    except Exception as e:
        print(f"AI handler error: {e}")

def ai_response(message):
    user_input = message.text
    response = f"🤖 رد الذكاء الاصطناعي:\nلقد قلت: {user_input}\nتذكر الصبر والإيمان!"
    bot.send_message(message.chat.id, response)

# === وظائف النشر التلقائي باستخدام APScheduler ===
scheduler = BackgroundScheduler()

def auto_adhkar():
    for user_id in USERS:
        try:
            for adkar in ADKAR_MORNING + ADKAR_EVENING:
                bot.send_message(user_id, adkar)
        except: pass

def auto_quran():
    for user_id in USERS:
        try:
            ayah = random.choice(QURAN)
            bot.send_message(user_id, f"{ayah['name']}\n\n{ayah['text']}")
        except: pass

def auto_ramadan_dua():
    for user_id in USERS:
        try:
            dua = random.choice(RAMADAN_DUA)
            bot.send_message(user_id, f"🤲 دعاء رمضاني:\n{dua}")
        except: pass

# === جدولة المهام ===
scheduler.add_job(auto_adhkar, 'cron', hour=7, minute=0)
scheduler.add_job(auto_adhkar, 'cron', hour=19, minute=0)
scheduler.add_job(auto_quran, 'cron', hour=8, minute=0)
scheduler.add_job(auto_ramadan_dua, 'cron', hour=12, minute=0)
scheduler.add_job(auto_ramadan_dua, 'cron', hour=18, minute=0)
scheduler.start()

# === تشغيل البوت ===
bot.infinity_polling()
