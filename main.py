import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, CallbackContext
from datetime import datetime, timedelta
import asyncio

# Keep-alive (Flask + Thread)
from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "I'm alive!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# Track clicks, forwards, cooldowns, and welcome message
user_clicks = {}
user_forward_count = {}
user_cooldowns = {}
latest_welcome_message = {}

GROUP_LINK = "https://t.me/+4WNANPIoICZlNDU9"

# /start in private
async def start(update: Update, context: CallbackContext):
    user = update.effective_user
    keyboard = [
        [InlineKeyboardButton("မမကြီး VIP ဝင်ရန် 🍑", url=GROUP_LINK)],
        [
            InlineKeyboardButton("Forward (8) 🔐",
                                 url="https://t.me/share/url?url=စောက်ရမ်းထန်တဲ့%20အန်တီမမကြီးတွေ%0Aတူတူအထန်ကြောင်းပြောမယ်%0Aမမကြီးတွေနဲ့လိုးကြောင်းပြောမယ်%0Aအထန်%20အကိတ်မမကြီး%20တွေ%20ထန်ချက်ဘဲ%20ကြိုက်ရင်%20join%20ထားလိုက်%20👉%20https://t.m/mamagyii77%0A%0A✅%20free%0A💸%20ငွေတပြားမှ%20မလိုဘူး%20👍"),
            InlineKeyboardButton("ဝင်ခွင့် အတည်ပြုရန် ✅ ", callback_data='request_access')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"""
👋 မင်္ဂလာပါ {user.first_name} ရေ

😚 မမလေးတွေနဲ့ Free ထန်ဖို့ အကောင်းဆုံးအခွင့်အရေး!

✅ Group ကို Join လုပ်ပြီး Forward 8 ချက် ပြီးရင် Access လုပ်လိုက်ပါ။

❗️အသက်ငယ်ငယ် ✋
        """,
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

# When new user joins group, hide group join message
async def welcome_new_member(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    new_user = update.message.new_chat_members[0]
    full_name = new_user.full_name
    user_id = new_user.id

    join_date = update.message.date.strftime('%Y-%m-%d')
    join_time = update.message.date.strftime('%H:%M:%S')

    if chat_id in latest_welcome_message:
        try:
            await context.bot.delete_message(chat_id=chat_id, message_id=latest_welcome_message[chat_id])
        except Exception as e:
            logging.error(f"Error deleting welcome message: {e}")

    message = f"""
🤝 ရှင့်ကို အထန်မမကြီးက ကြိုဆိုပါတယ် {full_name}

🆔 အိုင်ဒီ >>> `{user_id}`

🗓 ဝင်ရောက်သည့် နေ့စွဲ👇  
>>> {join_date} <<<

⏰ ဝင်ရောက်သည့် အချိန် 👇  
>>> {join_time} <<<

 ထွက်ရင် >>> *Auto Ban🚫* ပါတယ် ❗️

💋 *အန်တီအထန်မမကြီးတွေနဲ့ စိတ်ကြိုက်ထန်ချင်တယ်ဆိုမှ ဝင်ပါနော်

 မမကြီးတွေနဲ့ ပျော်ချင်တယ် လိုးချင်တယ်ဆိုမှ Request လုပ်ပေးပါ ✅*

🚫 စောက်ပတ်သေးသေးလေးနဲ့ အသက်ငယ်ငယ် ကလေးမလေးတွေ VIP မှာ မရှိပါဘူးနော်  ❌
    """

    keyboard = [
        [InlineKeyboardButton("အထန်မမကြီး VIP ဝင်ရန် ✅", url=GROUP_LINK)],
        [
            InlineKeyboardButton("Forward (8) 🔐",
                                 url="https://t.me/share/url?url=စောက်ရမ်းထန်တဲ့%20အန်တီမမကြီးတွေ%0Aတူတူအထန်ကြောင်းပြောမယ်%0Aမမကြီးတွေနဲ့လိုးကြောင်းပြောမယ်%0Aအထန်%20အကိတ်မမကြီး%20တွေ%20ထန်ချက်ဘဲ%20ကြိုက်ရင်%20join%20ထားလိုက်%20👉%20https://t.me/mamagyii77%0A%0A✅%20free%0A💸%20ငွေတပြားမှ%20မလိုဘူး%20👍"),
            InlineKeyboardButton("ဝင်ခွင့်အတည်ပြုရန်", callback_data='request_access')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    sent = await update.message.reply_text(message, reply_markup=reply_markup, parse_mode="Markdown")
    latest_welcome_message[chat_id] = sent.message_id

    await update.message.delete()

# Request access logic
async def request_access(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    now = datetime.now()

    if user_id not in user_clicks:
        user_clicks[user_id] = 0
    if user_id not in user_forward_count:
        user_forward_count[user_id] = 0
    if user_id not in user_cooldowns:
        user_cooldowns[user_id] = None

    cooldown_end = user_cooldowns[user_id]
    if cooldown_end and now < cooldown_end:
        await query.answer(
            "Forward လုပ်ထားသည်များကို စစ်ဆေးနေပါသည်။ စစ်ဆေးပြီးသွားလျှင် မှန်ကန်ပါက အထန်မမကြီး VIP GP ကိုထည့်ပေးပါမယ်။ မမှန်ကန်ပါက အော်တို ပယ်မယ် ဖြစ်ပါတယ်။ 30 မိနစ်စောင့်ပေးပါနော် ✅။",
            show_alert=True)
        return

    user_clicks[user_id] += 1
    clicks = user_clicks[user_id]
    count = user_forward_count[user_id]

    if count < 3:
        if clicks % 2 == 0:
            user_forward_count[user_id] += 1
    elif 3 <= count < 8:
        if clicks % 3 == 0:
            user_forward_count[user_id] += 1

    count = user_forward_count[user_id]

    if count == 8:
        user_cooldowns[user_id] = now + timedelta(minutes=30)
        await query.answer(
            "🕒 Forward လုပ်ထားသည်များကို စစ်ဆေးနေပါသည်။ စစ်ဆေးပြီးသွားလျှင် မှန်ကန်ပါက အထန်မမကြီး VIP GP ကိုထည့်ပေးပါမယ်။ မမှန်ကန်ပါက အော်တို ပယ်မယ် ဖြစ်ပါတယ်။ 30 မိနစ်စောင့်ပေးပါနော် ✅။",
            show_alert=True)
    elif count > 8:
        await query.answer("❌ Limit ကျသွားပါပြီ။", show_alert=True)
    else:
        if 1 <= count <= 3:
            await query.answer(
                f"✅ ရှင့် Forward အရေအတွက်: {count} / 8\n\n👉 Forward မှန်ကန်အောင်လုပ်ပေးပါနော်\n Foward လုပ်ပြီးမှသာ အတည်ပြုပါ ⚠️",
                show_alert=True)
        elif 4 <= count <= 5:
            await query.answer(
                f"✅ ရှင့် Forward အရေအတွက်: {count} / 8\n\n💗 အထန်မမကြီး တွေနဲ့ အရမ်းထန်ချင်နေပြီပေါ့ နော် 😚",
                show_alert=True)
        elif 6 <= count <= 7:
            await query.answer(
                f"✅ ရှင့် Forward အရေအတွက်: {count} / 8\n\nForward မှန်ကန်အောင်လုပ်ပါနော် မမှန်ကန်ပါက ဝင်ခွင့်မရနိုင်ပါ။",
                show_alert=True)

# Error logging
async def error_handler(update: object, context: CallbackContext):
    logging.error(msg="Exception while handling update:", exc_info=context.error)

# Bot start
async def main():
    application = Application.builder().token("8048967603:AAGVDzDYEFpdFFcRO9ymtNUve1iLtalIrnQ").build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_new_member))
    application.add_handler(CallbackQueryHandler(request_access, pattern='^request_access$'))
    application.add_error_handler(error_handler)

    await application.run_polling()

# Run app
if __name__ == '__main__':
    import nest_asyncio
    nest_asyncio.apply()
    keep_alive()  # Start Flask in a separate thread
    asyncio.run(main())  # Start the bot
