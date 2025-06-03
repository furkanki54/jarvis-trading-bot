import asyncio
from telegram import Bot
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

async def send_start_message():
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text="✅ Jarvis bot başlatıldı!")

if __name__ == "__main__":
    asyncio.run(send_start_message())
    print("Jarvis bot çalışıyor...")
    while True:
        pass  # veya time.sleep(60) koyabilirsin ama async kodda gerek yok şimdilik
