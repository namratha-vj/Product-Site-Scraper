import requests
from bs4 import BeautifulSoup

url = "https://www.gifthampersuk.co.uk/food-hampers"

response = requests.get(url)
html = response.content
soup = BeautifulSoup(html, 'html.parser')
print(soup.prettify())
imgs = soup.find_all("img")
print(imgs)
print("sdfaf")