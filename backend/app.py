from flask import Flask, jsonify, request
from flask_cors import CORS
from chromadb_handler import chromadb_get_client, chromadb_get_embeddings, chromadb_import_pdf_data
from loguru import logger
from question_generator import generate_question

app = Flask(__name__)
cors  = CORS(app, origins="*")
logger.add("./logs/backend.log", rotation="250 MB")

@app.errorhandler(Exception)
def handle_exception(e):
    logger.exception(e)
    return f"Internal server error: {e} ", 500

@app.route('/api/get/question/<question_quantity>/<collection_id>/<criteria>/<value>', methods=['GET'])
def get_question(question_quantity, collection_id, criteria, value):
    """
    Generates n questions based on the given question_quantity, collection ID, criteria, and value.
    """
    chromadb_client, _ = chromadb_get_client()
    embeddings = chromadb_get_embeddings(chromadb_client.get_collection(collection_id), criteria, value)
    return generate_question(question_quantity, embeddings)

@app.route('/api/get/collections', methods=['GET'])
def get_collections():
    """
    Returns a list of collections in chromadb and their documents.
    """
    _ , collections = chromadb_get_client()
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

@app.route('/api/update/database')
def update_chromadb():
    """
    Updates chromadb with the documents in the docs/ directory.
    """
    chromadb_client, _ = chromadb_get_client()
    chromadb_import_pdf_data(chromadb_client)
    response = jsonify({"message": " chromadb updated"})
    logger.debug(response)
    return response


@app.route('/test')
def success():
    response = jsonify({"message": " success"})
    logger.debug(response)
    return response

if __name__ == '__main__':
    from waitress import serve 
    serve(app,host='0.0.0.0', port=5000)
    #app.run(host='0.0.0.0', port=5000)

