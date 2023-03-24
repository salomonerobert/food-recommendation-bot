from audioop import add
from distutils.command.clean import clean
import os
import pymongo
from telebot import TeleBot, types
import telebot
from datetime import datetime
import datetime as dt
import re
import json
import requests
from flask import Flask
from pymongo import MongoClient
from cryptography.fernet import Fernet
from bson.objectid import ObjectId
import CategoryAndFilter as ct
import Heapsort
import math

server = Flask(__name__)
API_KEY = os.getenv('API_KEY')

bot = TeleBot(API_KEY)

user_data = {}

dir="singaporeFnBAll_final2.json"
f=open(dir,encoding='utf-8')
data=json.load(f)

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(row_width=1)
    itembtn1 = types.KeyboardButton('Show me good food around me!')
    itembtn2 = types.KeyboardButton('Customise my preference!')
    markup.add(itembtn1, itembtn2)
    bot.send_message(message.chat.id, "Hola {}! I'm Makan Bot! If you need to find yummy food spots within Singapore, I'm here to help!! 😋  Select from one of the two options below to get started!".format(message.chat.first_name), reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "Show me good food around me!")
def getLocation(message):
    keyboard = telebot.types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    location_button = telebot.types.KeyboardButton(text="Send Location", request_location=True)
    keyboard.add(location_button)
    bot.send_message(message.chat.id, "To get started, please press the button below to send your location.", reply_markup=keyboard)

def formatMsg(idx:int, item:dict):
    shopName = item['name']
    price = item['display_price']
    address = item['address']
    distance = int(item['distance'])
    recommendationScore = int(item['recommendation'])
    modified_price = len(price)*'💰'

    return """{0}) ⁣⁣
Name: {1} ⁣
Price: {2} ⁣⁣
Address: {3} ⁣
Distance: {4} metres ⁣
Recommendation Score: {5} ⁣
    """.format(idx+1,shopName, modified_price, address, distance, recommendationScore)

def checkIfEndOfResults(message):
    user_id = message.chat.id
    if user_data[user_id]['curr_index'] == len(user_data[user_id])-1:
        markup = types.ReplyKeyboardMarkup(row_width=1)
        itembtn1 = types.KeyboardButton('Show me good food around me!')
        itembtn2 = types.KeyboardButton('Customise my preference!')
        markup.add(itembtn1, itembtn2)
        bot.send_message(message.chat.id, "That's all the results we have at this time! You can change your search criteria to get different results!", reply_markup=markup)
    else:
        keyboard = telebot.types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        btn1 = telebot.types.KeyboardButton('Show me more results')
        keyboard.add(btn1)
        bot.send_message(message.chat.id, "What would you like to do next?", reply_markup=keyboard)

def sendResults(top_fifteen, user_id, message):
    for idx, item in enumerate(top_fifteen[user_data[user_id]['curr_index']: min(user_data[user_id]['curr_index']+5, len(user_data[user_id]))]):
        bot.send_message(message.chat.id, formatMsg(idx, item))

@bot.message_handler(content_types=['location'])
def handle_location(message):
    user_id = message.chat.id
    latitude = message.location.latitude
    longitude = message.location.longitude

    clean_data = ct.simplifyData(data, [latitude, longitude], 1, 1, 1)
    sorted_data = Heapsort.getItemsByField(clean_data, "recommendation", False)
    top_fifteen = sorted_data.getNextN(15)
    user_data[user_id] = {}
    user_data[user_id]['sorted_data'] = top_fifteen
    user_data[user_id]['curr_index'] = 0
    user_data[user_id]['selected_preferences'] = []

    bot.send_message(message.chat.id, "Thanks for sending your location! Your coordinates are: {} latitude, {} longitude.".format(latitude, longitude))
    sendResults(top_fifteen, user_id, message)
    
    user_data[user_id]['curr_index'] = min(user_data[user_id]['curr_index']+5, len(user_data[user_id])-1)
    checkIfEndOfResults(message)

@bot.message_handler(func=lambda message: message.text == "Show me more results")
def showMoreResults(message):
    user_id = message.chat.id
    top_fifteen = user_data[user_id]['sorted_data']
    curr_index = user_data[user_id]['curr_index']

    sendResults(top_fifteen, user_id, message)
    user_data[user_id]['curr_index'] = min(user_data[user_id]['curr_index']+5, len(user_data[user_id])-1)
    checkIfEndOfResults(message)

@bot.message_handler(func=lambda message: message.text == "Customise my preference!")
def collectPreferences(message):
    inline_keyboard = telebot.types.InlineKeyboardMarkup()
    button1 = telebot.types.InlineKeyboardButton(text="Price", callback_data="price")
    button2 = telebot.types.InlineKeyboardButton(text="Distance", callback_data="distance")
    button3 = telebot.types.InlineKeyboardButton(text="Ratings", callback_data="ratings")
    inline_keyboard.add(button1, button2, button3)
    bot.send_message(message.chat.id, "Hi there! Please rank the following options in order of preference:", reply_markup=inline_keyboard)

@bot.callback_query_handler(func=lambda query: query.data in ["price", "distance", "ratings"])
def handle_ranking(query):
    user_id = query.from_user.id
    ranking = query.data
    bot.send_chat_action(user_id, "typing")

    if user_id not in user_data.keys():
        user_data[user_id]['selected_preferences'] = []

    user_data[user_id]['selected_preferences'].append(ranking)

    bot.send_message(user_id, "Thanks for ranking! Your current order of preference is: {}".format(", ".join(user_data[user_id]['selected_preferences'])))


# @server.route('/' + API_KEY, methods=['POST'])
# def getMessage():
#     bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
#     return "!", 200

# @server.route("/")
# def webhook():
#     bot.remove_webhook()
#     bot.set_webhook(url="https://bft-telegram-bot.herokuapp.com/"+API_KEY)
#     return "!", 200

# if __name__ == "__main__":
#     server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))

#code for local testing
bot.remove_webhook()
bot.polling()