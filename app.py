from flask import Flask
from threading import Thread
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp
import os

app = Flask(__name__)

@app.route('/')
def index():
    return "✅ البوت شغال!"

TOKEN = os.environ.get("TELEGRAM_TOKEN")

if not TOKEN:
    print("❌ خطأ: لم يتم العثور على TELEGRAM_TOKEN")
    exit(1)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎬 أهلاً! أرسل رابط فيديو للتحميل.")

async def video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    await update.message.reply_text("⏳ جاري التحميل...")
    try:
        ydl_opts = {"format": "best[ext=mp4]", "outtmpl": "video.%(ext)s", "quiet": True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file = ydl.prepare_filename(info)
            await update.message.reply_video(open(file, "rb"))
            os.remove(file)
    except Exception as e:
        await update.message.reply_text(f"❌ فشل التحميل: {str(e)}")

def run_bot():
    try:
        bot_app = Application.builder().token(TOKEN).build()
        bot_app.add_handler(CommandHandler("start", start))
        bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, video))
        print("✅ البوت يعمل...")
        bot_app.run_polling()
    except Exception as e:
        print(f"❌ فشل تشغيل البوت: {e}")

if __name__ == '__main__':
    Thread(target=run_bot).start()
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)
