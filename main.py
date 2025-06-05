import telebot
from config import TELEGRAM_TOKEN
from helpers import analyze_coin
from formasyonlar import get_price_data, find_trend_break

bot = telebot.TeleBot(TELEGRAM_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, "📈 Hoş geldin! Coin ismi (örn: BTCUSDT) gönder, sana teknik analiz yapayım.")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    coin = message.text.strip().upper()

    if coin.endswith("USDT"):
        bot.send_message(message.chat.id, f"🔍 {coin} analiz ediliyor...")

        try:
            analysis = analyze_coin(coin)

            # Trend kırılımı kontrolü (1H grafik)
            prices = get_price_data(coin, interval="1h", limit=100)
            sinyal, trend_price, current = find_trend_break(prices)

            if sinyal:
                analysis += f"\n\n⚠️ {sinyal}\n📉 Trend çizgisi seviyesi: {trend_price}\n💰 Güncel fiyat: {current}"

            bot.send_message(message.chat.id, analysis)
        except Exception as e:
            bot.send_message(message.chat.id, f"⚠️ Hata oluştu:\n{str(e)}")
    else:
        bot.send_message(message.chat.id, "❗ Lütfen geçerli bir coin ismi gir (örn: BTCUSDT)")

print("Bot çalışıyor...")
bot.polling()
