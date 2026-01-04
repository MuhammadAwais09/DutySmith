import json
import pickle
import random
import numpy as np
import nltk

from flask import Flask, request, jsonify, render_template_string
from nltk.stem import WordNetLemmatizer
from tensorflow.keras.models import load_model

# ===================== SETUP =====================
app = Flask(__name__)

lemmatizer = WordNetLemmatizer()

# Ensure NLTK data exists
try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    nltk.download('punkt_tab')

try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet')

# Load trained assets
model = load_model('chatbot_model.keras')
words = pickle.load(open('words.pkl', 'rb'))
classes = pickle.load(open('classes.pkl', 'rb'))

with open('intents.json', 'r', encoding='utf-8') as f:
    intents = json.load(f)

# ===================== NLP FUNCTIONS =====================
def clean_sentence(sentence):
    tokens = nltk.word_tokenize(sentence)
    return [lemmatizer.lemmatize(w.lower()) for w in tokens]

def bag_of_words(sentence):
    sentence_words = clean_sentence(sentence)
    bag = [1 if word in sentence_words else 0 for word in words]
    return np.array(bag, dtype=np.float32)

def predict_intent(sentence, threshold=0.5):
    bow = bag_of_words(sentence)
    preds = model.predict(np.array([bow]), verbose=0)[0]

    results = [
        {"intent": classes[i], "probability": float(preds[i])}
        for i in range(len(preds))
        if preds[i] > threshold
    ]

    results.sort(key=lambda x: x["probability"], reverse=True)
    return results

def get_response(intents_list):
    if not intents_list:
        return "Sorry, I didn't understand that. Could you rephrase?"

    tag = intents_list[0]["intent"]

    for intent in intents["intents"]:
        if intent["tag"] == tag:
            return random.choice(intent["responses"])

    return "Sorry, something went wrong."

# ===================== ROUTES =====================
@app.route("/", methods=["GET"])
def home():
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Chatbot Test</title>
        <style>
            body { font-family: Arial; margin: 40px; }
            input { width: 80%; padding: 10px; }
            button { padding: 10px; }
            #chat { margin-top: 20px; }
        </style>
    </head>
    <body>
        <h2>Chatbot Tester</h2>
        <input id="msg" placeholder="Type a message..." />
        <button onclick="send()">Send</button>
        <div id="chat"></div>

        <script>
            function send() {
                const msg = document.getElementById("msg").value;
                fetch("/chat", {
                    method: "POST",
                    headers: {"Content-Type": "application/json"},
                    body: JSON.stringify({message: msg})
                })
                .then(res => res.json())
                .then(data => {
                    document.getElementById("chat").innerHTML +=
                        "<p><b>You:</b> " + msg + "</p>" +
                        "<p><b>Bot:</b> " + data.response + "</p>";
                    document.getElementById("msg").value = "";
                });
            }
        </script>
    </body>
    </html>
    """)

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    message = data.get("message", "")

    intents_list = predict_intent(message)
    response = get_response(intents_list)

    return jsonify({
        "message": message,
        "response": response,
        "intents": intents_list
    })

# ===================== RUN =====================
if __name__ == "__main__":
    app.run(debug=True)
