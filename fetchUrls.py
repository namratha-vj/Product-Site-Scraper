import requests
from bs4 import BeautifulSoup
import csv


url = "https://snitch.co.in"

response = requests.get(url)
soup = BeautifulSoup(response.content, "html.parser")

links = soup.find_all("a")

with open("urls.csv", "w", newline="") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["URL"])

    for link in links:
        href = link.get("href")
        writer.writerow([href])

print("URLs saved to urls.csv")

