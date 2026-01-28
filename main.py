import os
import time
import google.generativeai as genai
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    ContextTypes,
    CommandHandler,
    filters,
)

# ===== ENV =====
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# ===== Gemini Setup =====
genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction=(
        "You are an expert Excel VBA developer. "
        "Return ONLY clean, ready-to-run VBA macro code. "
        "No explanation. No markdown."
    ),
)

# ===== 🔐 ALLOWED USERS =====
ALLOWED_USERS = {
    8263890862,   # 👈 ကိုယ့် Telegram user_id
}

# ===== RATE LIMIT =====
USER_LAST = {}
COOLDOWN = 10

def can_use(uid):
    now = time.time()
    if now - USER_LAST.get(uid, 0) < COOLDOWN:
        return False
    USER_LAST[uid] = now
    return True

# ===== /start =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ALLOWED_USERS:
        await update.message.reply_text("🚫 သုံးခွင့်မရှိပါ")
        return

    await update.message.reply_text(
        "👋 Gemini VBA Bot မှ ကြိုဆိုပါတယ်\n"
        "Excel VBA ကို စာနဲ့ပို့လိုက်ရုံနဲ့ Macro ပြန်ရေးပေးပါတယ်"
    )

# ===== MESSAGE HANDLER =====
async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    if user.id not in ALLOWED_USERS:
        await update.message.reply_text("🚫 သုံးခွင့်မရှိပါ")
        return

    if not can_use(user.id):
        await update.message.reply_text("⏳ ခဏစောင့်ပြီး ပြန်ကြိုးစားပါ")
        return

    try:
        response = model.generate_content(update.message.text)
        await update.message.reply_text("🧾 VBA Code:\n\n" + response.text.strip())

    except Exception as e:
        await update.message.reply_text("❌ Gemini Error:\n" + str(e))
        print("GEMINI ERROR:", e)

# ===== APP =====
app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply))

print("🤖 Gemini VBA Bot running...")
app.run_polling()
