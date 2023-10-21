from flask import Flask, jsonify, request
from flask_cors import CORS
from chromadb_handler import get_chromadb_client, get_chromadb_embeddings
from question_generator import generate_question

app = Flask(__name__)
cors  = CORS(app, origins="*")

@app.route('/api/get/question/<collection_id>/<criteria>/<value>', methods=['GET'])
def get_question(collection_id, criteria, value):
    """
    Generates a question based on the given collection ID, criteria, and value.
    """
    chromadb_client, _ = get_chromadb_client()
    embeddings = get_chromadb_embeddings(chromadb_client.get_collection(collection_id), criteria, value)
    return generate_question(embeddings)

@app.route('/api/get/collections', methods=['GET'])
def get_collections():
    """
    Returns a list of collections in chromadb and their documents.
    """
    _ , collections = get_chromadb_client()
    data = {"collections": {c.name: {} for c in collections}}
    for collection in collections:
        documents = collection.get(
            include= [ "metadatas" ]
        )
        data['collections'][collection.name] = documents
        distinct_filenames = set(
            document['document']
            for document in (data['collections'][collection.name].get('metadatas') or [])
        )
        data['collections'][collection.name]['filenames'] = list(distinct_filenames)

    return jsonify(data)

@app.route('/test')
def success():
    return jsonify({"message": " success"})

if __name__ == '__main__':
    from waitress import serve
    serve(app,host='0.0.0.0', port=5000)