from flask import Flask, render_template, url_for, redirect
import requests
from datetime import datetime
from dateutil import parser as date_parser
from Lemminkaisenkatu import fetch_sodexo_data
from apscheduler.schedulers.background import BackgroundScheduler
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc, asc
import os


app = Flask(__name__)

#Cron job to update the database every monday at 10 AM
def scheduled_update():
    with app.app_context():
        update_database()

scheduler = BackgroundScheduler()

scheduler.add_job(scheduled_update, 'cron', day_of_week='mon', hour=10)
scheduler.start()

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///ravintolat.db")
db = SQLAlchemy(app)

class Restaurant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    opening_hours = db.Column(db.String(50), nullable=True)
    menu_days = db.relationship('MenuDay', backref='restaurant', lazy=True)

class MenuDay(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurant.id'), nullable=False)
    menus = db.relationship('Menu', backref='menu_day', lazy=True)

class Menu(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=True)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.String(20), nullable=True)
    menu_day_id = db.Column(db.Integer, db.ForeignKey('menu_day.id'), nullable=False)

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
        response.raise_for_status()
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
    
# Updates the database with the latest menu data
def update_database():
    for json_url in JSON_URLS:
        data = fetch_menu_data(json_url)
        if data is None:
            print(f"Ei dataa URL:sta {json_url}")
            continue
        save_restaurant_data_to_db(data)
        
    sodexo_data = fetch_sodexo_data()
    if not sodexo_data:
        print("Ei Sodexo dataa")
    else:
        for data in sodexo_data:
            save_restaurant_data_to_db(data)
        
        
# Saves the restaurant and menu data to the database        
def save_restaurant_data_to_db(data):
    restaurant_name = data.get('RestaurantName', 'Unknown Restaurant')
    lunch_time_raw = None
    if data.get("MenusForDays") and "LunchTime" in data["MenusForDays"][0]:
        lunch_time_raw = data["MenusForDays"][0].get("LunchTime", "Tarkista aukioloaika")

    # Restaurant
    restaurant = Restaurant.query.filter_by(name=restaurant_name).first()
    if not restaurant:
        restaurant = Restaurant(name=restaurant_name, opening_hours=lunch_time_raw)
        db.session.add(restaurant)
        db.session.commit()
        print(f"Lisätty ravintola: {restaurant.name} ({restaurant.opening_hours})")
    else:
        if lunch_time_raw:
            restaurant.opening_hours = lunch_time_raw
            print(f"Päivitetty aukioloaika: {restaurant.name} ({restaurant.opening_hours})")
    db.session.commit()

    # MenusForDays
    for day_menu in data.get("MenusForDays", []):
        day_date = date_parser.parse(day_menu['Date']).date()

        menu_day = MenuDay.query.filter_by(restaurant_id=restaurant.id, date=day_date).first()
        if not menu_day:
            menu_day = MenuDay(date=day_date, restaurant_id=restaurant.id)
            db.session.add(menu_day)
            db.session.commit()
            print(f"Lisätty päivä: {menu_day.date} ravintolalle {restaurant.name}")

        set_menus = day_menu.get('SetMenus', [])
        if not set_menus:
            print(f"Ei menuja päivälle {day_date} ravintolassa {restaurant.name}")
            continue

        for menu in set_menus:
            menu_name = menu.get('Name', '')
            components = menu.get('Components', [])
            cleaned_components = [c.replace('\n', ' ').strip() for c in components]
            components_text = "\n".join(cleaned_components)
            menu_price = menu.get('Price', '')

            existing_menu = Menu.query.filter_by(
                name=menu_name,
                description=components_text,
                price=menu_price,
                menu_day_id=menu_day.id
            ).first()

            if not existing_menu:
                new_menu = Menu(
                    name=menu_name,
                    description=components_text,
                    price=menu_price,
                    menu_day_id=menu_day.id
                )
                db.session.add(new_menu)
                db.session.commit()
                print(f"Lisätty menu: {menu_name} - {components_text} ({menu_price}) päivälle {day_date}")
            else:
                print(f"Menu jo olemassa: {menu_name} - {components_text} ({menu_price}) päivälle {day_date}")

