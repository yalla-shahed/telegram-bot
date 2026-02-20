# ================== الاعدادات ==================
TOKEN = "8503228903:AAH6SLaQFzNjhpsOVa6WNUnZ0jylB0BfhwI"
ADMIN_ID = 1706616766
FORCE_CHANNEL = "@YUSU_F24"
FORCE_GROUP   = "@Y_USUF24"
MENU_KEY = "يوسف"
# ===============================================

import json
import random
import re
from datetime import time as dtime
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    CallbackQueryHandler,
    filters,
)

CONTENT_FILE = "content.json"

# ================= تحميل البيانات =================

def load_json(file):
    try:
        with open(file, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def save_json(file, data):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

CONTENT = load_json(CONTENT_FILE)
WAITING_RENAME = {}

# ================= ردود ذكية =================

SMART_REPLIES = {
    "مرحبا": "أهلاً وسهلاً بك 🌹 كيف أقدر أساعدك؟",
    "هلا": "ياهلا وغلا 👋",
    "شلونك": "تمام الحمدلله 😊 وانت كيفك؟",
    "كيفك": "بخير دامك بخير ✨",
    "شكرا": "العفو 🤍",
    "احبك": "وأنا بعد أحبك 🤍🔥",
}

# ================= أدعية رمضان =================

RAMADAN_DUAS = [
    "اللهم بلغنا رمضان لا فاقدين ولا مفقودين 🌙",
    "اللهم اجعلنا من عتقائك من النار في هذا الشهر الكريم 🤲",
    "اللهم تقبل صيامنا وقيامنا 🌙",
    "اللهم ارزقنا حسن الخاتمة 🤍",
]

# ================= الاشتراك =================

def subscription_keyboard():
    keyboard = [
        [InlineKeyboardButton("📢 الدخول إلى القناة",
                              url=f"https://t.me/{FORCE_CHANNEL.replace('@','')}")],
        [InlineKeyboardButton("👥 الدخول إلى الجروب",
                              url=f"https://t.me/{FORCE_GROUP.replace('@','')}")],
        [InlineKeyboardButton("✅ التحقق من الاشتراك",
                              callback_data="check_sub")]
    ]
    return InlineKeyboardMarkup(keyboard)

async def check_subscription(user_id, bot):
    if user_id == ADMIN_ID:
        return True
    try:
        ch = await bot.get_chat_member(FORCE_CHANNEL, user_id)
        gr = await bot.get_chat_member(FORCE_GROUP, user_id)
        return ch.status not in ["left", "kicked"] and \
               gr.status not in ["left", "kicked"]
    except:
        return False

# ================= البداية =================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    subscribed = await check_subscription(update.effective_user.id, context.bot)

    if not subscribed:
        await update.message.reply_text(
            "🔒 يجب الاشتراك أولاً للاستفادة من البوت",
            reply_markup=subscription_keyboard()
        )
        return

    await update.message.reply_text("✨ أهلاً بك\nاكتب 'يوسف' لعرض القائمة.")

# ================= القائمة =================

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not CONTENT:
        await update.message.reply_text("📂 لا يوجد محتوى حالياً.")
        return

    text = "📂 قائمة المحتوى:\n\n"
    for item in CONTENT:
        text += f"• {item}\n"

    await update.message.reply_text(text)

# ================= حفظ محتوى =================

async def save_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    msg = update.message

    if msg.video:
        name = msg.caption or f"فيديو {len(CONTENT)+1}"
        CONTENT[name] = {"type": "video", "value": msg.video.file_id}
        save_json(CONTENT_FILE, CONTENT)
        await msg.reply_text(f"✅ تم حفظ الفيديو باسم: {name}")

# ================= تغيير اسم =================

async def rename(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    try:
        text = update.message.text.replace("/rename", "").strip()
        old_name, new_name = text.split("|")
        old_name = old_name.strip()
        new_name = new_name.strip()

        if old_name not in CONTENT:
            await update.message.reply_text("❌ الاسم غير موجود.")
            return

        CONTENT[new_name] = CONTENT.pop(old_name)
        save_json(CONTENT_FILE, CONTENT)

        await update.message.reply_text("✅ تم تغيير الاسم بنجاح")

    except:
        await update.message.reply_text("⚠️ استخدم:\n/rename القديم | الجديد")

# ================= ذكاء محلي =================

async def smart_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    for key in SMART_REPLIES:
        if key in text:
            await update.message.reply_text(SMART_REPLIES[key])
            return

# ================= أدعية =================

async def dua(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(random.choice(RAMADAN_DUAS))

# ================= نشر يومي =================

async def daily_post(context: ContextTypes.DEFAULT_TYPE):
    if not CONTENT:
        return

    name = random.choice(list(CONTENT.keys()))
    item = CONTENT[name]

    if item["type"] == "video":
        await context.bot.send_video(
            chat_id=FORCE_GROUP,
            video=item["value"],
            caption=f"🎥 {name}"
        )

# ================= ذكر كل ساعة =================

async def hourly_reminder(context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=FORCE_GROUP,
        text="اللهم صلِّ وسلم على سيدنا محمد 🤍"
    )

# ================= التشغيل =================

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("rename", rename))
    app.add_handler(CommandHandler("dua", dua))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, smart_chat))
    app.add_handler(MessageHandler(filters.VIDEO, save_file))

    # نشر يومي الساعة 9 مساء
    app.job_queue.run_daily(daily_post, time=dtime(hour=21, minute=0))

    # كل ساعة ذكر
    app.job_queue.run_repeating(hourly_reminder, interval=3600, first=10)

    app.run_polling()

if __name__ == "__main__":
    main()
