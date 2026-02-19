import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# التوكن واسم القناة للتحقق من الاشتراك
TOKEN = "8359797506:AAEd2dpPEULaKt9kJ-LoOQqRaN0a7bqeM-c"
CHANNEL_ID = "@Y_USUF24"
bot = telebot.TeleBot(TOKEN)

# الفئات والمحتوى
categories = {
    "شروحات التصاميم": {"درس 1": "رابط_درس_1"},
    "برامج التصميم": {"كابتك": "رابط_كابتك", "نوت فيديو": "رابط_نوت_فيديو"},
    "إطارات جاهزة": {"إطار 1": "رابط_إطار_1"},
    "تصاميم قابلة للتعديل": {"تصميم 1": "رابط_تصميم_1"},
    "كل ما يخص الذكاء الاصطناعي": {"أداة AI 1": "رابط_AI_1"}
}

# قوائم الفئات والبرامج
def categories_keyboard():
    keyboard = InlineKeyboardMarkup()
    for cat in categories.keys():
        keyboard.add(InlineKeyboardButton(text=cat, callback_data=f"cat_{cat}"))
    return keyboard

def items_keyboard(category):
    keyboard = InlineKeyboardMarkup()
    for item in categories[category].keys():
        keyboard.add(InlineKeyboardButton(text=item, callback_data=f"item_{category}_{item}"))
    return keyboard

# التحقق من الاشتراك
def check_subscription(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status != "left"
    except:
        return False

# /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    if not check_subscription(message.from_user.id):
        bot.reply_to(message, f"⚠️ يجب الاشتراك في القناة {CHANNEL_ID} أولاً.")
        return
    bot.reply_to(message, "مرحبًا! استخدم /الفئات لعرض الفئات.")

# /الفئات
@bot.message_handler(commands=['الفئات'])
def show_categories(message):
    if not check_subscription(message.from_user.id):
        bot.reply_to(message, f"⚠️ يجب الاشتراك في القناة {CHANNEL_ID} أولاً.")
        return
    keyboard = categories_keyboard()
    bot.send_message(message.chat.id, "اختر الفئة:", reply_markup=keyboard)

# التعامل مع الأزرار
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if not check_subscription(call.from_user.id):
        bot.answer_callback_query(call.id, f"⚠️ يجب الاشتراك في القناة {CHANNEL_ID} أولاً.")
        return
    data = call.data
    if data.startswith("cat_"):
        category = data[4:]
        keyboard = items_keyboard(category)
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              text=f"اختر المحتوى من فئة: {category}",
                              reply_markup=keyboard)
    elif data.startswith("item_"):
        parts = data.split("_", 2)
        category = parts[1]
        item = parts[2]
        link = categories[category][item]
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              text=f"📥 هنا ما طلبت:\n{item}\n{link}")

# الرد على أي رسالة نصية
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    if not check_subscription(message.from_user.id):
        bot.reply_to(message, f"⚠️ يجب الاشتراك في القناة {CHANNEL_ID} أولاً.")
        return
    bot.reply_to(message, "⚠️ الميزات المتقدمة غير مدعومة على الهاتف. استخدم القوائم.")

# تشغيل البوت
bot.polling()

