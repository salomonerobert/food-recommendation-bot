import requests
from bs4 import BeautifulSoup
import logging

logging.basicConfig(level=logging.DEBUG)

def distinguish_google_maps_url_format(url):
    if "goo.gl/maps" in url:
        return "Short Format"
    elif "maps.app.goo.gl" in url:
        return "Long Format"
    else:
        return "Unknown Format"

def get_google_maps_details_for_long_format(url):
    try:
        logging.info(f'Getting google maps details for Long Format URL: {url}')
        response = requests.get(url)
        response.raise_for_status()  # Check for any HTTP errors

        soup = BeautifulSoup(response.text, 'html.parser')

        # Extracting name, rating and type
        name_element = soup.find("meta", itemprop="name")
        name = name_element["content"] if name_element else "N/A"

        split_name = name.split('·')
        final_name = split_name[0]
        rating = split_name[1] if split_name[1] else 'N/A'
        cleaned_rating = rating.split('★')[0] if rating != 'N/A' else rating
        type_of_eatery = split_name[2] if split_name[2] else 'N/A'
        # Extracting address
        address_element = soup.find("meta", itemprop="description")
        address = address_element["content"] if address_element else "N/A"

        #Extract thumbnail url
        thumbnail_url = soup.find("meta", itemprop="image")
        thumbnail = thumbnail_url['content'] if thumbnail_url else 'N/A'

        return {
            "name": final_name,
            "address": address,
            "rating": cleaned_rating,
            "type": type_of_eatery,
            "thumbnail": thumbnail
        }

    except requests.exceptions.RequestException as e:
        logging.error("Error:", e)
        return None

def get_google_maps_details_for_short_format(url):
    try:
        logging.info(f'Getting google maps details for Short Format URL: {url}')
        response = requests.get(url)
        response.raise_for_status()  # Check for any HTTP errors

        soup = BeautifulSoup(response.text, 'html.parser')

        # Extracting name, rating and type
        name_and_address_element = soup.find("meta", itemprop="name")
        name_and_address = name_and_address_element["content"] if name_and_address_element else "N/A"

        split_array = name_and_address.split('·')
        final_name = split_array[0].strip()
        address = split_array[1].strip()

        # Extracting rating and type
        rating_and_type_element = soup.find("meta", itemprop="description")
        rating_and_type = rating_and_type_element["content"] if rating_and_type_element else "N/A"

        split_rating_and_type = rating_and_type.split('·')
        rating = split_rating_and_type[0].strip()
        type = split_rating_and_type[1].strip()

        #Extract thumbnail url
        thumbnail_url = soup.find("meta", itemprop="image")
        thumbnail = thumbnail_url['content'] if thumbnail_url else 'N/A'

        return {
            "name": final_name,
            "address": address,
            "rating": None,
            "type": type,
            "thumbnail": thumbnail
        }

    except requests.exceptions.RequestException as e:
        logging.error("Error:", e)
        return None


    
