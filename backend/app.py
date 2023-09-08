from flask import Flask, jsonify, request
import openai
import os

app = Flask(__name__)

openai.api_key = os.environ.get('OPENAI_API_KEY')

@app.route('/test')
def success():
    return jsonify({"message": " success"})

@app.route('/api/<topic>', methods=['GET'])
def generate_text(topic):
    # prompt inspired by https://github.com/quentin-mckay/AI-Quiz-Generator
    prompt = f"""Gib mir eine Multiple-Choice-Frage zum Thema {topic}. Die Fragen sollten auf einem schwierigen Niveau sein.
        Gib deine Antwort ausschließlich in Form eines JSON-Objekts zurück.
        Das JSON-Objekt sollte einen Schlüssel namens 'questions' haben, der ein Array der Fragen ist.
        Jede Quizfrage sollte die Auswahlmöglichkeiten, die Antwort und eine kurze Erklärung enthalten, warum die Antwort korrekt ist.
        Füge nichts anderes als das JSON hinzu.
        Die JSON-Eigenschaften jeder Frage sollten 'query' (das ist die Frage), 'choices', 'answer' und 'explanation' sein.
        Die Auswahlmöglichkeiten sollten keinen ordinalen Wert wie A, B, C, D oder eine Zahl wie 1, 2, 3, 4 haben.
        Die Antwort sollte die 0-indizierte Nummer der richtigen Auswahl sein."""

    # Generate text using the OpenAI API
    response  = openai.ChatCompletion.create(
        model='gpt-3.5-turbo',
        messages=[
            {"role": "system", "content": "You are a quiz bot"},
            {"role": "user", "content": prompt}
        ]
    )

    # Return the generated text as a JSON response
    print(response)
    return jsonify({"response": response.choices[0]['message']['content']})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)