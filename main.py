import os
import re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# جلب توكن البوت ورابط القناة العامة من منصة Render
TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_URL = os.getenv("CHANNEL_URL")

def get_chat_id():
    if "t.me/" in CHANNEL_URL:
        username = CHANNEL_URL.split("t.me/")[1].replace("+", "")
        if username.startswith("joinchat/") or username.startswith("chat/"):
             return CHANNEL_URL
        return f"@{username}"
    return CHANNEL_URL

CHAT_CHECK_ID = get_chat_id()

# دالة لتنظيف وتجهيز معرف قناة التخزين المستلم من الرابط
def format_channel_id(channel_str):
    # إذا كان المعرف يحتوي على علامة السالب (مثل -100123456)
    if channel_str.startswith("minus"):
        channel_str = channel_str.replace("minus", "-")
    elif not channel_str.startswith("-"):
        if channel_str.startswith("100"):
            channel_str = f"-{channel_str}"
        else:
            channel_str = f"-100{channel_str}"
    return channel_str

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    user_id = update.effective_user.id
    
    if not args:
        await update.message.reply_text("مرحباً بك! يرجى اختيار فيلم أو مسلسل من القناة العامة لتشغيله.")
        return
    
    data = args[0]
    if "_" not in data:
        await update.message.reply_text("رابط التشغيل غير صالح.")
        return
        
    # تفكيك الرابط لمعرفة قناة التخزين ورقم الملف
    storage_channel, file_id = data.split("_", 1)
    storage_channel = format_channel_id(storage_channel)
        
    try:
        member = await context.bot.get_chat_member(chat_id=CHAT_CHECK_ID, user_id=user_id)
        if member.status in ['member', 'administrator', 'creator']:
            # نسخ الملف وإرساله مباشرة للمستخدم
            await context.bot.copy_message(
                chat_id=user_id,
                from_chat_id=storage_channel,
                message_id=int(file_id)
            )
        else:
            await request_subscription(update, data)
    except Exception:
        await request_subscription(update, data)

async def request_subscription(update: Update, data: str):
    keyboard = [
        [InlineKeyboardButton("اضغط هنا للاشتراك في القناة 📢", url=CHANNEL_URL)],
        [InlineKeyboardButton("تحقق من الاشتراك ✅", callback_data=f"check_{data}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("عذراً، يجب عليك الاشتراك في قناتنا أولاً لمشاهدة المحتوى!", reply_markup=reply_markup)

async def check_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    # استخراج البيانات الممررة عبر الزر
    data = query.data.replace("check_", "")
    storage_channel, file_id = data.split("_", 1)
    storage_channel = format_channel_id(storage_channel)
        
    try:
        member = await context.bot.get_chat_member(chat_id=CHAT_CHECK_ID, user_id=user_id)
        if member.status in ['member', 'administrator', 'creator']:
            await query.delete_message()
            await context.bot.copy_message(
                chat_id=user_id,
                from_chat_id=storage_channel,
                message_id=int(file_id)
            )
        else:
            await query.answer("لم تشترك في القناة بعد! رجاءً اشترك واضغط تحقق مجدداً.", show_alert=True)
    except Exception:
        await query.answer("حدث خطأ أثناء التحقق، تأكد من اشتراكك وبأن البوت مسؤول في القناة.", show_alert=True)

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(check_callback, pattern="^check_"))
    app.run_polling()

if __name__ == '__main__':
    main()
