import json
import requests
from datetime import datetime, timedelta
import pytz  # pip install pytz

# Function to fetch Sodexo JSON data
def fetch_sodexo_data():
    sodexo_url = "https://www.sodexo.fi/ruokalistat/output/weekly_json/160"    #Turun AMK-Lemminkäisenkatu
    response = requests.get(sodexo_url)

    if response.status_code != 200:
        print(f"Error fetching data: {response.status_code}")
        return None

    sodexo_json = response.json()
    return transform_sodexo_json(sodexo_json)

# Function to convert day name to ISO 8601 date format
def convert_day_to_iso8601(day_name):
    days_of_week = ['Maanantai', 'Tiistai', 'Keskiviikko', 'Torstai', 'Perjantai', 'Lauantai', 'Sunnuntai']
    today = datetime.now()
    current_day_index = today.weekday()  # Monday is 0 and Sunday is 6
    
    # Create a mapping of day names to their respective date
    day_index = days_of_week.index(day_name)
    
    # Calculate the date offset from today
    date_offset = day_index - current_day_index
    target_date = today + timedelta(days=date_offset)

    # Set the timezone to UTC
    timezone = pytz.timezone('UTC')
    target_date_with_time = timezone.localize(target_date)  # Localize to UTC
    
    # Convert to ISO 8601 format
    return target_date_with_time.isoformat()  # Example: "2024-10-07T00:00:00+00:00"

# Function to transform the data
def transform_sodexo_json(sodexo_data):
    restaurant_name = sodexo_data['meta']['ref_title']
    
    transformed_data = {
        "RestaurantName": restaurant_name,
        "MenusForDays": []
    }

    # Process each meal date
    for meal_date in sodexo_data['mealdates']:

        day_name = meal_date['date']  # Assuming this is the day name like "Maanantai"
        iso_date = convert_day_to_iso8601(day_name)  # Convert the day name directly

        menu_entry = {
            "Date": iso_date,  
            "SetMenus": []
        }
        
        # Process each course
        for course in meal_date['courses'].values():

            price = course.get('price', 'N/A')
            title = course.get('title_fi', 'No title')

    
            menu_entry["SetMenus"].append({
                "Name": "Lounas",
                "Price": price,
                "Components": [title]
            })

        transformed_data["MenusForDays"].append(menu_entry)

    return transformed_data

# This will run script
if __name__ == "__main__":
    new_json = fetch_sodexo_data()
    print(json.dumps(new_json, ensure_ascii=False, indent=2))
