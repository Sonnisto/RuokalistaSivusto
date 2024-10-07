from flask import Flask, render_template, url_for, redirect
import requests
from datetime import datetime, timedelta
from dateutil import parser as date_parser

app = Flask(__name__)

# JSON URLs for each restaurant
JSON_URLS = [
    "https://www.unica.fi/modules/json/json/Index?costNumber=1920&language=fi",
    "https://www.unica.fi/modules/json/json/Index?costNumber=1970&language=fi",
    "https://www.unica.fi/modules/json/json/Index?costNumber=1995&language=fi",
    "https://www.unica.fi/modules/json/json/Index?costNumber=1980&language=fi",
    "https://www.unica.fi/modules/json/json/Index?costNumber=1935&language=fi",
    "https://www.unica.fi/modules/json/json/Index?costNumber=1985&language=fi",
    "https://www.unica.fi/modules/json/json/Index?costNumber=2000&language=fi",
    "https://www.unica.fi/modules/json/json/Index?costNumber=1900&language=fi"
    
]

# Takes the JSON data and checks for errors.
def fetch_menu_data(json_url):
    response = requests.get(json_url)
    response.raise_for_status()  # Will raise an HTTPError for bad responses
    return response.json()

# Function to extract menus for a specific day
def get_menus_for_day(menu_data, date_today):
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
        restaurant_name = restaurant_data.get('RestaurantName', 'Unknown Restaurant')
        day_menus = get_menus_for_day(restaurant_data, requested_date)

        all_restaurant_content.append({
            'restaurant_name': restaurant_name,
            'day_menus': day_menus,
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
