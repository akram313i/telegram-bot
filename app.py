from flask import Flask, jsonify
from threading import Thread
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import yt_dlp
import os
import json
import requests
import re
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def index():
    return "✅ البوت شغال!"

@app.route('/health')
def health():
    return jsonify({"status": "ok", "time": datetime.now().isoformat()})

TOKEN = os.environ.get("TELEGRAM_TOKEN", "8778509203:AAH8uJrR_z7A_k3w8OWWllxAKf7V_qFCeNM")

USERS_FILE = "users.json"

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    return {}

def save_user(user_id, username, first_name):
    users = {}
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            users = json.load(f)
    users[str(user_id)] = {
        "username": username,
        "first_name": first_name,
        "last_used": str(datetime.now())
    }
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4)

def download_image(url, filename="image.jpg"):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code == 200:
            with open(filename, 'wb') as f:
                f.write(response.content)
            return filename
        return None
    except Exception:
        return None

WELCOME_MESSAGE = """
🎬 **مرحباً بك في بوت أكرم!**

أرسل ما تريد تحميله وسأقوم بتحميله لك فوراً.

📌 **المنصات المدعومة:**
✅ يوتيوب (فيديوهات، شورتس)
✅ تيك توك (فيديوهات فقط)
✅ تويتر/X (فيديوهات وصور)
✅ فيسبوك (فيديوهات عامة)
✅ روابط صور مباشرة (.jpg, .png, .gif)
"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    save_user(user.id, user.username, user.first_name)
    keyboard = [
        [InlineKeyboardButton("🎬 تحميل فيديو", callback_data="download_video")],
        [InlineKeyboardButton("🖼️ تحميل صورة", callback_data="download_image")],
        [InlineKeyboardButton("📊 الإحصائيات", callback_data="stats"), 
         InlineKeyboardButton("❓ مساعدة", callback_data="help")]
    ]
    await update.message.reply_text(
        f"👋 أهلاً بك {user.first_name}!\n\n{WELCOME_MESSAGE}",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "stats":
        users = load_users()
        await query.edit_message_text(f"👥 عدد المستخدمين: {len(users)}")
    elif query.data == "help":
        await query.edit_message_text("📌 أرسل رابط فيديو أو صورة للتحميل.")
    elif query.data == "download_video":
        await query.edit_message_text("✏️ أرسل رابط الفيديو الآن:")
    elif query.data == "download_image":
        await query.edit_message_text("✏️ أرسل رابط الصورة الآن:")

async def handle_content(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    save_user(user.id, user.username, user.first_name)
    url = update.message.text
    await update.message.reply_text("⏳ جاري المعالجة...")

    # تحميل الصور
    if re.search(r'\.(jpg|jpeg|png|gif|webp)(\?.*)?$', url, re.IGNORECASE):
        file = download_image(url, "image.jpg")
        if file:
            await update.message.reply_photo(open(file, "rb"))
            os.remove(file)
        else:
            await update.message.reply_text("❌ فشل تحميل الصورة.")
        return

    # تحميل الفيديوهات
    try:
        ydl_opts = {
            "format": "best[ext=mp4]",
            "outtmpl": "video.%(ext)s",
            "quiet": True,
            "no_check_certificate": True,
            "ignoreerrors": True,
            "noplaylist": True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            if info is None:
                await update.message.reply_text("❌ الرابط لا يحتوي على فيديو صالح.")
                return
            if 'entries' in info:
                info = info['entries'][0]
            file = ydl.prepare_filename(info)
            if not os.path.exists(file):
                await update.message.reply_text("❌ فشل تحميل الفيديو.")
                return
            await update.message.reply_video(open(file, "rb"))
            os.remove(file)
    except Exception as e:
        await update.message.reply_text(f"❌ فشل التحميل: {str(e)}")

def run_bot():
    bot_app = Application.builder().token(TOKEN).build()
    bot_app.add_handler(CommandHandler("start", start))
    bot_app.add_handler(CallbackQueryHandler(button_handler))
    bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_content))
    print("✅ البوت يعمل...")
    bot_app.run_polling()

if __name__ == '__main__':
    Thread(target=run_bot).start()
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)
