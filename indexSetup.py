import pymongo
import os
from dotenv import load_dotenv
load_dotenv()


MONGO_PW = os.getenv("MONGO_PW")
MONGO_USER = os.getenv("MONGO_USERNAME")
MONGO_URL = os.getenv("MONGO_URL")

# MongoDB connection string (replace with your actual connection string)
MONGODB_URI = f"mongodb+srv://{MONGO_USER}:{MONGO_PW}@{MONGO_URL}/?retryWrites=true&w=majority"
if MONGO_PW and MONGO_URL and MONGO_USER:
    print('env variables obtained successfully')
else:
    print('error obtaining env one or more variables')
    
# Define a validator to enforce required fields for USERS
required_fields_validator_for_users = {
    "chat_id": {"$exists": True},
    "name": {"$exists": True},
    "last_used": {"$exists": True},
    "contributions": {"$exists": True},
}

# Define a validator to enforce required fields for LOCATIONS
required_fields_validator_for_locations = {
    "name": {"$exists": True},
    "address": {"$exists": True},
    "rating": {"$exists": True},
    "location.type": {"$eq": "Point"},
    "location.coordinates": {"$exists": True},
}

def setup_indexes():
    # Create a MongoDB client
    client = pymongo.MongoClient(MONGODB_URI)

    # Get a reference to the database and locations collection
    db = client["sg-makan-bot"]
    locations_collection = db["locations"]
    locations_collection.drop_index("unique_name_index")
    users_collection = db["users"]

    # Create indexes with JSON schema validation
    users_collection.create_indexes([
        pymongo.IndexModel(
            [("chat_id", pymongo.ASCENDING)],
            name="required_fields_index",
            partialFilterExpression=required_fields_validator_for_users,
            unique=True
        )
    ])

    locations_collection.create_indexes([
        pymongo.IndexModel(
            [("name", pymongo.ASCENDING)],
            name="unique_name_index",
            partialFilterExpression=required_fields_validator_for_locations,
            unique=True
        ),
        pymongo.IndexModel(
            [("location", "2dsphere")],  # Create a 2dsphere index on the location field
            name="geospatial_index"
        )
    ])

if __name__ == "__main__":
    # Run the index setup when the script is executed directly
    setup_indexes()
    print("Index setup completed.")
