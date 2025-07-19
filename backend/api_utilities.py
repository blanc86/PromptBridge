import os
import requests

# === City Extraction Function ===
def extract_city_name(prompt):
    known_cities = [
        "Delhi", "Mumbai", "Bengaluru", "Chennai", "Kolkata", "Hyderabad", "Pune",
        "Ahmedabad", "Jaipur", "Lucknow", "Kanpur", "Nagpur", "Indore", "Bhopal",
        "Patna", "Vadodara", "Ludhiana", "Agra", "Nashik", "Faridabad", "Meerut",
        "Rajkot", "Varanasi", "Srinagar", "Amritsar", "Prayagraj", "Ranchi",
        "Howrah", "Gwalior", "Jodhpur", "Coimbatore", "Vijayawada", "Jabalpur",
        "Madurai", "Raipur", "Kota", "Guwahati", "Chandigarh", "Solapur", "Hubli",
        "Mysore", "Tiruchirappalli", "Bareilly", "Moradabad", "Thiruvananthapuram",
        "Noida", "Ghaziabad", "Visakhapatnam", "Davangere", "Mangalore", "Salem"
    ]
    for city in known_cities:
        if city.lower() in prompt.lower():
            return city
    return None


class APIUtilities:
    def __init__(self):
        self.gnews_key = os.getenv("GNEWS_KEY")
        self.weather_key = os.getenv("OPENWEATHERMAP_KEY")
        self.timezonedb_key = os.getenv("TIMEZONEDB_API_KEY")
        self.fyers_token = os.getenv("FYERS_API_KEY")
        self.kite_token = os.getenv("ZERODHA_KITE_API_KEY")
        self.market_prices_api_key = os.getenv("MARKET_PRICES_API_KEY") 

    # === Existing Methods ===

    def get_news(self, prompt="India", lang="en", max_results=5):
        if not self.gnews_key:
            return ["❌ GNews API key not found."]
        
        query = extract_city_name(prompt) or prompt
        url = f"https://gnews.io/api/v4/search?q={query}&lang={lang}&max={max_results}&apikey={self.gnews_key}"
        try:
            response = requests.get(url, timeout=10)
            data = response.json()
            return [f"{a['title']} ({a['source']['name']})" for a in data.get("articles", [])] or ["No news found."]
        except requests.exceptions.RequestException as e:
            return [f"🌐 GNews API Error: {e}"]

    def get_weather(self, prompt="Delhi"):
        if not self.weather_key:
            return {"error": "❌ OpenWeatherMap API key not found."}
        
        city = extract_city_name(prompt) or "Delhi"
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={self.weather_key}&units=metric"
        try:
            return requests.get(url, timeout=10).json()
        except requests.exceptions.RequestException as e:
            return {"error": f"🌦️ Weather API Error: {e}"}

    def get_time_by_timezone(self, prompt="India"):
        if not self.timezonedb_key:
            return {"error": "❌ TimeZoneDB API key not found."}
        
        city = extract_city_name(prompt)
        city_timezone_map = {
            "Delhi": "Asia/Kolkata", "Mumbai": "Asia/Kolkata", "Bengaluru": "Asia/Kolkata",
            "Kolkata": "Asia/Kolkata", "Chennai": "Asia/Kolkata", "Hyderabad": "Asia/Kolkata",
            "Ahmedabad": "Asia/Kolkata", "Lucknow": "Asia/Kolkata", "Jaipur": "Asia/Kolkata",
            "Srinagar": "Asia/Kolkata", "Guwahati": "Asia/Kolkata"
        }
        timezone = city_timezone_map.get(city, "Asia/Kolkata")
        url = f"http://api.timezonedb.com/v2.1/get-time-zone?key={self.timezonedb_key}&format=json&by=zone&zone={timezone}"
        try:
            return requests.get(url, timeout=10).json()
        except requests.exceptions.RequestException as e:
            return {"error": f"🕒 Time API Error: {e}"}

    # === New Market Prices by State Method ===
    def get_market_prices_by_state(self, state):
        if not self.market_prices_api_key:
            return {"error": "❌ Market Prices API key not found."}

        # You can check if the state is in a list of valid states if needed
        valid_states = [
            "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh",
            "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka",
            "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya", "Mizoram",
            "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana",
            "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal"
        ]
        
        if state not in valid_states:
            return {"error": f"❌ Invalid state: {state}. Please provide a valid state."}
        
        url = f"https://api.example.com/resource/35985678-0d79-46b4-9ed6-6f13308a1d24?api-key={self.market_prices_api_key}&filters[State.keyword]={state}&format=json"
        
        try:
            response = requests.get(url, timeout=10)
            data = response.json()
            if data:
                return {state: data}
            else:
                return {state: "No data found."}
        except requests.exceptions.RequestException as e:
            return {state: f"API Error: {e}"}


# === For use in main.py ===
api_client = APIUtilities()

def fetch_news(prompt="India"):
    return api_client.get_news(prompt)

def fetch_weather(prompt="Delhi"):
    return api_client.get_weather(prompt)

def fetch_quote():
    return api_client.get_quote()

def fetch_fun_fact():
    return api_client.get_fun_fact()

def fetch_definition(word="technology"):
    return api_client.get_word_definition(word)

def fetch_time(prompt="India"):
    return api_client.get_time_by_timezone(prompt)

def fetch_market_prices(state="Karnataka"):
    return api_client.get_market_prices_by_state(state)
