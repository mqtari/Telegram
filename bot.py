import os
import logging
import sys
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import yt_dlp

# إعداد السجلات لتظهر فوراً في GitHub Actions دون تأخير (Flush)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

TOKEN = os.environ.get("TELEGRAM_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚀 البوت يعمل الآن بكفاءة على GitHub Actions!\nأرسل /download متبوعاً برابط اليوتيوب.")

async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = ' '.join(context.args)
    if not url:
        await update.message.reply_text("⚠️ أرسل الرابط هكذا: /download [رابط الفيديو]")
        return

    msg = await update.message.reply_text("⏳ جاري التحميل... يرجى الانتظار")
    try:
        file_name = "video.mp4"
        ydl_opts = {
            'format': 'best[ext=mp4]/best',
            'outtmpl': file_name,
            'max_filesize': 45 * 1024 * 1024, # ضمان عدم تجاوز 50 ميجا
            'quiet': True
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        await update.message.reply_document(document=open(file_name, 'rb'))
        os.remove(file_name)
    except Exception as e:
        await update.message.reply_text(f"❌ خطأ: {str(e)}")
    finally:
        await msg.delete()

if __name__ == '__main__':
    if not TOKEN:
        logger.error("TELEGRAM_TOKEN is missing!")
        sys.exit(1)

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("download", download))

    logger.info("Starting bot with drop_pending_updates=True...")
    # السر هنا: drop_pending_updates تمسح كل الرسائل القديمة ليعمل البوت فوراً على الجديد فقط
    app.run_polling(drop_pending_updates=True)
