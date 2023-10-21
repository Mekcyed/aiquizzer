import openai
import os
from flask import jsonify

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