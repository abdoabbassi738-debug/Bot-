import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# جلب المتغيرات البيئية كما تم ضبطها في منصة Render تماماً
TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_URL = os.getenv("CHANNEL_URL")  # تم التعديل ليتطابق مع رندر
STORAGE_CHANNEL_ID = os.getenv("STORAGE_CHANNEL_ID")

# استخراج المعرف البرمجي للقناة (User/ID) للتحقق من العضوية
def get_chat_id():
    if "t.me/" in CHANNEL_URL:
        username = CHANNEL_URL.split("t.me/")[1].replace("+", "")
        # إذا كانت القناة خاصة وتبدأ برابط دعوة، يجب وضع الآيدي الرقمي مكانها في رندر
        if username.startswith("joinchat/") or username.startswith("chat/"):
             return CHANNEL_URL
        return f"@{username}"
    return CHANNEL_URL

CHAT_CHECK_ID = get_chat_id()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if not args:
        await update.message.reply_text("مرحباً بك! يرجى اختيار فيلم أو مسلسل من القناة العامة لتشغيله.")
        return
    
    file_id = args[0]  # هذا يمثل رقم الرسالة (Message ID) في قناة التخزين
    user_id = update.effective_user.id
    
    try:
        member = await context.bot.get_chat_member(chat_id=CHAT_CHECK_ID, user_id=user_id)
        if member.status in ['member', 'administrator', 'creator']:
            # إذا كان مشتركاً، يقوم البوت بنسخ الرسالة المحددة من قناة التخزين وإرسالها للمستخدم مباشرة
            await context.bot.copy_message(
                chat_id=user_id,
                from_chat_id=STORAGE_CHANNEL_ID,
                message_id=int(file_id)
            )
        else:
            await request_subscription(update, file_id)
    except Exception:
        await request_subscription(update, file_id)

async def request_subscription(update: Update, file_id: str):
    keyboard = [
        [InlineKeyboardButton("اضغط هنا للاشتراك في القناة 📢", url=CHANNEL_URL)],
        [InlineKeyboardButton("تحقق من الاشتراك ✅", callback_data=f"check_{file_id}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("عذراً، يجب عليك الاشتراك في قناتنا أولاً لمشاهدة الفيلم أو المسلسل!", reply_markup=reply_markup)

async def check_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    file_id = query.data.split("_")[1]
    
    try:
        member = await context.bot.get_chat_member(chat_id=CHAT_CHECK_ID, user_id=user_id)
        if member.status in ['member', 'administrator', 'creator']:
            await query.delete_message()  # حذف رسالة طلب الاشتراك
            await context.bot.copy_message(
                chat_id=user_id,
                from_chat_id=STORAGE_CHANNEL_ID,
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
    
