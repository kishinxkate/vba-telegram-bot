import os
import time
from openai import OpenAI
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    ContextTypes,
    CommandHandler,
    filters,
)

# ===== Environment Variables =====
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# ===== OpenAI Client =====
client = OpenAI(api_key=OPENAI_API_KEY)

# ===== Prompt =====
SYSTEM_PROMPT = (
    "You are an expert Excel VBA developer. "
    "Return ONLY clean, ready-to-run VBA macro code. "
    "No explanation. No markdown."
)

# ===== Simple Rate Limit (Cost Protection) =====
USER_LAST_CALL = {}
COOLDOWN_SECONDS = 10   # user တစ်ယောက် 10 sec တစ်ခါပဲ

def can_use(user_id: int) -> bool:
    now = time.time()
    last = USER_LAST_CALL.get(user_id, 0)
    if now - last < COOLDOWN_SECONDS:
        return False
    USER_LAST_CALL[user_id] = now
    return True

# ===== OpenAI VBA Generator =====
async def generate_vba(prompt: str) -> str:
    response = client.responses.create(
        model="gpt-4.1-mini",
        input=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
        max_output_tokens=400,
    )
    return response.output_text.strip()

# ===== /start Command =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 VBA Bot မှ ကြိုဆိုပါတယ်\n\n"
        "Excel VBA ကို စာနဲ့ပို့လိုက်ရုံနဲ့\n"
        "Macro code ပြန်ရေးပေးပါတယ် 💻\n\n"
        "ဥပမာ:\n"
        "Sheet1 က data ကို Sheet2 ထဲ copy လုပ်ချင်တယ်"
    )

# ===== Message Handler =====
async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = update.message.text

    if not can_use(user.id):
        await update.message.reply_text(
            "⏳ ခဏစောင့်ပြီး ပြန်ကြိုးစားပါ (10 sec)"
        )
        return

    try:
        vba_code = await generate_vba(text)
        await update.message.reply_text("🧾 VBA Code:\n\n" + vba_code)
    except Exception as e:
        await update.message.reply_text(
            "❌ Error ဖြစ်နေပါတယ်\nခဏနောက်မှ ပြန်ကြိုးစားပါ"
        )
        print("ERROR:", e)

# ===== Telegram App =====
app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply))

print("🤖 VBA GPT Bot running...")
app.run_polling()
