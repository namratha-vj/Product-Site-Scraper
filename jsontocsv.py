import json
import os
import pandas as pd
from main import get_soup
from individualScraper import individual_product_info, dump_product_info


def get_json_files():
    json_files = []
    for file in os.listdir("rawdata"):
        if file.endswith(".json"):
            json_files.append(file)
    return json_files


all_files = get_json_files()
data = pd.read_json("rawdata/" + all_files[0])

product_data_list_ = []
for index, row in data.iterrows():
    url = row["product_url"]
    soup = get_soup(url)
    product_info = individual_product_info(soup, url)
    product_data_list_.append(product_info)
    print(f"Scraped {index} of {len(data)}")

csv_file_name = f"rawdata/{all_files[0].split('.')[0]}.csv"
dump_product_info(product_data_list_, csv_file_name)
