import requests
import mongoDBService

class GoogleMapsAPIService:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json"
        self.places_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        self.place_details_url = "https://maps.googleapis.com/maps/api/place/details/json"

    def fetch_place_details(self, name, address, get_rating_flag):
        try:
            # Construct the query parameters
            params = {
                "input": f"{name} {address}",
                "inputtype": "textquery",
                "fields": "name,formatted_address,geometry,types,business_status",
                "key": self.api_key
            }

            if get_rating_flag:
                params["fields"] += ',rating'

            # Make the API request
            response = requests.get(self.base_url, params=params)
            response_data = response.json()

            print(response_data)

            if response_data.get("status") == "OK":
                candidates = response_data.get("candidates", [])
                if candidates:
                    candidate = candidates[0]
                    longitude = candidate.get('geometry', {}).get('location', {}).get('lng')
                    latitude = candidate.get('geometry', {}).get('location', {}).get('lat')
                    location = mongoDBService.Location(
                        name=candidate.get('name'),
                        address=candidate.get('formatted_address'),
                        google_maps_link=None,
                        thumbnail=None,
                        location_type="restaurant" if (candidate.get('types') and ("food" in candidate.get('types') or "restaurant" in candidate.get('types'))) else None,
                        rating=candidate.get('rating', None),
                        longitude=longitude,
                        latitude=latitude
                    )
                    return location
            
            return None
        except requests.exceptions.RequestException as e:
            print("Error while fetching place details:", e)
            return None

    
    def fetch_place_details_by_id(self, place_id):
        try: 
            # Construct the query parameters for Place Details API
            params = {
                "place_id": place_id,
                "fields": "name,formatted_address,geometry,type,business_status,url,rating",
                "key": self.api_key
            }

            # Make the API request
            response = requests.get(self.place_details_url, params=params)
            response_data = response.json()

            if response_data.get("status") == "OK":
                return response_data.get('result')
            
            return None
        except requests.exceptions.RequestException as e:
            print("Error while fetching place details by place_id:", e)
            return None

    def fetch_nearby_food_places(self, longitude, latitude):
        try:
            # Construct the query parameters for nearby search
            params = {
                "location": f"{latitude},{longitude}",
                "radius": 1000,  # 1 km radius
                "type": "restaurant",  # Filter by restaurant type
                "key": self.api_key
            }

            response = requests.get(self.places_url, params=params)
            response_data = response.json()

            if response_data.get("status") == "OK":
                places = response_data.get("results", [])

                # Fetch detailed information for each place using Place Details API
                detailed_places = []
                counter = 0
                for place in places:
                    place_id = place.get("place_id")
                    detailed_place = self.fetch_place_details_by_id(place_id)
                    if detailed_place:
                        new_location = map_to_location_object(detailed_place)
                        detailed_places.append(new_location)
                        counter += 1
                        if counter >= 10:  # Break the loop after processing 10 places
                            break

                return detailed_places
            
            return []
        except requests.exceptions.RequestException as e:
            print("Error while fetching nearby food places:", e)
            return None


def map_to_location_object(detailed_place_object):
        return mongoDBService.Location(
            name=detailed_place_object.get('name'),
            address=detailed_place_object.get('formatted_address'),
            google_maps_link=detailed_place_object.get('url'),
            thumbnail=None,
            location_type="restaurant" if (detailed_place_object.get('types') and ("food" in detailed_place_object.get('types') or "restaurant" in detailed_place_object.get('types'))) else None,
            rating=detailed_place_object.get('rating', 0),
            longitude=detailed_place_object["geometry"]["location"]["lng"],
            latitude=detailed_place_object["geometry"]["location"]["lat"]
        )
