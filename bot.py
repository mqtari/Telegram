import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import yt_dlp

# إعداد السجلات (Logs) لرؤية الأخطاء في GitHub Actions
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TOKEN = os.environ.get("TELEGRAM_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("أهلاً بك! أرسل رابط يوتيوب بعد أمر /download \nمثال: `/download https://youtube.com/...` ")

async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = ' '.join(context.args)
    if not url:
        await update.message.reply_text("الرجاء إرسال الرابط هكذا: \n /download رابط_الفيديو")
        return

    msg = await update.message.reply_text("🚀 جاري معالجة الرابط والتحميل...")
    
    try:
        # إعدادات التحميل: نختار جودة متوسطة لضمان عدم تخطي حجم 50 ميجا
        ydl_opts = {
            'format': 'best[ext=mp4]/best', 
            'outtmpl': 'downloaded_video.mp4',
            'max_filesize': 45 * 1024 * 1024  # حد أقصى 45 ميجا لضمان الإرسال
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        await update.message.reply_document(
            document=open('downloaded_video.mp4', 'rb'),
            caption="تم التحميل بنجاح عبر GitHub Actions ✅"
        )
        # حذف الملف بعد الإرسال لتوفير مساحة السيرفر
        os.remove('downloaded_video.mp4')
        
    except Exception as e:
        await update.message.reply_text(f"❌ حدث خطأ: {str(e)}")
    finally:
        await msg.delete()

if __name__ == '__main__':
    if not TOKEN:
        print("Error: TELEGRAM_TOKEN not found!")
    else:
        app = ApplicationBuilder().token(TOKEN).build()
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("download", download))
        
        print("Bot is running...")
        app.run_polling()