# Function to extract menus for a specific day
def get_menus_for_day(menu_data, date_today):
    if menu_data is None:
        return []
    
    for day_menu in menu_data.get("MenusForDays", []):
        day_date = date_parser.parse(day_menu['Date']).date()
        if day_date == date_today:
            return day_menu.get('SetMenus', [])
    return []

# Function to get the current day in Finnish
def get_current_day_in_finnish():
    days_of_week = ['Maanantai', 'Tiistai', 'Keskiviikko', 'Torstai', 'Perjantai', 'Lauantai', 'Sunnuntai']
    current_day_index = datetime.now().weekday()
    return days_of_week[current_day_index] 


# Test route to verify database contents
@app.route('/test_db')
def test_db():
    update_database()
    restaurants = Restaurant.query.all()
    output = ""
    for r in restaurants:
        output += f"Ravintola: {r.name} ({r.opening_hours})<br>"
        for day in r.menu_days:
            output += f"&emsp;Päivä: {day.date}<br>"
            for menu in day.menus:
                output += f"&emsp;&emsp;Menu: {menu.description} ({menu.price})<br>"
    return output or "Tietokanta tyhjä"


# Home route: Redirects to the current day's menu
@app.route('/')
def home():
    today_str = datetime.now().strftime("%Y-%m-%d")
    return redirect(url_for('show_day', date_str=today_str))

# Route to show the menu for a specific day
@app.route('/day/<date_str>')
def show_day(date_str):
    # Convert URL parameter to a date
    try:
        requested_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        # If the format is wrong, fallback to today
        requested_date = datetime.now().date()

    # Query all MenuDay objects for this date
    menu_days = MenuDay.query.filter_by(date=requested_date).all()

    all_restaurant_content = []
    for menu_day in menu_days:
        restaurant = menu_day.restaurant
        menus = menu_day.menus

        if menus:
            all_restaurant_content.append({
                "restaurant_name": restaurant.name,
                "day_menus": [
                    {"Name": m.name, "Components": [c for c in m.description.split("\n") if c.strip()], "Price": m.price}
                    for m in menus
                ],
                "Opening_hours": restaurant.opening_hours or "Tarkista aukioloaika"
            })

    # Find previous and next available days that have menus
    prev_day_entry = MenuDay.query.filter(MenuDay.date < requested_date).order_by(desc(MenuDay.date)).first()
    next_day_entry = MenuDay.query.filter(MenuDay.date > requested_date).order_by(asc(MenuDay.date)).first()

    prev_day_url = url_for('show_day', date_str=prev_day_entry.date.strftime("%Y-%m-%d")) if prev_day_entry else None
    next_day_url = url_for('show_day', date_str=next_day_entry.date.strftime("%Y-%m-%d")) if next_day_entry else None

    # Format current date for display (e.g. "29.09.2025")
    current_date_display = requested_date.strftime("%d.%m.%Y")

    days_of_week_fi = ['Maanantai', 'Tiistai', 'Keskiviikko', 'Torstai', 'Perjantai', 'Lauantai', 'Sunnuntai']
    day_name_fi = days_of_week_fi[requested_date.weekday()]

    return render_template(
        'day.html',
        all_restaurant_content=all_restaurant_content,
        current_date=current_date_display,
        day_name=day_name_fi,
        prev_day_url=prev_day_url,
        next_day_url=next_day_url,
        datetime=str(datetime.now())
    )

with app.app_context():
    db.create_all()
    if Restaurant.query.count() == 0:
        print("Tietokanta tyhjä, haetaan data")
        update_database()
    else:
        print("Tietokanta jo olemassa")

if __name__ == '__main__':
    app.run(debug=True)

