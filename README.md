# Food Recommendation Bot

Telegram bot which helps users to find good food spots near them. If you're in Singapore and want to explore yummy local food, this bot will assist you in discovering new places to dine!

## Overview

The Food Recommendation bot leverages the power of the Google Maps API to find the best restaurants near your location. It also incorporates user-generated recommendations and ratings to provide a personalized and community-driven experience.

## Features

- **Discover Food Around You:** Send your location, and the bot will recommend the top-rated restaurants nearby.
- **Contribute Your Recommendations:** You can also take in your recommendations for good dining spots which may be shared with other users and earn credits for more recommendations.
- **Community-driven Experience:** Utilizes both Google Maps and community recommendations for a comprehensive guide to local dining.
- **Visual Ratings:** Get visual star ratings for a quick understanding of how good the food is.

## Requirements

- A Telegram account
- Access to Google Maps
- Python 3
- A MongoDB database for storing user data and locations

## How It Works

1. **Starting the Bot:** Use the '/start' command to initiate the bot. You'll be greeted with options to either show food around you or recommend a spot.
2. **Finding Food:** Click 'Show me good food around me!' and send your location. The bot will then provide details of the best places nearby.
3. **Recommending a Spot:** Click 'Recommend a makan spot!' and follow the instructions to share your favorite places.
4. **Credits System:** Users have credits that are used for obtaining recommendations. More credits can be earned by contributing recommendations.
5. **Database Integration:** The bot uses MongoDB to store user information and community recommendations, enhancing its capabilities over time.

## Getting Started

Clone the repository and install the required dependencies. Make sure to set up your environment variables for the Telegram Bot API key and the Google Maps API key. Here's a basic setup guide:

1. Clone the repository
2. Install dependencies with `pip install -r requirements.txt`
3. Set up environment variables for `TELEGRAM_BOT_API_KEY`, `GOOGLE_MAPS_API_KEY` and `MONDODB_URL`
4. Run the bot with `python telegram-bot.py`

Enjoy discovering new places to eat and share your favorite spots with others!

## Contributing

Feel free to open issues or submit pull requests if you have suggestions or improvements. Your contributions are welcome!

## License

[MIT License](LICENSE.md) - see the file for details

---

Built with 💙 and 🍽 by Salomone
