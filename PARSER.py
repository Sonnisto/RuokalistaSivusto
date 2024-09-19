import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET

def get_menu(page_url):

    response = requests.get(page_url)
    soup = BeautifulSoup(response.content, "html.parser")

    menu_divs = soup.find_all("div", class_="menu-action-popup-content-item")
    right_menu_div = menu_divs[1]

    menu_link = right_menu_div.find("a")["href"]

    base_url = "https://www.unica.fi"
    menu_url = base_url + menu_link

    return menu_url

print(get_menu("https://www.unica.fi/ravintolat/Yliopisto/assarin-ullakko/"))

print(get_menu("https://www.unica.fi/ravintolat/Kupittaa/dental/"))


def parse_rss(xml_content):
    root = ET.fromstring(xml_content)
    channel = root.find('channel')
    items = channel.findall('item')

    rss_data = []
    for item in items:
         rss_item = {
            'title': item.find('title').text,
            'link': item.find('link').text,
            'description': item.find('description').text,
            'guid': item.find('guid').text
        }
         
    rss_data.append(rss_item)
    
    return rss_data





def get_different_menu_url(url):
    return;