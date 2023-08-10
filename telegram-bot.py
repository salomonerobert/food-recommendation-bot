import os
from telebot import TeleBot, types
import telebot
from flask import Flask
import mapsAPIService
import mongoDBService
import re
import mapsPreviewService
import random

server = Flask(__name__)
TELEGRAM_BOT_API_KEY = os.getenv('TELEGRAM_BOT_API_KEY')
GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')

bot = TeleBot(TELEGRAM_BOT_API_KEY)
google_maps_service = mapsAPIService.GoogleMapsAPIService(GOOGLE_MAPS_API_KEY)

user_data = {}

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(row_width=1)
    itembtn1 = types.KeyboardButton('Show me good food around me!')
    itembtn2 = types.KeyboardButton('Recommend a makan spot!')
    markup.add(itembtn1, itembtn2)
    bot.send_message(message.chat.id, "Hola {}! I'm Makan Bot! If you're in Singapore and you need to find yummy food spots near you, I'm here to help!! 😋  Click the button below to get started!".format(message.chat.first_name), reply_markup=markup)
    user = mongoDBService.get_user(message.chat.id)
    if not user:
        user = mongoDBService.User(
            name=message.chat.first_name,
            chat_id=message.chat.id,
        )
        mongoDBService.create_new_user(user)
        user_data[message.chat.id] = user

def userHasSufficientCredits(user):
    markup = types.ReplyKeyboardMarkup(row_width=1)
    if user.remaining_credits < 1:
        itembtn1 = types.KeyboardButton('Recommend a makan spot!')
        markup.add(itembtn1)
        bot.send_message(user.chat_id, "Sorry! You've run out of credits, please add a recommendation to get more free credits. We rely on user inputs of good food places to eat to improve our user experience. Your contributions will greatly help other makan bot users like yourself 😊", reply_markup=markup)
        return False
    return True

@bot.message_handler(func=lambda message: message.text == "Show me good food around me!")
def getLocation(message):
    user = user_data.get(message.chat.id) or mongoDBService.get_user(message.chat.id)
    sufficientCredits = userHasSufficientCredits(user)
    if not sufficientCredits:
        return
    keyboard = telebot.types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    location_button = telebot.types.KeyboardButton(text="Send Location", request_location=True)
    keyboard.add(location_button)
    bot.send_message(message.chat.id, "Please send your location so that I can recommend some food spots near you.", reply_markup=keyboard)

def formatMsg(location):
    shopName = location.name
    address = location.address
    rating = location.rating
    thumbnail = location.thumbnail if location.thumbnail else None
    visual_rating = round(rating)*'⭐️'
    google_maps_url = location.google_maps_link
    community_ratings = location.community_recommendations

    output = """
Name: {0} ⁣
Rating: {1} {4} ⁣⁣
Address: {2} ⁣
Google Maps URL: {3} ⁣
    """.format(shopName, rating, address, google_maps_url, visual_rating)

    if community_ratings > 0:
        output += """ ⁣⁣
Recommended by Makan Bot Users! ✅
    """

    if thumbnail:
        output += """ ⁣⁣
Thumbnail: {0}
    """.format(thumbnail)

    return output

@bot.message_handler(func=lambda message: message.text == 'Recommend a makan spot!')
def request_url(message):
    chat_id = message.chat.id
    reply_markup = telebot.types.ReplyKeyboardRemove()
    message = """
Please send the Google Maps in link in one of the below formats:
1. https://maps.app.goo.gl/<location_specific_url_extension>
2. https://goo.gl/maps/<location_specific_place_id>
If you hit the "Share" button on Google maps and copy the URL it should appear in one of the above formats by default :)
"""
    bot.send_message(chat_id, message, reply_markup=reply_markup)

