import re
import os
import json
import csv
import requests
from urllib.parse import urlparse
from bs4 import BeautifulSoup, Comment
from markdownify import MarkdownConverter
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import openai
import pandas as pd

# Load environment variables
load_dotenv()
api_key = os.getenv("API_KEY")


def get_soup(url, use_selenium=False):
    try:
        if use_selenium:
            options = Options()
            options.headless = True
            driver = webdriver.Chrome(options=options)
            driver.get(url)
            driver.implicitly_wait(10)
            html = driver.page_source
            driver.quit()
        else:
            response = requests.get(url)
            response.raise_for_status()
            html = response.content
        soup = BeautifulSoup(html, 'html.parser')
        return soup
    except Exception as e:
        print(f"An error occurred while retrieving URL {url}: {e}")
        return None


def clean_html(soup, root_url):
    if soup is None:
        return None

    # Parse the root URL to extract the domain
    parsed_root_url = urlparse(root_url)
    root_domain = parsed_root_url.netloc

    for element in soup(
            ["script", "style", "header", "footer", "nav", "aside", "svg", "form", "input", "textarea", "button",
             "select", "a"]):
        element.decompose()

    for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
        comment.extract()

    for tag in soup.find_all():
        tag.attrs = {key: value for key, value in tag.attrs.items() if
                     not key.startswith(("data-", "aria-", "on")) and key not in ["class", "id", "onclick", "onerror",
                                                                                  "onload"]}
    for tag_name in ['span', 'div', 'section']:
        for tag in soup.find_all(tag_name):
            tag.unwrap()

    # Filter out external image URLs
    img_urls = [img['src'] for img in soup.find_all('img') if urlparse(img['src']).netloc == root_domain]

    return soup.prettify(), img_urls


def count_tokens(cleaned_html):
    if cleaned_html is None:
        return 0
    tokens = cleaned_html.split()
    return len(tokens)


def html_to_clean_markdown(html_text):
    if not html_text:
        return ""
    markdown = MarkdownConverter().convert(html_text)
    cleaned_markdown = re.sub(r'\n{3,}', '\n\n', markdown)
    cleaned_markdown = cleaned_markdown.strip('\n')
    return cleaned_markdown


def llm_output(cleaned_markdown):
    system_prompt = """
    You are a helpful assistant that extracts product information from provided text and outputs the details in JSON format. 
    The JSON object should contain the following fields: product_title, description (complete details about the product), vendor, type (category of the product), color, size, and price. 
    If any of the fields cannot be determined from the given text, leave them blank. Focus on accurately extracting all available product details.
    """
    client = openai.OpenAI(
        base_url="https://api.endpoints.anyscale.com/v1",
        api_key=api_key)

    # noinspection PyTypeChecker
    chat_completion = client.chat.completions.create(
        model="mistralai/Mixtral-8x7B-Instruct-v0.1",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": cleaned_markdown}
        ],
        response_format={
            "type": "json_object",
            "schema": {
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
            },
        },
        temperature=0.7
    )
    llmoutput = chat_completion.choices[0].message.content

    return llmoutput


def append_to_csv(llmoutput, img_urls, filename):
    data = json.loads(llmoutput)
    if not data:
        print("No data to append.")
        return
    with open(filename, 'a', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['product_title', 'description', 'vendor', 'type', 'color', 'size', 'price', 'image_urls']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        data['img_urls'] = ','.join(img_urls)
        writer.writerow(data)
    print(f"Data appended to {filename}")


def append_to_json(llmoutput, img_urls, filename):
    data = json.loads(llmoutput)
    if not data:
        print("No data to append.")
        return

    data['img_urls'] = img_urls

    with open(filename, 'a', encoding='utf-8') as jsonfile:
        json.dump(data, jsonfile, ensure_ascii=False)
        jsonfile.write('\n')

    print(f"Data appended to {filename}")


def save_to_markdown(cleaned_markdown, filename):
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(cleaned_markdown)
    print(f"Cleaned Markdown saved to {filename}")


def process_url(url, markdown_dir):
    # Define a regex pattern to match the root URL
    root_url_pattern = r"https?://(?:www\.)?([^/]+)"
    root_url_match = re.match(root_url_pattern, product_urls[0])
    root_url = root_url_match.group(0) if root_url_match else None

    # Define a regex pattern to match the product name
    product_name_pattern = r"/product/([^/]+)"
    product_name_match = re.search(product_name_pattern, url)
    product_name = product_name_match.group(1) if product_name_match else None
    os.makedirs(markdown_dir, exist_ok=True)

    print(f"Processing URL: {url}")
    soup = get_soup(url, use_selenium=True)
    if soup is None:
        return
    cleaned_html, img_urls = clean_html(soup, root_url)
    if cleaned_html is None:
        return
    token_count = count_tokens(cleaned_html)
    print(f"Number of tokens in the cleaned HTML: {token_count}")
    cleaned_markdown = html_to_clean_markdown(cleaned_html)
    markdown_filename = os.path.join(markdown_dir, f"{product_name}.md")
    save_to_markdown(cleaned_markdown, markdown_filename)

    llm_response = llm_output(cleaned_markdown)
    print("LLM Response:", llm_response)
    # append_to_csv(llm_response, img_urls, 'rawdata/myharvestfarms/product_info.csv')
    append_to_json(llm_response, img_urls, 'rawdata/myharvestfarms/product_info.json')


if __name__ == "__main__":
    urls_file = "rawdata/myharvestfarms/product_urls.csv"
    markdown_dir = 'rawdata/myharvestfarms/markdown'
    df = pd.read_csv(urls_file)
    product_urls = df['url'].tolist()

    # process_url(product_urls[1], markdown_dir)

    for url in product_urls:
        process_url(url, markdown_dir)
