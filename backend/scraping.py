import requests
import json

# Replace with your actual API key
api_key = ''

# API endpoint URL for fetching the commodity price data
api_url = 'https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070'

# List of all states in India
states = [
    "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh", "Goa", 
    "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka", "Kerala", 
    "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya", "Mizoram", "Nagaland", 
    "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana", "Tripura", 
    "Uttar Pradesh", "Uttarakhand", "West Bengal", "Andaman and Nicobar Islands", 
    "Chandigarh", "Dadra and Nagar Haveli and Daman and Diu", "Lakshadweep", "Delhi"
]

for state in states:
    print(f"Searching for data in {state}...")
    
    # Define the parameters for the request
    params = {
        "api-key": api_key,
        "format": "json",  # Or you can set to xml/csv based on preference
        "filters[state.keyword]": state,
        "limit": 10  # You can adjust this to fetch more records
    }

    # Make the GET request
    response = requests.get(api_url, params=params)

    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()
        
        if data.get("records"):
            print(f"Data found for {state}:\n")
            for record in data["records"]:
                print(f"Market: {record.get('market')}")
                print(f"Commodity: {record.get('commodity')}")
                print(f"Variety: {record.get('variety')}")
                print(f"Grade: {record.get('grade')}")
                print(f"Arrival Date: {record.get('arrival_date')}")
                print(f"Min Price: ₹{record.get('min_price')}")
                print(f"Max Price: ₹{record.get('max_price')}")
                print(f"Modal Price: ₹{record.get('modal_price')}")
                print("-" * 50)
        else:
            print(f"No data found for {state}.")
    else:
        print(f"Failed to retrieve data for {state}, status code: {response.status_code}")
    
    print("\n" + "="*80 + "\n")
