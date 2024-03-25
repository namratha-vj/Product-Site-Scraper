# Product Site Scraper

`main.py`
this file has the code to create a json file of all the products on the site.

`jsonToCSV.ipynb`
this file has the code to convert the json of a product to an individual csv file.

`jsonToCSV.ipynb` uses `individualScraper.py` to scrape all the contents of a product page.


# Image Search Engine with Streamlit, OpenCLIP, and ChromaDB
This Python script powers a simple yet effective image search engine using Streamlit for the web interface, OpenCLIP for image and text embeddings, and ChromaDB for persistent vector storage and querying. It allows users to search for images using text queries, URIs, or directly uploading images.

# Features
Text Search: Allows searching the database using text queries.
URI Search: Enables search using the Uniform Resource Identifier (URI) of an image.
Image Upload Search: Users can upload an image to search for visually similar images in the database.

# Requirements
Before you begin, ensure you have the following installed:

Python 3.8+
Streamlit
OpenCLIP (and its dependencies)
ChromaDB
NumPy
PIL
You can install most of these dependencies using pip. For specific installation instructions for OpenCLIP and ChromaDB, refer to their respective documentation.

## Setup

Follow these steps to get the image search engine up and running on your local machine:

### Clone the Repository
First, clone this repository to your local machine using the following command:


`<https://github.com/namratha-vj/Product-Site-Scraper>` 

### Install Dependencies
Navigate to the cloned directory and install the required Python packages using:

```bash
pip install -r requirements.txt
```

### Running the Script

To start the web interface, run the following command in your terminal:

```bash
streamlit run simpleUI.py
```

This command will start a local server and open the web interface in your default browser. You can now search for images using text queries, URIs, or by uploading images.

## How It Works

This section explains the core functionalities of the image search engine.

### Setup ChromaDB

The `setup_chroma_db` function initializes the ChromaDB client and creates a collection named `multimodal_db` using OpenCLIP embeddings for image and text processing. This setup is crucial for enabling the search capabilities of the engine.

### Search Functions

Depending on the search option selected by the user, the application uses one of three handlers to process the query:

- `handle_text_search` for text queries,
- `handle_uri_search` for URI-based searches, and
- `handle_image_search` for searches initiated with an uploaded image.

These functions manage the querying process and gather results from the `multimodal_db`.

### Display Results

The `display_search_results` function is responsible for presenting the search results to the user. It renders the results on the web page, showing image previews, their distances (indicating similarity), and metadata. This function ensures users can visually browse through the results and obtain relevant information about each one.
