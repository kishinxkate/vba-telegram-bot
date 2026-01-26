import os
from openai import OpenAI
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

SYSTEM_PROMPT = (
    "You are an expert Excel VBA developer. "
    "Return ONLY clean, ready-to-run VBA macro code. "
    "No explanation. No markdown."
)

async def generate_vba(prompt: str) -> str:
    response = client.responses.create(
        model="gpt-4.1-mini",
        input=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
    )
    return response.output_text.strip()

async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    vba_code = await generate_vba(user_text)
    await update.message.reply_text("🧾 VBA Code:\n\n" + vba_code)

app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply))

print("🤖 VBA GPT Bot running on Railway...")
app.run_polling()
