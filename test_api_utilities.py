import os
from dotenv import load_dotenv
from pprint import pprint

# Load environment variables
load_dotenv()

# Import the helper functions or the client directly
from backend.api_utilities import (
    fetch_news,
    fetch_weather,
    fetch_time,
    fetch_quote,
    fetch_fun_fact,
    fetch_definition,
)

def test_all():
    print("\n📰 Top News (default):")
    pprint(fetch_news())

    print("\n🌦️ Weather in Delhi:")
    pprint(fetch_weather("Davangere"))

    print("\n🕒 Current Time in Asia/Kolkata:")
    time_data = fetch_time("Asia/Kolkata")
    if time_data.get("status") == "OK":
        print(f"🗓️ Formatted Time: {time_data.get('formatted')}")
        print(f"📍 Zone: {time_data.get('zoneName')} | Country: {time_data.get('countryName')}")
    else:
        print(f"❌ Failed to get time: {time_data.get('message', 'Unknown error')}")

    print("\n💬 Random Quote:")
    print(fetch_quote())

    print("\n🎉 Fun Fact:")
    print(fetch_fun_fact())

    print("\n📚 Definition of 'intelligence':")
    pprint(fetch_definition("intelligence"))

if __name__ == "__main__":
    test_all()


#Final Copy
