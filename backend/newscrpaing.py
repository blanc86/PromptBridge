import requests

def get_variety_wise_data_all_states(api_key, limit=10, offset=0, output_format="json"):
    url = "https://api.data.gov.in/resource/35985678-0d79-46b4-9ed6-6f13308a1d24"
    
    params = {
        'api-key': api_key,
        'format': output_format,
        'limit': limit,
        'offset': offset
    }
    
    # List of all states to iterate through
    states = [
        "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh", "Goa", 
        "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka", "Kerala", 
        "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya", "Mizoram", "Nagaland", 
        "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana", "Tripura", 
        "Uttar Pradesh", "Uttarakhand", "West Bengal", "Andaman and Nicobar Islands", 
        "Chandigarh", "Dadra and Nagar Haveli and Daman and Diu", "Lakshadweep", "Delhi"
    ]
    
    all_data = []

    # Loop through each state and fetch data
    for state in states:
        print(f"Fetching data for {state}...")
        params['filters[State.keyword]'] = state
        
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('records'):
                print(f"Data found for {state}:")
                for record in data['records']:
                    all_data.append(record)
                    print(record)
            else:
                print(f"No data found for {state}")
        else:
            print(f"Failed to retrieve data for {state}, status code: {response.status_code}")
    
    return all_data

# Example usage
api_key = "579b464db66ec23bdd000001a4cb6c4e2dcd4da774853ef67960ceec"
limit = 10

all_state_data = get_variety_wise_data_all_states(api_key, limit=limit)

if all_state_data:
    print("\nFetched Data from all states:")
    for record in all_state_data:
        print(record)
else:
    print("No data found across all states.")
