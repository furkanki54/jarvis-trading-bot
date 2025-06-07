import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from config import TELEGRAM_TOKEN, COIN_LIST
from analysis_utils import generate_decision

logging.basicConfig(level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Bileşik Karar Botu hazır!\nKomut: BTC analiz, ETH analiz, vb.")

async def analyze(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip().upper()
    if not text.endswith("ANALİZ"):
        return

    coin = text.replace("ANALİZ", "").strip()
    if coin not in COIN_LIST:
        await update.message.reply_text(f"❌ '{coin}' listede bulunamadı.")
        return

    try:
        logging.info(f"Analyzing {coin}")
        decision_text = generate_decision(coin)
        await update.message.reply_text(decision_text)
    except Exception as e:
        logging.error(str(e))
        await update.message.reply_text("⚠️ Hata oluştu. Lütfen tekrar dene.")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), analyze))
    app.run_polling()
