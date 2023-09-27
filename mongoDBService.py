import pymongo
from datetime import datetime
import os
import logging
from dotenv import load_dotenv
load_dotenv()

MONGO_PW = os.environ.get("MONGO_PW")
MONGO_USER = os.environ.get("MONGO_USERNAME")
MONGO_URL = os.environ.get("MONGO_URL")

logging.basicConfig(level=logging.DEBUG)

# MongoDB connection string (replace with your actual connection string)
MONGODB_URI = f"mongodb+srv://{MONGO_USER}:{MONGO_PW}@{MONGO_URL}/?retryWrites=true&w=majority"
if MONGO_PW and MONGO_URL and MONGO_USER:
    logging.info('env variables obtained successfully')
else:
    logging.error('error obtaining env one or more variables')

# Create a MongoDB client
client = pymongo.MongoClient(MONGODB_URI)

# Get a reference to the database and locations collection
db = client["sg-makan-bot"]
locations_collection = db["locations"]
users_collection = db["users"]

# User model and functions

class User:
    def __init__(self, name, chat_id, last_used=datetime.today(), contributions=0, remaining_credits=5):
        self.name = name
        self.chat_id = chat_id
        self.last_used = last_used
        self.contributions = contributions
        self.remaining_credits = remaining_credits

def create_new_user(user):
    user_data = {
        "name": user.name,
        "chat_id": user.chat_id,
        "last_used": user.last_used,
        "contributions": user.contributions,
        "remaining_credits": user.remaining_credits
    }
    users_collection.insert_one(user_data)

def update_user_last_used_date(chat_id):
    try:
        # Update the "last_used" field for the user with the given chat_id
        result = users_collection.update_one(
            {"chat_id": chat_id},
            {'$set': {'last_used': datetime.today()}}
        )
        
        if result.modified_count > 0:
            logging.info(f'Successfully updated last used date for user with chat_id: {chat_id}')
        else:
            logging.warn(f'No user found with chat_id: {chat_id}')
    except pymongo.errors.PyMongoError as e:
        logging.error(f'An error occurred while updating last used date for user with chat_id {chat_id}: {e}')
        
    return

def update_user_credits(chat_id, amount, decrement=True):
    try:
        # Determine the increment or decrement amount based on the flag
        update_amount = -amount if decrement else amount
        
        # Update the user's remaining credits using the $inc operator
        result = users_collection.update_one(
            {"chat_id": chat_id},
            {'$inc': {'remaining_credits': update_amount}}
        )
        
        if result.modified_count > 0:
            logging.info(f'Successfully updated remaining credits: {chat_id}')
        else:
            logging.warn(f'No user found with chat_id: {chat_id}')
    except pymongo.errors.PyMongoError as e:
        logging.error(f'An error occurred while updating remaining credits for user with chat_id {chat_id}: {e}')
        
    return

def update_user_contributions(chat_id, amount, increment=True):
    try:
        # Determine the increment or decrement amount based on the flag
        update_amount = amount if increment else -amount
        
        # Update the user's remaining credits using the $inc operator
        result = users_collection.update_one(
            {"chat_id": chat_id},
            {'$inc': {'contributions': update_amount}}
        )
        
        if result.modified_count > 0:
            logging.info(f'Successfully updated user contributions: {chat_id}')
        else:
            logging.warn(f'No user found with chat_id: {chat_id}')
    except pymongo.errors.PyMongoError as e:
        logging.error(f'An error occurred while updating user contributions for user with chat_id {chat_id}: {e}')
        
    return

def get_user(chat_id):
    user = None
    try:
        result = users_collection.find_one({"chat_id": chat_id})
        if result:
            user = User(
            name=result['name'],
            chat_id=result['chat_id'],
            last_used=result['last_used'],
            contributions=result['contributions'],
            remaining_credits=result['remaining_credits']
        )
            update_user_last_used_date(chat_id)

    except pymongo.errors.PyMongoError as e:
        logging.error(f'An error occurred while getting user with chat_id: {chat_id}: {e}')
    
    return user



# Location model and functions

class Location:
    def __init__(self, name, address, google_maps_link, thumbnail, location_type, rating, longitude, latitude, community_recommendations=0):
        self.name = name
        self.address = address
        self.google_maps_link = google_maps_link
        self.thumbnail = thumbnail
        self.location_type = location_type
        self.rating = rating
        self.longitude = longitude
        self.latitude = latitude
        self.community_recommendations = community_recommendations

