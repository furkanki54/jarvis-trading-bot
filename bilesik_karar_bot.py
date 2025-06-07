import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import pandas as pd
from ai_predictor import predict_price_movement

# Coin listesi
with open("coinlist.txt", "r") as f:
    coin_list = [line.strip().upper() for line in f.readlines()]

# Bot Token
TOKEN = "8171630986:AAFUJ6tTJsAYDg6ZeOt0AyU43k3RjaKmfGc"

logging.basicConfig(level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🧠 Jarvis Bileşik Karar Botu hazır. Örnek: BTC analiz")

async def analiz_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip().upper()
    if not text.endswith("ANALIZ"):
        return

    coin = text.replace(" ANALIZ", "").strip()
    if coin not in coin_list:
        return  # Sessizce geç, düzeltme mesajı yok

    # Simülasyon: Teknik veriler
    fiyat = 104950.00
    rsi_list = [3, 2, 4, 3]
    macd_list = [2, 3, 3, 4]
    ema_list = [3, 2, 3, 3]
    volume_list = [10, 12, 9, 15]
    price_list = [100000, 102000, 103500, 104950]

    rsi_str = str(rsi_list)
    macd_str = str(macd_list)
    ema_str = str(ema_list)

    ortalama_puan = round((sum(rsi_list + macd_list + ema_list)) / 12, 2)
    yorum = "🐂 Boğa piyasası" if ortalama_puan >= 7 else "🐻 Ayı piyasası" if ortalama_puan <= 3 else "🔄 Nötr"

    mesaj = f"""
📊 Teknik Analiz: {coin}
Fiyat: {fiyat} USDT
———————————————
🔹 RSI Puanları: {rsi_str}
🔹 MACD Puanları: {macd_str}
🔹 EMA Puanları: {ema_str}
🎯 Ortalama Puan: {ortalama_puan}/10
💬 Yorum: {yorum}
""".strip()

    ai_yorum = predict_price_movement(rsi_list, macd_list, ema_list, volume_list, price_list)
    mesaj += f"\n\n{ai_yorum}"

    await update.message.reply_text(mesaj)

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, analiz_handler))
    app.run_polling()
