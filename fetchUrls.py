import csv
import json
from urllib.parse import urljoin
import sys

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Initialize global variable for webdriver instance
webdriver_instance = None


def get_webdriver_instance():
    """Get a webdriver instance."""
    global webdriver_instance
    if webdriver_instance is None:
        options = Options()
        webdriver_instance = webdriver.Chrome(options=options)
    return webdriver_instance


def get_webdriver_instance_no_img():
    """Get a webdriver instance with images disabled."""
    global webdriver_instance
    if webdriver_instance is None:
        options = Options()
        prefs = {"profile.managed_default_content_settings.images": 2}  # Disable images
        options.add_experimental_option("prefs", prefs)
        webdriver_instance = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return webdriver_instance


def get_soup(url, use_selenium=False):
    """Get a BeautifulSoup from a URL. If we use_selenium is True, use Selenium to get the page source."""
    try:
        if use_selenium:
            driver = get_webdriver_instance()
            driver.get(url)
            driver.implicitly_wait(10)
            html = driver.page_source
        else:
            response = requests.get(url)
            response.raise_for_status()
            html = response.text

        return BeautifulSoup(html, 'html.parser')

    except Exception as e:
        print(f"An error occurred while retrieving URL {url}: {e}")
        return None


def extract_link_text(link):
    """Extract the text of a link. If the text is empty, use the title or the content of the link."""
    text = link.text.strip()
    if text:
        return text

    title = link.get('title')
    if title:
        return title

    if link.contents:
        content_text = ''.join(c.strip() for c in link.contents if isinstance(c, str))
        if content_text:
            return content_text

    return link['href']


def fetch_urls(url, depth=0, max_depth=2, visited=None, urls=None, use_selenium=False, root_url=None, count=0):
    """Fetch URLs from a URL."""
    if visited is None:
        visited = set()
    if urls is None:
        urls = []

    # Use a set for quick URL lookup
    url_set = {u['url'] for u in urls}

    if depth > max_depth or url in visited:
        return urls

    visited.add(url)
    soup = get_soup(url, use_selenium)
    if not soup:
        return urls

    for link in soup.find_all("a", href=True):
        href = urljoin(root_url or url, link["href"])

        # Only process URLs that start with the root URL
        if href.startswith(root_url) and href not in url_set:
            text = extract_link_text(link)
            urlname = text.replace('\u00a0', ' ')  # Replace non-breaking spaces here
            urls.append({"urlname": urlname, "url": href})
            url_set.add(href)
            count += 1
            print(f"Depth {depth}: Scraped {count} URLs - {href}")
            urls = fetch_urls(href, depth + 1, max_depth, visited, urls, use_selenium, root_url, count)

    return urls


def save_urls(urls, file_path):
    """Save URLs to a CSV file."""
    try:
        with open(file_path, "w", newline="", encoding="utf-8") as csvfile:
            fieldnames = ["urlname", "url"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(urls)
        print(f"URLs saved to {file_path}")
    except Exception as e:
        print(f"An error occurred while saving URLs to {file_path}: {e}")


def save_to_json(urls, file_path):
    try:
        with open(file_path, "w", encoding="utf-8") as jsonfile:
            json.dump(urls, jsonfile, indent=4, ensure_ascii=False)
        print(f"URLs saved to {file_path}")
    except Exception as e:
        print(f"An error occurred while saving URLs to {file_path}: {e}")


def main():
    url1 = "https://www.gifthampersuk.co.uk"
    url2 = "https://www.neidhal.com"
    url3 = "https://shop.myharvestfarms.com"
    url4 = "https://snitch.co.in"
    url = url2
    max_depth = 3
    urls = fetch_urls(url, max_depth=max_depth, use_selenium=True, root_url=url)
    save_urls(urls, f"rawdata/myharvestfarms/csv_urls.csv")
    save_to_json(urls, "rawdata/myharvestfarms/json_urls.json")


if __name__ == "__main__":
    main()
