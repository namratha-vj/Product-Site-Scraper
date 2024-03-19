import requests
from bs4 import BeautifulSoup, Comment
from markdownify import MarkdownConverter
import re
import openai
import os
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

load_dotenv()
api_key = os.getenv("API_KEY")


def get_soup(url, use_selenium=False):
    try:
        if use_selenium:
            # Configure Selenium options
            driver = webdriver.Chrome()
            driver.get(url)
            driver.implicitly_wait(10)  # Wait for up to 10 seconds for page to load
            html = driver.page_source
            driver.quit()  # Close the browser
        else:
            response = requests.get(url)
            response.raise_for_status()  # Raise an exception for non-2xx status codes
            html = response.content

        soup = BeautifulSoup(html, 'html.parser')
        return soup
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def clean_html(soup):
    # No need to re-parse the soup object with BeautifulSoup
    if soup.head:
        soup.head.decompose()
    for script_or_style in soup.find_all(["script", "style"]):
        script_or_style.decompose()  # Remove script and style elements

    # Remove comments
    comments = soup.find_all(string=lambda text: isinstance(text, Comment))
    for comment in comments:
        comment.extract()

    unwanted_attributes = ["class", "id", "style", "onclick", "onerror", "onload"]
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
    client = openai.OpenAI(
        base_url="https://api.endpoints.anyscale.com/v1",
        api_key=api_key)

    # Note: not all arguments are currently supported and will be ignored by the backend.
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
                    "product_description": {"type": "string"},
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


def main(url):
    soup = get_soup(url, use_selenium=True)
    cleaned_html = clean_html(soup)
    print(cleaned_html)
    token_count = count_tokens(cleaned_html)
    print(f"Number of tokens in the cleaned HTML: {token_count}")
    cleaned_markdown = html_to_clean_markdown(cleaned_html)
    llm_response = llm_output(cleaned_markdown)
    print("LLM Response:", llm_response)


if __name__ == "__main__":
    # Example URL - replace this with any URL you want to process
    url = 'https://www.thesouledstore.com/product/black-hoodie-women-oversized-hoodie?gte=2'
    main(url)
