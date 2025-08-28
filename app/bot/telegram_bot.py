import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Cargar variables de entorno
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("¡Hola! Soy NutriChat 🤖")

def run_bot():
    if not TELEGRAM_TOKEN:
        print("ERROR: Token de Telegram no configurado")
        return
    
    print(f"Conectando bot con token: {TELEGRAM_TOKEN[:10]}...")
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    print("Bot iniciado. Presiona Ctrl+C para detener.")
    app.run_polling()
