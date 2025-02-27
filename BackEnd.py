from flask import Flask, render_template, url_for, redirect
import requests #pip install requests
from datetime import datetime, timedelta
from dateutil import parser as date_parser
from Lemminkaisenkatu import fetch_sodexo_data

app = Flask(__name__)

#1.2.2025? URL CHANGE FROM /MODULES/JSON/JSON TO MENUAPI/FEED/JSON

# JSON URLs for each restaurant
JSON_URLS = [
    "https://www.unica.fi/menuapi/feed/json?costNumber=1920&language=fi",          #Assarin ullakko
    "https://www.unica.fi/menuapi/feed/json?costNumber=1970&language=fi",          #Macciavelli
    "https://www.unica.fi/menuapi/feed/json?costNumber=1995&language=fi",          #Galilei
    "https://www.unica.fi/menuapi/feed/json?costNumber=1980&language=fi",          #Dental
    "https://www.unica.fi/menuapi/feed/json?costNumber=1985&language=fi",          #Delica
    "https://www.unica.fi/menuapi/feed/json?costNumber=2000&language=fi",          #Linus
    "https://www.unica.fi/menuapi/feed/json?costNumber=1900&language=fi",          #Kisälli
    
]

# Takes the JSON data and checks for errors.
def fetch_menu_data(json_url):
    try:
        response = requests.get(json_url)
        response.raise_for_status()  # Raise an HTTPError for bad responses
        data = response.json()
        if data is None or not data["MenusForDays"]:
            return None
    
        return data
    
    except requests.RequestException as e:
        print(f"Error {json_url}, cause {e}")
        return None
    except ValueError:
        print(f"ValueError {json_url}")
        return None

# Function to extract menus for a specific day
def get_menus_for_day(menu_data, date_today):
    if menu_data is None:
        return []
    
    for day_menu in menu_data.get("MenusForDays", []):
        # Check if the current date matches the "Date" in the JSON data
        day_date = date_parser.parse(day_menu['Date']).date()
        if day_date == date_today:
            return day_menu.get('SetMenus', [])
    return []  # Return an empty list if no menus found for the current day

# Function to get the current day in Finnish
def get_current_day_in_finnish():
    days_of_week = ['Maanantai', 'Tiistai', 'Keskiviikko', 'Torstai', 'Perjantai', 'Lauantai', 'Sunnuntai']
    current_day_index = datetime.now().weekday()
    return days_of_week[current_day_index] 


# Home route: Redirects to the current day's menu
@app.route('/')
def home():
    current_day_finnish = get_current_day_in_finnish()
    return redirect(url_for('show_day', day_name=current_day_finnish))

# Route to show the menu for a specific day
@app.route('/day/<day_name>')
def show_day(day_name):
    # Get today's date
    today_date = datetime.now().date()

    # Get the index of the day name (e.g., Maanantai = 0, Tiistai = 1, etc.)
    days_of_week = ['Maanantai', 'Tiistai', 'Keskiviikko', 'Torstai', 'Perjantai', 'Lauantai', 'Sunnuntai']
    current_day_index = days_of_week.index(get_current_day_in_finnish())
    requested_day_index = days_of_week.index(day_name)

    # Calculate the date offset based on the requested day
    date_offset = requested_day_index - current_day_index
    requested_date = today_date + timedelta(days=date_offset)


    # Get current date for display in the format DD.MM.YYYY
    current_date = requested_date.strftime("%d.%m.%Y")

    all_restaurant_content = []

    # Fetch menus for the requested date
    for json_url in JSON_URLS:
        restaurant_data = fetch_menu_data(json_url)

        if restaurant_data is None:
            print(f"No data returned for {json_url}, skipping")
            continue

        restaurant_name = restaurant_data.get('RestaurantName', 'Unknown Restaurant')
        day_menus = get_menus_for_day(restaurant_data, requested_date)

        
        #Gets the opening_hours and formats it {Opening_time}-{Closing_time}
        lunch_time_raw = restaurant_data.get('MenusForDays')[0].get('LunchTime', None)

        if lunch_time_raw:
            lunch_time_hyphen_normalized = lunch_time_raw.replace("–", "-")
            time_parts = lunch_time_hyphen_normalized.strip().split('-')
            start_time = time_parts[0].strip()
            end_time = time_parts[1]
            clean_lunch_time = f"{start_time}-{end_time}"
        else:
            clean_lunch_time = "Tarkista aukioloaika"

        #Append the restaurant to the list if there is a menu. Otherwise don't show it on the HTML
        if day_menus: 
            all_restaurant_content.append({
                'restaurant_name': restaurant_name,
                'day_menus': day_menus,
                'Opening_hours': clean_lunch_time,
         })

    sodexo_data = fetch_sodexo_data()  # Call the function to fetch Sodexo data
    if sodexo_data:
        sodexo_menus = get_menus_for_day(sodexo_data, requested_date)  # Extract the menus for the requested date

        if sodexo_menus:
            all_restaurant_content.append({
                'restaurant_name': sodexo_data.get('RestaurantName'),
                'day_menus': sodexo_menus,
                'Opening_hours': "10:30-13:00"   #HARD-CODED Opening-hours, because json-format doesnt include it
            })


    # Set up navigation for previous and next day
    prev_day_index = (requested_day_index - 1) % len(days_of_week)
    next_day_index = (requested_day_index + 1) % len(days_of_week)

    prev_day = days_of_week[prev_day_index]
    next_day = days_of_week[next_day_index]

    return render_template('day.html', 
                           all_restaurant_content=all_restaurant_content, 
                           current_date=current_date, 
                           day_name=day_name, 
                           prev_day=prev_day, 
                           next_day=next_day, 
                           datetime=str(datetime.now()))


# Starts the Flask application
if __name__ == '__main__':
    app.run(debug=True)

