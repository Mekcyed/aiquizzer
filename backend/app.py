import chromadb
from chromadb.config import Settings
from flask import Flask, jsonify, request
from flask_cors import CORS
import openai
import os

app = Flask(__name__)
cors  = CORS(app, origins="*")

chromadb_path = os.environ.get('CHROMADB_PATH', './chromadb/')

def get_chromadb_client(path=chromadb_path):
    try:
        chroma_client = chromadb.PersistentClient(path=path, settings=Settings(allow_reset=True))
        collections = chroma_client.list_collections()
    except Exception as e:
        print(e)
        return None
    
    return chroma_client, collections

def get_chromadb_embeddings(collection, criteria, element):
    try:
        if criteria == "topic":
            embeddings = collection.query(
                query_texts=[element],
                n_results=1,
                )
        elif criteria == "filename": 
            embeddings = collection.get(
            ids = [element],
            )
        else:
            return []
    except Exception as e:
        print(e)
        return None
    
    return embeddings

def get_openai_chat_completion(model, system_prompt, prompt):
    openai.api_key = os.environ.get('OPENAI_API_KEY')  
    try:
        response = openai.ChatCompletion.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
    )
    except Exception as e:
        print(e)
        return None

    return response

def generate_question(embeddings):
    # prompt inspired by https://github.com/quentin-mckay/AI-Quiz-Generator
    prompt = f"""Provide me 1 single multiple-choice question in English based on the following embeddings ignoring footers and headers: {embeddings["documents"]}. The questions should be at a difficult level.
        Return your answer exclusively in the form of a JSON object.
        The JSON object should have a key named 'question' that is an array.
        Each quiz question should contain the choices, the answer, and a brief explanation of why the answer is correct.
        Add nothing else but the JSON.
        The JSON properties of each question should first be 'query' (that is the question), then 'explanation' and 'answer', and lastly 'choices'.
        The choices should not have an ordinal value like A, B, C, D or a number like 1, 2, 3, 4.
        The answer should be the 0-indexed number of the correct choice.
        Verify that the answer is correct by comparing the choices and explanations with the question."""
    system_prompt = 'You\'re a quiz bot generating questions from lecture slide embeddings. The user is a student preparing for an exam using these embeddings'
    response = get_openai_chat_completion('gpt-3.5-turbo-16k', system_prompt, prompt)
    print(response)

    if response is None:
        return jsonify({"response": "Error"})

    response_content = eval(response.choices[0]['message']['content'])
    response_content['embeddings'] = embeddings
    data_dict = {"response": response_content}
    return jsonify(data_dict)

@app.route('/api/get/question/<collection_id>/<criteria>/<element>', methods=['GET'])
def get_question(collection_id, criteria,  element):
    chromadb_client, _ = get_chromadb_client()
    embeddings = get_chromadb_embeddings(chromadb_client.get_collection(collection_id), criteria, element)
    return generate_question(embeddings)

@app.route('/api/get/collections', methods=['GET'])
def get_collections():
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