def save_location(location):
    location_data = {
        "name": location.name,
        "address": location.address,
        "google_maps_link": location.google_maps_link,
        "thumbnail": location.thumbnail,
        "location_type": location.location_type,
        "rating": location.rating,
        'location': {
            'type': "Point",
            'coordinates': [location.longitude, location.latitude]
        },
        "community_recommendations": location.community_recommendations
    }
    try:
        # Search for an existing document with the same name, longitude, and latitude
        existing_location = locations_collection.find_one({
            "name": location.name,
            "location.coordinates": [location.longitude, location.latitude]
        })
        if not existing_location:
            return locations_collection.insert_one(location_data)
        else:
            return existing_location
    except pymongo.errors.PyMongoError as e:
        logging.error(f'An error occurred while saving single location: longitude {location.longitude}: latitude {location.latitude} - Error: {e}')
        return None


def save_user_recommended_location(location):
    location_data = {
        "name": location.name,
        "address": location.address,
        "google_maps_link": location.google_maps_link,
        "thumbnail": location.thumbnail,
        "location_type": location.location_type,
        "rating": location.rating,
        'location': {
            'type': "Point",
            'coordinates': [location.longitude, location.latitude]
        },
        "community_recommendations": location.community_recommendations
    }

    try: 
        # Search for an existing document with the same name, longitude, and latitude
        existing_location = locations_collection.find_one({
            "name": location.name,
            "location.coordinates": [location.longitude, location.latitude]
        })

        if existing_location:
            # If found, increment the community_recommendations field by 1
            locations_collection.update_one(
                {
                    "name": location.name,
                    "location.coordinates": [location.longitude, location.latitude]
                },
                {
                    "$inc": {"community_recommendations": 1},
                }
            )
        else:
            # If not found, insert the new document
            location_data["community_recommendations"] = 1
            locations_collection.insert_one(location_data)
    except pymongo.errors.PyMongoError as e:
        logging.error(f'An error occurred while saving user recommended location for: longitude {location.longitude}: latitude {location.latitude} - Error: {e}')

def save_locations(locations):
    for location in locations:
        location_data = {
            "name": location.name,
            "address": location.address,
            "google_maps_link": location.google_maps_link,
            "thumbnail": location.thumbnail,
            "location_type": location.location_type,
            "rating": location.rating,
            'location': {
                'type': "Point",
                'coordinates': [location.longitude, location.latitude]
            },
            "community_recommendations": location.community_recommendations
        }
        
        try:
            existing_location = locations_collection.find_one({
            "name": location.name,
            "location.coordinates": [location.longitude, location.latitude]
            })
            if not existing_location:
                locations_collection.insert_one(location_data)
        except pymongo.errors.PyMongoError as e:
            logging.error(f"Error while bulk inserting locations: {e}")

def map_to_location_object(detailed_place_object):
        coordinates = detailed_place_object.get('location', {}).get('coordinates', [])
        longitude = None
        latitude = None
        if len(coordinates) == 2:
            longitude = coordinates[0]
            latitude = coordinates[1]

        return Location(
            name=detailed_place_object.get('name'),
            address=detailed_place_object.get('address'),
            google_maps_link=detailed_place_object.get('google_maps_link'),
            thumbnail=detailed_place_object.get('thumbnail'),
            location_type=detailed_place_object.get('location_type', None),
            rating=detailed_place_object.get('rating'),
            longitude=longitude,
            latitude=latitude
        )

def fetch_nearby_locations_sorted_by_reviews(longitude, latitude):
    try:
        # Coordinates of the center point (latitude, longitude)
        center_point = {
            "type": "Point",
            "coordinates": [longitude, latitude]  # Replace with your center coordinates
        }

        # Find locations within a 1 km radius from the center point and sort by ratings
        nearby_locations = locations_collection.aggregate([
            {
                "$geoNear": {
                    "near": center_point,
                    "distanceField": "distance",
                    "maxDistance": 1000,  # 1 km in meters,
                    "spherical": True
                }
            },
            {
                "$sort": {
                    "rating": -1  # Sort by ratings in descending order
                }
            }
        ])

        output = []

        for location in nearby_locations:
            output.append(map_to_location_object(location))

        return output
    except pymongo.errors.PyMongoError as e:
        logging.error(f'An error occurred while fetching nearby locations sorted by reviews for: longitude {longitude}: latitude {latitude} - Error: {e}')
        return []
