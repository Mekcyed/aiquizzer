import chromadb
from chromadb.config import Settings
from loguru import logger
import os
from pypdf import PdfReader

chromadb_path = os.environ.get('CHROMADB_PATH', './chromadb/')

@logger.catch
def chromadb_get_client(path = chromadb_path):
    """
    Returns a chromadb client and a list of collections.
    """
    try:
        chroma_client = chromadb.PersistentClient(path=path, settings=Settings(allow_reset=True))
        collections = chroma_client.list_collections()
    except Exception as e:
        print(e)
        return None
    
    return chroma_client, collections

@logger.catch
def chromadb_get_embeddings(collection, criteria, value):
    """
    Returns a list of embeddings from a collection.
    args:
        collection: a chromadb collection object
        criteria: either "topic" or "filename"
        value: the value of the criteria
    returns:
        a list of embeddings
    """
    try:
        if criteria == "topic":
            embeddings = collection.query(
                query_texts=[value],
                n_results=1,
                )
        elif criteria == "filename": 
            embeddings = collection.get(
            ids = [value],
            )
        else:
            return []
    except Exception as e:
        print(e)
        return None
    
    logger.debug(f"{collection=}, {criteria=}, {value=}, {embeddings=}")
    return embeddings

@logger.catch
def chromadb_import_pdf_data(chroma_client):
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