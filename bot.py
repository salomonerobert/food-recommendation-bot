import os
# from telebot import TeleBot, types
# import telebot
from telegram import ReplyKeyboardMarkup, Update, Bot
from telegram.ext import Application, CommandHandler, filters, ContextTypes
from flask import Flask, request
import mapsAPIService
import mongoDBService
import re
import mapsPreviewService
import random
import logging
from dotenv import load_dotenv
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)

server = Flask(__name__)
TELEGRAM_BOT_API_KEY = os.getenv('TELEGRAM_BOT_API_KEY')
GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')
GCP_PROJECT_ID = os.getenv('GCP_PROJECT_ID')

if GOOGLE_MAPS_API_KEY is not None:
    logging.info(TELEGRAM_BOT_API_KEY)

# bot = TeleBot(TELEGRAM_BOT_API_KEY)
google_maps_service = mapsAPIService.GoogleMapsAPIService(GOOGLE_MAPS_API_KEY)
bot = Bot(token=TELEGRAM_BOT_API_KEY)

user_data = {}

# @bot.message_handler(commands=['start'])
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info('Start handler triggered')
    # markup = types.ReplyKeyboardMarkup(row_width=1)
    # itembtn1 = types.KeyboardButton('Show me good food around me!')
    # itembtn2 = types.KeyboardButton('I want to recommend a makan spot!')
    # markup.add(itembtn1, itembtn2)
    # bot.send_message(message.chat.id, "Hola {}! I'm Makan Bot! If you're in Singapore and you need to find yummy food spots near you, I'm here to help!! 😋 Click the button below to get started!".format(message.chat.first_name), reply_markup=markup)
    # bot.send_message(message.chat.id, "Help me build a foodie community by contributing your food recommendations so that I can share good makan places to others like you! Hit /info to find out more about how you can contribute your recommendations!", reply_markup=markup)

    # user = mongoDBService.get_user(message.chat.id)
    # if not user:
    #     user = mongoDBService.User(
    #         name=message.chat.first_name,
    #         chat_id=message.chat.id,
    #     )
    #     mongoDBService.create_new_user(user)
    #     user_data[message.chat.id] = user
    await update.message.reply_text('Started')
    user = mongoDBService.get_user(update.message.chat.id)
    if not user:
        user = mongoDBService.User(
            name=update.message.chat.first_name,
            chat_id=update.message.chat.id,
        )
        mongoDBService.create_new_user(user)
        user_data[update.message.chat.id] = user
    return 'OK', 200

def process_update(request):
    try:
        if request.method == 'POST':
            application = Application.builder().token(TELEGRAM_BOT_API_KEY).build()
            application.add_handler(CommandHandler("start", start))
            update = Update.de_json(request.get_json(force=True, cache=False))
            application.process_update(update)
            # bot.process_new_updates([update])
            logging.info(update)
            logging.info("Update processed successfully")
            return 'OK', 200
        else:
            return 'This endpoint is for Telegram Webhook only.', 403
    except Exception as e:
        # Log the error
        logging.error(f"An error occurred: {str(e)}")
        # You can also raise the error or return an error response if needed
        return 'Internal Server Error', 500

# Set Webhook
def set_webhook(request):
    bot.remove_webhook()
    bot.set_webhook(url=f"https://{GCP_PROJECT_ID}.cloudfunctions.net/process_update")
    return 'Webhook set', 200

#code for local testing
# bot.remove_webhook()
# bot.polling()