import chromadb
from chromadb.config import Settings
import os

chromadb_path = os.environ.get('CHROMADB_PATH', './chromadb/')

def get_chromadb_client(path=chromadb_path):
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

def get_chromadb_embeddings(collection, criteria, value):
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
    
    return embeddings