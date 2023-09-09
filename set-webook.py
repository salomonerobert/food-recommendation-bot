import os
from telebot import TeleBot

TELEGRAM_BOT_API_KEY = os.getenv('TELEGRAM_BOT_API_KEY')
bot = TeleBot(TELEGRAM_BOT_API_KEY)
# Set Webhook
def set_webhook(request):
    bot.remove_webhook()
    bot.set_webhook(url=f"https://asia-southeast1-brilliant-lens-353909.cloudfunctions.net/process_update")
    return 'Webhook set', 200