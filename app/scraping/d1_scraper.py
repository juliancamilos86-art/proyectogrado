import requests
from bs4 import BeautifulSoup

def scrape_example():
    url = "https://ejemplo.com"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    return [item.text for item in soup.find_all("h1")]
