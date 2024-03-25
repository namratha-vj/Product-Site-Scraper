import os
import streamlit as st
from chromadb.utils.embedding_functions import OpenCLIPEmbeddingFunction
from chromadb.utils.data_loaders import ImageLoader
import chromadb
import numpy as np
from PIL import Image


def setup_chroma_db():
    chroma_client = chromadb.PersistentClient(path="vectordb")
    image_loader = ImageLoader()
    multimodal_ef = OpenCLIPEmbeddingFunction()
    multimodal_db = chroma_client.get_or_create_collection(
        name="multimodal_db",
        embedding_function=multimodal_ef,
        data_loader=image_loader
    )
    return multimodal_db


def display_search_results(results, n_results):
    if results:
        for idx, result in enumerate(results['data'][0]):
            col_idx = idx % 3
            if col_idx == 0:
                cols = st.columns(3)

            with cols[col_idx]:
                st.write(f"Result {idx + 1}")
                st.image(result, caption=f"Distance: {results['distances'][0][idx]}")
                st.write(f"URI: {results['uris'][0][idx]}")
                st.caption(results['metadatas'][0][idx])

            if col_idx == 2 or idx == n_results - 1:
                st.write("---")


def handle_text_search(query_text, multimodal_db, n_results=3):
    if query_text:
        st.write(f'Search Results for: **{query_text}**')
        results = multimodal_db.query(
            query_texts=[query_text],
            n_results=n_results,
            include=['documents', 'distances', 'metadatas', 'data', 'uris'],
        )
        display_search_results(results, n_results)


def handle_uri_search(query_uri, multimodal_db, n_results=3):
    if query_uri:
        st.write(f'Searching for: {query_uri}')
        st.image(query_uri, caption='Query Image', width=200)
        results = multimodal_db.query(
            query_uris=[query_uri],
            n_results=n_results,
            include=['documents', 'distances', 'metadatas', 'data', 'uris'],
        )
        display_search_results(results, n_results)


def handle_image_search(query_image, multimodal_db, n_results=3):
    results = multimodal_db.query(
        query_images=[query_image],
        n_results=n_results,
        include=['documents', 'distances', 'metadatas', 'data', 'uris'],
    )
    display_search_results(results, n_results)


def save_uploadedfile(uploadedfile, file_name):
    with open(os.path.join("queryImg", file_name), "wb") as f:
        f.write(uploadedfile.getbuffer())
    return st.success("Image saved!")


def main():
    st.title('Image Search Engine')
    st.write('This is a simple image search engine using OpenCLIP embeddings and ChromaDB.')

    multimodal_db = setup_chroma_db()
    option = st.radio("Select an option", ('Search by text', 'Search by URI', 'Search by Image'), horizontal=True,
                      index=1)

    n_results = st.number_input("Number of results to display", min_value=1, value=3, step=1)

    if option == 'Search by text':
        query_text = st.text_input('Enter your search query:')
        handle_text_search(query_text, multimodal_db, n_results=n_results)

    if option == 'Search by URI':
        query_uri = st.text_input('Enter the URI of the image you want to search for:')
        handle_uri_search(query_uri, multimodal_db, n_results=n_results)

    if option == 'Search by Image':
        query_image = st.file_uploader('Upload an image to search for:', type=['jpg', 'jpeg', 'png'])
        if query_image:
            st.image(query_image, caption='Query Image', width=200)
            image = np.array(Image.open(query_image))
            handle_image_search(image, multimodal_db, n_results=n_results)


if __name__ == "__main__":
    main()
