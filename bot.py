import os
import logging
import sys
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import yt_dlp

# إعداد اللوجات
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

TOKEN = os.environ.get("TELEGRAM_TOKEN")

# أمر start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚀 البوت يعمل! أرسل رابط يوتيوب لأقوم بالتحميل.")

# أمر download
async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = ' '.join(context.args)
    if not url:
        await update.message.reply_text("❌ الرجاء وضع رابط التحميل.")
        return

    filename = 'video.mp4'
    try:
        ydl_opts = {
            'format': 'best[ext=mp4]/best',
            'outtmpl': filename,
            'max_filesize': 45*1024*1024  # 45 ميجا كحد أقصى
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        await update.message.reply_document(document=open(filename, 'rb'))
    except Exception as e:
        await update.message.reply_text(f"❌ حدث خطأ: {e}")
    finally:
        if os.path.exists(filename):
            os.remove(filename)

# heartbeat لتجنب timeout GitHub Actions
async def heartbeat():
    while True:
        print("💓 البوت يعمل... لا تغلقني 😅", flush=True)
        await asyncio.sleep(5)

if __name__ == '__main__':
    if not TOKEN:
        sys.exit(1)

    # بناء التطبيق
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("download", download))

    # تشغيل البوت والـ heartbeat معًا
    async def main():
        await asyncio.gather(
            app.run_polling(drop_pending_updates=True),
            heartbeat()
        )

    asyncio.run(main())
