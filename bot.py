import os
import logging
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import yt_dlp

# إعداد السجلات لمراقبة الأداء في GitHub Actions
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = os.environ.get("TELEGRAM_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 أهلاً بك في بوت تحميل يوتيوب!\nاستخدم الأمر: /download [رابط الفيديو]")

async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = ' '.join(context.args)
    if not url:
        await update.message.reply_text("❌ الرجاء إرسال رابط بعد الأمر، مثال:\n/download https://youtube.com/watch?v=xxxx")
        return

    status_msg = await update.message.reply_text("⏳ جاري معالجة الفيديو... يرجى الانتظار.")
    
    try:
        # إعدادات yt-dlp للتحميل بجودة معقولة وحجم أقل من 50 ميجا
        file_name = f"video_{update.effective_user.id}.mp4"
        ydl_opts = {
            'format': 'best[ext=mp4]/best',
            'outtmpl': file_name,
            'max_filesize': 48 * 1024 * 1024, # 48 ميجا بايت
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        await update.message.reply_document(
            document=open(file_name, 'rb'),
            caption="✅ تم التحميل بنجاح!"
        )
        
        # حذف الملف بعد الإرسال لتوفير المساحة
        if os.path.exists(file_name):
            os.remove(file_name)

    except Exception as e:
        logger.error(f"Error: {e}")
        await update.message.reply_text(f"❌ حدث خطأ أثناء التحميل: {str(e)}")
    finally:
        await status_msg.delete()

if __name__ == '__main__':
    if not TOKEN:
        print("❌ Error: TELEGRAM_TOKEN variable is missing!")
    else:
        print("🚀 Bot is starting...")
        app = ApplicationBuilder().token(TOKEN).build()
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("download", download))
        
        # التشغيل بنظام Polling
        app.run_polling()
