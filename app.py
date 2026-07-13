from flask import Flask
from threading import Thread
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
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
    await update.message.reply_text("🎬 البوت يعمل!")

def run_bot():
    try:
        bot_app = Application.builder().token(TOKEN).build()
        bot_app.add_handler(CommandHandler("start", start))
        print("✅ البوت يعمل...")
        bot_app.run_polling()
    except Exception as e:
        print(f"❌ فشل تشغيل البوت: {e}")

if __name__ == '__main__':
    Thread(target=run_bot).start()
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)
