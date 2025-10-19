import json
import requests
from datetime import datetime, timedelta
import pytz

SODEXO_URLS = [
    "https://www.sodexo.fi/ruokalistat/output/weekly_json/160",  # Turun AMK Lemminkäisenkatu
    "https://www.sodexo.fi/ruokalistat/output/weekly_json/102",  # Flavoria
]


# Fetches and processes Sodexo menu data from the provided URLs
def fetch_sodexo_data():
    all_restaurants = []
    for url in SODEXO_URLS:
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Virhe haettaessa {url}: {e}")
            continue

        sodexo_json = response.json()
        transformed = transform_sodexo_json(sodexo_json)
        if transformed:
            all_restaurants.append(transformed)

    return all_restaurants


# Converts Finnish day names to ISO 8601 date strings
def convert_day_to_iso8601(day_name):
    days_of_week = [
        "Maanantai",
        "Tiistai",
        "Keskiviikko",
        "Torstai",
        "Perjantai",
        "Lauantai",
        "Sunnuntai",
    ]
    today = datetime.now()
    current_day_index = today.weekday()

    try:
        day_index = days_of_week.index(day_name)
    except ValueError:
        print(f"Tuntematon viikonpäivä: {day_name}")
        return None

    date_offset = day_index - current_day_index
    target_date = today + timedelta(days=date_offset)

    timezone = pytz.timezone("UTC")
    target_date_with_time = timezone.localize(target_date)
    return target_date_with_time.isoformat()


# Transforms Sodexo JSON data into a standardized format
def transform_sodexo_json(sodexo_data):
    restaurant_name = sodexo_data["meta"]["ref_title"]

    transformed_data = {"RestaurantName": restaurant_name, "MenusForDays": []}

    for meal_date in sodexo_data["mealdates"]:
        day_name = meal_date["date"]
        iso_date = convert_day_to_iso8601(day_name)

        if not iso_date:
            continue

        menu_entry = {"Date": iso_date, "SetMenus": []}

        for course in meal_date.get("courses", {}).values():
            price = course.get("price", "N/A")
            title = course.get("title_fi", "No title")

            menu_entry["SetMenus"].append(
                {"Name": "Lounas", "Price": price, "Components": [title]}
            )

        transformed_data["MenusForDays"].append(menu_entry)

    return transformed_data


if __name__ == "__main__":
    all_data = fetch_sodexo_data()
    print(json.dumps(all_data, ensure_ascii=False, indent=2))
