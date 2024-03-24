import streamlit as st
from chromadb.utils.embedding_functions import OpenCLIPEmbeddingFunction
from chromadb.utils.data_loaders import ImageLoader
import chromadb


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


def display_search_results(results, col1, col2, col3):
    if results:
        st.write(f"Found {len(results['ids'][0])} results!")
        with col1:
            st.write("Result 1")
            st.image(results['data'][0][0], caption=f"Distance: {results['distances'][0][0]}")
            st.write(f"URI: {results['uris'][0][0]}")
            st.write(results['metadatas'][0][0])
        with col2:
            st.write("Result 2")
            st.image(results['data'][0][1], caption=f"Distance: {results['distances'][0][1]}")
            st.write(f"URI: {results['uris'][0][1]}")
            st.write(results['metadatas'][0][1])
        with col3:
            st.write("Result 3")
            st.image(results['data'][0][2], caption=f"Distance: {results['distances'][0][2]}")
            st.write(f"URI: {results['uris'][0][2]}")
            st.write(results['metadatas'][0][2])


def handle_text_search(query_text, multimodal_db):
    if query_text:
        st.write(f'Searching for: {query_text}')
        results = multimodal_db.query(
            query_texts=[query_text],
            n_results=3,
            include=['documents', 'distances', 'metadatas', 'data', 'uris'],
        )
        col1, col2, col3 = st.columns(3)
        display_search_results(results, col1, col2, col3)


def handle_uri_search(query_uri, multimodal_db):
    if query_uri:
        st.write(f'Searching for: {query_uri}')
        st.image(query_uri, caption='Query Image', width=200)
        uri = query_uri.split("/")[1]
        code = uri.split("(")[0].replace(" ", "")
        st.write(f'Code: {code}')
        results = multimodal_db.query(
            query_uris=[query_uri],
            n_results=3,
            include=['documents', 'distances', 'metadatas', 'data', 'uris'],
            where={'filename': {'$ne': code}}
        )
        col1, col2, col3 = st.columns(3)
        display_search_results(results, col1, col2, col3)


def main():
    st.title('Image Search Engine')
    st.write('This is a simple image search engine using OpenCLIP embeddings and ChromaDB.')

    multimodal_db = setup_chroma_db()
    option = st.radio("Select an option", ('Search by text', 'Search by URI'), horizontal=True, index=1)
    if option == 'Search by text':
        query_text = st.text_input('Enter your search query:')
        handle_text_search(query_text, multimodal_db)

    if option == 'Search by URI':
        query_uri = st.text_input('Enter the URI of the image you want to search for:')
        handle_uri_search(query_uri, multimodal_db)


if __name__ == "__main__":
    main()
