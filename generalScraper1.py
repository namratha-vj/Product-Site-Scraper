# import concurrent.futures
# import os
# import json
# import csv
# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# from bs4 import BeautifulSoup
# from markdownify import MarkdownConverter
# import re
# import openai
# from dotenv import load_dotenv
#
# # Load environment variables
# load_dotenv()
# api_key = os.getenv("API_KEY")
#
# def get_soup(url):
#     options = Options()
#     options.headless = True
#     driver = webdriver.Chrome(options=options)
#     driver.get(url)
#     driver.implicitly_wait(10)
#     html = driver.page_source
#     driver.quit()
#     return BeautifulSoup(html, 'html.parser')
#
# def clean_html(soup):
#     for tag in soup(['script', 'style', 'head', 'header', 'footer', 'nav', 'aside', 'form', 'input', 'textarea', 'button', 'select']):
#         tag.decompose()
#     return soup.get_text()
#
# def html_to_markdown(html_text):
#     markdown = MarkdownConverter().convert(html_text)
#     return re.sub(r'\n{3,}', '\n\n', markdown).strip()
#
# def llm_output(cleaned_markdown):
#     system_prompt = """
#     You are a helpful assistant that extracts product information from provided text and outputs the details in JSON format.
#     The JSON object should contain the following fields: product_title, description, vendor, type (category of the product), color, size, and price.
#     If any of the fields cannot be determined from the given text, leave them blank.
#     """
#     client = openai.OpenAI(base_url="https://api.endpoints.anyscale.com/v1", api_key=api_key)
#     chat_completion = client.chat.completions.create(
#         model="mistralai/Mixtral-8x7B-Instruct-v0.1",
#         messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": cleaned_markdown}],
#         response_format={"type": "json_object", "schema": {
#             "type": "object",
#             "properties": {
#                 "product_title": {"type": "string"},
#                 "description": {"type": "string"},
#                 "vendor": {"type": "string"},
#                 "type": {"type": "string"},
#                 "color": {"type": "string"},
#                 "size": {"type": "string"},
#                 "price": {"type": "string"},
#             },
#             "required": ["product_title"]
#         }},
#         temperature=0.7
#     )
#     return chat_completion.choices[0].message.content
#
# def append_to_csv(data, filename='product_info.csv'):
#     with open(filename, 'a', newline='', encoding='utf-8') as csvfile:
#         fieldnames = ['product_title', 'description', 'vendor', 'type', 'color', 'size', 'price']
#         writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
#         writer.writerow(data)
#
# def process_url(url):
#     soup = get_soup(url)
#     cleaned_html = clean_html(soup)
#     cleaned_markdown = html_to_markdown(cleaned_html)
#     llm_response = llm_output(cleaned_markdown)
#     try:
#         extracted_info = json.loads(llm_response)
#         append_to_csv(extracted_info)
#         print(f"Processed URL: {url}")
#     except json.JSONDecodeError:
#         print(f"Failed to decode JSON from LLM response for URL: {url}")
#
# def process_urls_in_parallel(urls_file, max_workers=4):
#     with open(urls_file, 'r') as file:
#         urls = [url.strip() for url in file.readlines()]
#
#     with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
#         executor.map(process_url, urls)
#
# if __name__ == "__main__":
#     process_urls_in_parallel('urls.txt')
# import re
# import os
# import json
# import csv
# import requests
# from bs4 import BeautifulSoup, Comment
# from markdownify import MarkdownConverter
# from dotenv import load_dotenv
# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# import openai
# from concurrent.futures import ThreadPoolExecutor, as_completed
#
# # Load environment variables
# load_dotenv()
# api_key = os.getenv("API_KEY")
#
# def get_soup(url, use_selenium=False):
#     try:
#         if use_selenium:
#             options = Options()
#             options.headless = True
#             driver = webdriver.Chrome(options=options)
#             driver.get(url)
#             driver.implicitly_wait(10)
#             html = driver.page_source
#             driver.quit()
#         else:
#             response = requests.get(url)
#             response.raise_for_status()
#             html = response.content
#         soup = BeautifulSoup(html, 'html.parser')
#         return soup
#     except Exception as e:
#         print(f"An error occurred while retrieving URL {url}: {e}")
#         return None
#
# def clean_html(soup):
#     if soup is None:
#         return None
#     if soup.head:
#         soup.head.decompose()
#     for script_or_style in soup.find_all(["script", "style"]):
#         script_or_style.decompose()
#     comments = soup.find_all(string=lambda text: isinstance(text, Comment))
#     for comment in comments:
#         comment.extract()
#     unwanted_attributes = ["class", "id", "onclick", "onerror", "onload"]
#     for tag in soup.find_all():
#         for attribute in list(tag.attrs):
#             if attribute.startswith(("data-", "aria-", "on")) or attribute in unwanted_attributes:
#                 del tag.attrs[attribute]
#     unwanted_tags = ['header', 'footer', 'nav', 'aside', 'svg', 'form', 'input', 'textarea', 'button', 'select']
#     for tag in unwanted_tags:
#         for element in soup.find_all(tag):
#             element.decompose()
#     for tag_name in ['span', 'div', 'section']:
#         for tag in soup.find_all(tag_name):
#             tag.unwrap()
#     return soup.prettify()
#
# def count_tokens(cleaned_html):
#     if cleaned_html is None:
#         return 0
#     tokens = cleaned_html.split()
#     return len(tokens)
#
# def html_to_clean_markdown(html_text):
#     if not html_text:
#         return ""
#     markdown = MarkdownConverter().convert(html_text)
#     cleaned_markdown = re.sub(r'\n{3,}', '\n\n', markdown)
#     cleaned_markdown = cleaned_markdown.strip('\n')
#     return cleaned_markdown
#
# def llm_output(cleaned_markdown):
#     system_propt = """
#     You are a helpful assistant that extracts product information from provided text and outputs the details in JSON format.
#     The JSON object should contain the following fields: product_title, description (complete details about the product), vendor, type (category of the product), color, size, and price.
#     If any of the fields cannot be determined from the given text, leave them blank. Focus on accurately extracting all available product details.
#     """
#     client = openai.OpenAI(
#         base_url="https://api.endpoints.anyscale.com/v1",
#         api_key=api_key)
#
#     chat_completion = client.chat.completions.create(
#         model="mistralai/Mixtral-8x7B-Instruct-v0.1",
#         messages=[
#             {"role": "system", "content": "You are a helpful assistant that outputs in JSON."},
#             {"role": "user", "content": cleaned_markdown}
#         ],
#         response_format={
#             "type": "json_object",
#             "schema": {
#                 "type": "object",
#                 "properties": {
#                     "product_title": {"type": "string"},
#                     "description": {"type": "string"},
#                     "vendor": {"type": "string"},
#                     "type": {"type": "string"},
#                     "color": {"type": "string"},
#                     "size": {"type": "string"},
#                     "price": {"type": "string"},
#                 },
#                 "required": ["product_title"]
#             },
#         },
#         temperature=0.7
#     )
#     llmoutput = chat_completion.choices[0].message.content
#
#     return llmoutput
#
# def append_to_csv(llmoutput, filename):
#     data = json.loads(llmoutput)
#     if not data:
#         print("No data to append.")
#         return
#     with open(filename, 'a', newline='', encoding='utf-8') as csvfile:
#         fieldnames = ['product_title', 'description', 'vendor', 'type', 'color', 'size', 'price']
#         writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
#         writer.writerow(data)
#     print(f"Data appended to {filename}")
#
# def process_url(url):
#     print(f"Processing URL: {url}")
#     soup = get_soup(url, use_selenium=True)
#     if soup is None:
#         return
#     cleaned_html = clean_html(soup)
#     if cleaned_html is None:
#         return
#     token_count = count_tokens(cleaned_html)
#     print(f"Number of tokens in the cleaned HTML: {token_count}")
#     cleaned_markdown = html_to_clean_markdown(cleaned_html)
#     llm_response = llm_output(cleaned_markdown)
#     print("LLM Response:", llm_response)
#     append_to_csv(llm_response, 'product_info2.csv')
#
# def process_urls_in_parallel(filename, max_workers=5):
#     with open(filename, 'r') as file:
#         urls = file.read().splitlines()
#
#     with ThreadPoolExecutor(max_workers=max_workers) as executor:
#         future_to_url = {executor.submit(process_url, url): url for url in urls}
#         for future in as_completed(future_to_url):
#             url = future_to_url[future]
#             try:
#                 data = future.result()
#             except Exception as exc:
#                 print(f'{url} generated an exception: {exc}')
#
# if __name__ == "__main__":
#     urls_file = 'urls.txt'  # The file containing URLs, one per line
#     process_urls_in_parallel(urls_file)
import concurrent.futures
import os
import json
import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from markdownify import MarkdownConverter
import re
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
api_key = os.getenv("API_KEY")

