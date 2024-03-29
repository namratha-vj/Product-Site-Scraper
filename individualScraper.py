import csv
from main import get_soup


def individual_product_info(soup, product_url):
    title = soup.find('h1', class_='product-name').text.strip()
    id_tag = soup.find('ul', id='brand-and-availability')
    ex_text = id_tag.find_all('span', class_='ex-text')
    # availability = id_tag.find_all('li')[1].text.split(":")[1].strip()
    if len(ex_text) > 2:
        ex_text = id_tag.find_all('span', class_='ex-text')[1].text
        availability = id_tag.find_all('span', class_='ex-text')[2].text
    else:
        ex_text = id_tag.find_all('span', class_='ex-text')[0].text
        availability = id_tag.find_all('span', class_='ex-text')[1].text
    price_tag = soup.find('span', class_='placeholder-price-holder').text.strip()
    description_div = soup.find('div', id='tab-description')
    description_li = description_div.find_all('li')
    description = [desc.text for desc in description_li]
    if len(description) < 1:
        description_p = description_div.find_all('p')
        description = [desc.text for desc in description_p]

    image_src = soup.find("a", class_="thumbnail").img['src']

    product_data = {
        "product_id": ex_text,
        "title": title,
        "availability": availability,
        "price": price_tag,
        "description": description,
        "image_source": image_src,
        "product_url": product_url
    }

    return product_data


def dump_product_info(product_data_list, csv_file_name):
    with open(csv_file_name, 'w', newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["Product ID", "Title", "Availability", "Price", "Description", "Image Source", "Product URL"])
        for product_data in product_data_list:
            writer.writerow([product_data['product_id'],
                             product_data['title'],
                             product_data['availability'],
                             product_data['price'],
                             product_data['description'],
                             product_data['image_source'],
                             product_data['product_url']])


if __name__ == '__main__':
    urls = ["https://www.gifthampersuk.co.uk/care-hampers/recovery-treats-gift-hampers-uk",
            "https://www.gifthampersuk.co.uk/food-hampers/a-special-treat-for-you-gift-hamper-uk",
            "https://www.gifthampersuk.co.uk/food-hampers/afternoon-tea-for-two-home-delivery-gift-hamper-uk"]
    product_data_list_ = []
    for url in urls:
        soup = get_soup(url)
        product_data_ = individual_product_info(soup, url)
        product_data_list_.append(product_data_)

    csv_file_name_ = "food-hamper.csv"
    dump_product_info(product_data_list_, csv_file_name_)