@bot.message_handler(content_types=['location'])
def handle_location(message):
    user = user_data.get(message.chat.id) or mongoDBService.get_user(message.chat.id)
    if not userHasSufficientCredits(user):
        return
    user_id = message.chat.id
    bot.send_chat_action(user_id, 'typing')
    latitude = message.location.latitude
    longitude = message.location.longitude
    is_result_from_db = False

    locations = mongoDBService.fetch_nearby_locations_sorted_by_reviews(longitude, latitude)

    if len(locations) < 8:
        locations = google_maps_service.fetch_nearby_food_places(longitude, latitude)
    else:
        is_result_from_db = True
    
    locations = sorted(locations, key=lambda x: x.rating, reverse=True)

    count = 0

    while count < len(locations) and count < 4:
        bot.send_message(user_id, formatMsg(locations[count]))
        count += 1
    
    mongoDBService.update_user_credits(user_id, 1)
    user.remaining_credits += 1
    user_data[message.chat.id] = user

    markup = types.ReplyKeyboardMarkup(row_width=1)
    itembtn1 = types.KeyboardButton('Show me good food around me!')
    itembtn2 = types.KeyboardButton('Recommend a makan spot!')
    markup.add(itembtn1, itembtn2)
    bot.send_message(user_id, "What would you like to do next?", reply_markup=markup)

    if not is_result_from_db:
        mongoDBService.save_locations(locations)
    
    return

def find_urls(text):
    pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    return len(re.findall(pattern, text)) > 0

def contains_google_maps_url(text):
    # Regular expression pattern to match Google Maps URLs
    pattern = r'https://(goo\.gl/maps/|maps\.app\.goo\.gl/)[a-zA-Z0-9?=_&]+'
    return re.search(pattern, text) is not None

def compute_credits(chat_id):
    user = user_data.get(chat_id) or mongoDBService.get_user(chat_id)
    if user.contributions <= 3:
        return 5
    else:
        return random.randint(1, 8)

@bot.message_handler(func=lambda message: contains_google_maps_url(message.text) or find_urls(message.text))
def handle_provided_url(message):
    
    chat_id = message.chat.id
    bot.send_chat_action(chat_id, 'typing')

    def handleIncorrectURL():
            bot.send_message(chat_id, 'Oops, there was an issue with the URL you shared, please double check your URL')
    
    google_maps_url_present = contains_google_maps_url(message.text)
    if not google_maps_url_present:
        bot.send_message(chat_id, "Uhoh, invalid URL sent, please check and send a valid URL in the format specified above")
        return

    url_format = mapsPreviewService.distinguish_google_maps_url_format(message.text)
    location_details = None

    try:
        if url_format == 'Long Format':
            location_details = mapsPreviewService.get_google_maps_details_for_long_format(message.text)
        elif url_format == 'Short Format':
            location_details = mapsPreviewService.get_google_maps_details_for_short_format(message.text)
        else:
            handleIncorrectURL()
            return

        if not (location_details.get('name') or location_details.get('address')):
            handleIncorrectURL()
            return

        #make API call to Google Maps to get place details that could not be found from website preview
        get_rating_flag = False if location_details.get('rating') else True
        hydrated_location = google_maps_service.fetch_place_details(location_details.get("name"), location_details.get("address"), get_rating_flag)
        if hydrated_location:
            hydrated_location.google_maps_link = message.text
            hydrated_location.thumbnail = location_details.get('thumbnail')
            if not get_rating_flag:
                hydrated_location.rating = location_details.get('rating')
        
        #save location recommended by user to DB
        saved_to_db = mongoDBService.save_location(hydrated_location)
        if saved_to_db:
            print(f'new location saved to db successfully: {hydrated_location.name} {hydrated_location.address}')

        #update user's credits and contributions on DB
        credits_to_be_added = compute_credits(chat_id)
        mongoDBService.update_user_credits(chat_id, credits_to_be_added, False)
        mongoDBService.update_user_contributions(chat_id, 1)

        markup = types.ReplyKeyboardMarkup(row_width=1)
        itembtn1 = types.KeyboardButton('Show me good food around me!')
        itembtn2 = types.KeyboardButton('Recommend a makan spot!')
        markup.add(itembtn1, itembtn2)
        bot.send_message(message.chat.id, f"Congratulations! You've been given **{credits_to_be_added} credits** 🎉 Thank you for your recommendation! Other users like yourself will benefit from this greatly 😊", reply_markup=markup)
        bot.send_message(message.chat.id, "What would you like to do next?", reply_markup=markup)

    except Exception as e:
        print(f'Error while processing user-provided URL: {e}')



# @server.route('/' + API_KEY, methods=['POST'])
# def getMessage():
#     bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
#     return "!", 200

# @server.route("/")
# def webhook():
#     bot.remove_webhook()
#     bot.set_webhook(url="https://sg-makan-bot.herokuapp.com/"+API_KEY)
#     return "!", 200

# if __name__ == "__main__":
#     server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))

#code for local testing
bot.remove_webhook()
bot.polling()