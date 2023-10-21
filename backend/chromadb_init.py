import chromadb
from chromadb.config import Settings
import os
from pypdf import PdfReader

def init_chroma(path="./chromadb/"):
    chroma_client = chromadb.PersistentClient(path=path, settings=Settings(allow_reset=True))
    return chroma_client, chroma_client.list_collections()

def init_database(chroma_client):
    text_filter_str = os.environ.get('TEXT_FILTER')
    text_filters = set(text_filter_str.split(';')) if text_filter_str else set()

    base_dir = "./docs/"
    folders = [f for f in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, f))]

    for folder in folders:
        collection = chroma_client.get_or_create_collection(folder)
        folder_path = os.path.join(base_dir, folder)
        pdf_files = [f for f in os.listdir(folder_path) if f.endswith('.pdf')]

        for file in pdf_files:
            with open(os.path.join(folder_path, file), "rb") as pdf:
                reader = PdfReader(pdf)
                pages_text = [(p, reader.pages[p].extract_text()) for p in range(len(reader.pages))]

            for page, text in pages_text:
                for item in text_filters:
                    text = text.replace(item, ' ')
                collection.upsert(
                    documents=[text],
                    metadatas=[{"page": page + 1, "document": file}],
                    ids=[f"{file}_{page + 1}"]
                )
    
    return chroma_client.list_collections()

if __name__ == "__main__":
    chroma_client, collections = init_chroma()
    print("Collections before init: ", collections)
    collections = init_database(chroma_client)
    print("Collections after init: ", collections)