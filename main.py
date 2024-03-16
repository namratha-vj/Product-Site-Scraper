import json
import csv

import requests
from bs4 import BeautifulSoup


def get_soup(url):
    response = requests.get(url)
    html = response.content
    soup = BeautifulSoup(html, 'html.parser')
    return soup


def product_info(soup):
    products_data = []
    products = soup.find_all('div', class_='product-thumb layout1')

    for product in products:
        image_tag = product.find('img')
        img_src = image_tag['src']
        title = image_tag['title']
        product_name = product.find('h2', class_='product-name').text.strip()
        price_tag = product.find('p', class_='price')
        description_tag = product.find('p', class_='product-des')
        product_url = product.find('a')['href']
        price = price_tag.text.strip()
        description = description_tag.text.strip()

        product_data = {
            "title": product_name,
            "image_source": img_src,
            "price": price,
            "description": description,
            "product_url": product_url
        }

        products_data.append(product_data)

    return products_data


def dump_csv(products_data, csv_file_name):
    with open(csv_file_name, 'w', newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["Title", "Image Source", "Price", "Description", "Product URL"])
        for product in products_data:
            writer.writerow([product['title'], product['image_source'], product['price'], product['description'],
                             product['product_url']])


def dump_json(products_data, json_file_name):
    with open(json_file_name, 'w') as json_file:
        json.dump(products_data, json_file, indent=4)


def main():
    url = "https://www.gifthampersuk.co.uk/food-hampers"
    soup = get_soup(url)
    cat_name = soup.find("h1", class_="category-name").text.strip()
    products_data = product_info(soup)
    json_file_name = f"rawdata/{cat_name}.json"
    dump_json(products_data, json_file_name)
    csv_file_name = f"rawdata/{cat_name}.csv"
    dump_csv(products_data, csv_file_name)


if __name__ == '__main__':
    main()
