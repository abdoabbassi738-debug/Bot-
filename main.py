import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# توكن البوت الخاص بك من BotFather
TOKEN = os.getenv("BOT_TOKEN")
# معرف القناة العامة التي يجب الاشتراك بها (مثال: @mychannel)
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME")
# معرف قناة التخزين السرية التي تحتوي على الأفلام
STORAGE_CHANNEL_ID = os.getenv("STORAGE_CHANNEL_ID")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # استقبال المعامل القادم مع الرابط (مثال: /start movie_123)
    args = context.args
    if not args:
        await update.message.reply_text("مرحباً بك! يرجى اختيار فيلم من القناة العامة.")
        return
    
    file_id = args[0]
    user_id = update.effective_user.id
    
    # التحقق من اشتراك المستخدم في القناة العامة
    try:
        member = await context.bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        if member.status in ['member', 'administrator', 'creator']:
            # إذا كان مشتركاً، نقوم بتوجيه المقطع أو إرسال رابط قناة التخزين
            await update.message.reply_text(f"شكرًا لاشتراكك! يمكنك مشاهدة المحتوى في قناة التخزين عبر الرابط التالي:")
            # هنا يمكنك إرسال رابط دعوة مؤقت لقناة التخزين
            invite_link = await context.bot.create_chat_invite_link(chat_id=STORAGE_CHANNEL_ID, member_limit=1)
            await update.message.reply_text(invite_link.invite_link)
        else:
            await request_subscription(update, file_id)
    except Exception:
        # في حال حدوث خطأ بالتحقق، نطلب الاشتراك للاحتياط
        await request_subscription(update, file_id)

async def request_subscription(update: Update, file_id: str):
    keyboard = [
        [InlineKeyboardButton("اضغط هنا للاشتراك في القناة 📢", url=f"https://t.me{CHANNEL_USERNAME.replace('@', '')}")],
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
        member = await context.bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        if member.status in ['member', 'administrator', 'creator']:
            invite_link = await context.bot.create_chat_invite_link(chat_id=STORAGE_CHANNEL_ID, member_limit=1)
            await query.edit_message_text(f"تم التحقق بنجاح! تفضل رابط قناة التخزين للمشاهدة:\n{invite_link.invite_link}")
        else:
            await query.answer("لم تشترك في القناة بعد! رجاءً اشترك واضغط تحقق مجدداً.", show_alert=True)
    except Exception:
        await query.answer("حدث خطأ أثناء التحقق، تأكد من اشتراكك.", show_alert=True)

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(check_callback, pattern="^check_"))
    app.run_polling()

if __name__ == '__main__':
    main()
          