def initialize_csv(filename='product_info.csv'):
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['product_title', 'description', 'vendor', 'type', 'color', 'size', 'price']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

def get_soup(url):
    options = Options()
    options.headless = True
    driver = webdriver.Chrome(options=options)
    driver.get(url)
    driver.implicitly_wait(10)
    html = driver.page_source
    driver.quit()
    return BeautifulSoup(html, 'html.parser')

def clean_html(soup):
    for tag in soup(['script', 'style', 'head', 'header', 'footer', 'nav', 'aside', 'form', 'input', 'textarea', 'button', 'select']):
        tag.decompose()
    return soup.get_text()

def html_to_markdown(html_text):
    markdown = MarkdownConverter().convert(html_text)
    return re.sub(r'\n{3,}', '\n\n', markdown).strip()

def llm_output(cleaned_markdown):
    system_prompt = """
    You are a helpful assistant that extracts product information from provided text and outputs the details in JSON format.
    The JSON object should contain the following fields: product_title, description, vendor, type (category of the product), color, size, and price.
    If any of the fields cannot be determined from the given text, leave them blank.
    """
    client = openai.OpenAI(base_url="https://api.endpoints.anyscale.com/v1", api_key=api_key)
    chat_completion = client.chat.completions.create(
        model="mistralai/Mixtral-8x7B-Instruct-v0.1",
        messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": cleaned_markdown}],
        response_format={"type": "json_object", "schema": {
            "type": "object",
            "properties": {
                "product_title": {"type": "string"},
                "description": {"type": "string"},
                "vendor": {"type": "string"},
                "type": {"type": "string"},
                "color": {"type": "string"},
                "size": {"type": "string"},
                "price": {"type": "string"},
            },
            "required": ["product_title"]
        }},
        temperature=0.7
    )
    return chat_completion.choices[0].message.content

def append_to_csv(data, filename='product_info3.csv'):
    with open(filename, 'a', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['product_title', 'description', 'vendor', 'type', 'color', 'size', 'price']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writerow(data)

def process_url(url):
    soup = get_soup(url)
    cleaned_html = clean_html(soup)
    cleaned_markdown = html_to_markdown(cleaned_html)
    llm_response = llm_output(cleaned_markdown)
    try:
        extracted_info = json.loads(llm_response)
        append_to_csv(extracted_info)
        print(f"Processed URL: {url}")
    except json.JSONDecodeError:
        print(f"Failed to decode JSON from LLM response for URL: {url}")

def process_urls_in_parallel(urls_file, max_workers=4):
    initialize_csv()  # Initialize the CSV file before processing
    with open(urls_file, 'r') as file:
        urls = [url.strip() for url in file.readlines()]

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        executor.map(process_url, urls)

if __name__ == "__main__":
    process_urls_in_parallel('urls.txt')

