import re
import openai
import os
import json
import csv

import requests
from bs4 import BeautifulSoup, Comment
from markdownify import MarkdownConverter
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

load_dotenv()
api_key = os.getenv("API_KEY")


def get_soup(url, use_selenium=False):
    try:
        if use_selenium:
            driver = webdriver.Chrome()
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
        print(f"An error occurred: {e}")
        return None


def clean_html(soup):
    if soup.head:
        soup.head.decompose()
    for script_or_style in soup.find_all(["script", "style"]):
        script_or_style.decompose()  # Remove script and style elements

    # Remove comments
    comments = soup.find_all(string=lambda text: isinstance(text, Comment))
    for comment in comments:
        comment.extract()

    unwanted_attributes = ["class", "id", "onclick", "onerror", "onload"]
    for tag in soup.find_all():
        for attribute in list(tag.attrs):
            if attribute.startswith(("data-", "aria-", "on")) or attribute in unwanted_attributes:
                del tag.attrs[attribute]

    unwanted_tags = ['header', 'footer', 'nav', 'aside', 'svg', 'form', 'input', 'textarea', 'button', 'select']
    for tag in unwanted_tags:
        for element in soup.find_all(tag):
            element.decompose()

    for tag_name in ['span', 'div', 'section']:
        for tag in soup.find_all(tag_name):
            tag.unwrap()

    return soup.prettify()


def count_tokens(cleaned_html):
    tokens = cleaned_html.split()
    return len(tokens)


def html_to_clean_markdown(html_text):
    markdown = MarkdownConverter().convert(html_text)
    cleaned_markdown = re.sub(r'\n{3,}', '\n\n', markdown)
    cleaned_markdown = cleaned_markdown.strip('\n')
    return cleaned_markdown


def llm_output(cleaned_markdown):
    system_propt = """
    You are a helpful assistant that extracts product information from provided text and outputs the details in JSON format. 
    The JSON object should contain the following fields: product_title, description (complete details about the product), vendor, type (category of the product), color, size, and price. 
    If any of the fields cannot be determined from the given text, leave them blank. Focus on accurately extracting all available product details.
    """
    client = openai.OpenAI(
        base_url="https://api.endpoints.anyscale.com/v1",
        api_key=api_key)

    chat_completion = client.chat.completions.create(
        model="mistralai/Mixtral-8x7B-Instruct-v0.1",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that outputs in JSON."},
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


def write_to_csv(llmoutput, filename):
    data = json.loads(llmoutput)
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['product_title', 'description', 'vendor', 'type', 'color', 'size', 'price']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow(data)

    print(f"Data written to {filename}")


def main(url):
    soup = get_soup(url, use_selenium=False)
    cleaned_html = clean_html(soup)
    # print(cleaned_html)
    token_count = count_tokens(cleaned_html)
    print(f"Number of tokens in the cleaned HTML: {token_count}")
    cleaned_markdown = html_to_clean_markdown(cleaned_html)
    llm_response = llm_output(cleaned_markdown)
    print("LLM Response:", llm_response)
    write_to_csv(llm_response, 'rawdata/product_info.csv')


if __name__ == "__main__":
    url = 'https://www.gifthampersuk.co.uk/chocolate-mountain-gift-hamper-uk'
    main(url)
