
from telegram import Bot
import os

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

print("TOKEN:", TOKEN)
print("CHAT_ID:", CHAT_ID)

bot = Bot(token=TOKEN)
bot.send_message(chat_id=CHAT_ID, text="✅ TEST: Telegram funktioniert!")
