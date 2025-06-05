import telebot
from config import TELEGRAM_TOKEN
from helpers import analyze_coin

bot = telebot.TeleBot(TELEGRAM_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, "📈 Hoş geldin! Coin ismini (örnek: BTCUSDT) yazarak teknik analiz alabilirsin.")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    coin = message.text.strip().upper()

    if coin.endswith("USDT"):
        bot.send_message(message.chat.id, f"🔍 {coin} analiz ediliyor, lütfen bekleyin...")
        try:
            analysis = analyze_coin(coin)
            bot.send_message(message.chat.id, analysis)
        except Exception as e:
            bot.send_message(message.chat.id, f"⚠️ Analiz sırasında bir hata oluştu:\n{str(e)}")
    else:
        bot.send_message(message.chat.id, "❗ Lütfen geçerli bir coin ismi gir (örnek: BTCUSDT)")

print("Bot çalışıyor...")
bot.polling()
