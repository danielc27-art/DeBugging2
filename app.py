from flask import Flask, render_template, jsonify, request, Response, stream_with_context
import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel
from typing import List

load_dotenv()

# create OpenAI client after environment is loaded
client = OpenAI()

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/counter")
def counter():
    return render_template("counter.html")

@app.route("/todo")
def todo():
    return render_template("todo.html")

@app.route("/quotes")
def quotes():
    return render_template("quotes.html")

@app.route("/quiz")
def quiz():
    return render_template("quiz.html")

@app.route("/flashcards")
def flashcards():
    return render_template("flashcards.html")

@app.route("/chat")
def chat():
    return render_template("chat.html")

@app.route("/question-data")
def question_data():
    
    class QuizQuestions(BaseModel):
        question: str
        options: List[str]
        correct: int

    response = client.responses.parse(
        model="gpt-4o-2024-08-06",
        input=[
            {"role": "system", "content": "Create exactly 3 multiple choice quiz questions on a topic of the user's choice."},
            {"role": "user", "content": "The topic is science."},
        ],
        text_format=QuizQuestions,
    )
    
    text = response.output_text
    questions = []
    depth = 0
    start = 0
    for i in range(len(text)):
        if text[i] == '{':
            if depth == 0:
                start = i
            depth += 1
        elif text[i] == '}':
            depth -= 1
            if depth == 0:
                questions.append(json.loads(text[start:i+1]))
    
    return jsonify(questions)

@app.route("/flashcard-data")
def flashcard_data():
    
    class Flashcard(BaseModel):
        word: str
        definition: str

    response = client.responses.parse(
        model="gpt-4o-2024-08-06",
        input=[
            {"role": "system", "content": "Create exactly 3 vocabulary flashcards with a word and its definition."},
            {"role": "user", "content": "Create vocabulary flashcards for Latin verbs."},
        ],
        text_format=Flashcard,
    )
    
    text = response.output_text
    flashcards = []
    depth = 0
    start = 0
    for i in range(len(text)):
        if text[i] == '{':
            if depth == 0:
                start = i
            depth += 1
        elif text[i] == '}':
            depth -= 1
            if depth == 0:
                flashcards.append(json.loads(text[start:i+1]))
    
    return jsonify(flashcards)





@app.route("/chat-stream", methods=["POST"])
def chat_stream():
    data = request.json or {}
    conversation = data.get("conversation", [])

    # Convert conversation to a list of messages for chat.completions API
    messages = []
    for msg in conversation:
        messages.append({
            "role": msg["role"],
            "content": msg["content"]
        })

    stream = client.chat.completions.create(
        model="gpt-4",  
        messages=messages,
        stream=True,
    )

    def generate():
        for chunk in stream:
            # Check if there's content in this chunk
            if chunk.choices[0].delta.content is not None:
                content = chunk.choices[0].delta.content
                yield f"data: {content}\n\n"

        yield "data: [DONE]\n\n"

    return Response(
        stream_with_context(generate()),
        content_type="text/event-stream",
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no'
        }
    )


if __name__ == "__main__":
    app.run(debug=True, port=8001)