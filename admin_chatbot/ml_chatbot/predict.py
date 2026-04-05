# dutysmith_admin/ml_chatbot/predict.py

import json
import pickle
import random
import numpy as np
import nltk
import os
from nltk.stem import WordNetLemmatizer
from tensorflow.keras.models import load_model

# Ensure NLTK data
def setup_nltk():
    try:
        nltk.data.find('tokenizers/punkt_tab')
    except LookupError:
        nltk.download('punkt_tab', quiet=True)
    
    try:
        nltk.data.find('corpora/wordnet')
    except LookupError:
        nltk.download('wordnet', quiet=True)

setup_nltk()

# Setup
lemmatizer = WordNetLemmatizer()
BASE_DIR = os.path.dirname(__file__)

# Load model and data
try:
    model = load_model(os.path.join(BASE_DIR, 'chatbot_model.keras'))
    words = pickle.load(open(os.path.join(BASE_DIR, 'words.pkl'), 'rb'))
    classes = pickle.load(open(os.path.join(BASE_DIR, 'classes.pkl'), 'rb'))
    
    with open(os.path.join(BASE_DIR, 'intents.json'), 'r', encoding='utf-8') as f:
        intents = json.load(f)
    
    print("✅ Chatbot model loaded successfully!")
except Exception as e:
    print(f"⚠️ Warning: Chatbot model not loaded - {e}")
    model = None
    words = []
    classes = []
    intents = {"intents": []}

# NLP Functions
def clean_sentence(sentence):
    """Tokenize and lemmatize input sentence"""
    if not sentence:
        return []
    tokens = nltk.word_tokenize(sentence)
    return [lemmatizer.lemmatize(w.lower()) for w in tokens]

def bag_of_words(sentence):
    """Convert sentence to bag of words vector"""
    sentence_words = clean_sentence(sentence)
    bag = [1 if word in sentence_words else 0 for word in words]
    return np.array(bag, dtype=np.float32)

def predict_intent(sentence, threshold=0.5):
    """Predict intent from user message"""
    if not model:
        return [{"intent": "error", "probability": 0.0}]
    
    bow = bag_of_words(sentence)
    preds = model.predict(np.array([bow]), verbose=0)[0]
    
    results = [
        {"intent": classes[i], "probability": float(preds[i])}
        for i in range(len(preds))
        if preds[i] > threshold
    ]
    
    results.sort(key=lambda x: x["probability"], reverse=True)
    return results if results else [{"intent": "unknown", "probability": 0.0}]

def get_response(intents_list):
    """Get response based on predicted intent"""
    if not intents_list or intents_list[0]["intent"] == "unknown":
        return "Sorry, I didn't understand that. Could you rephrase or ask about duties, leave balance, or attendance?"
    
    tag = intents_list[0]["intent"]
    
    for intent in intents["intents"]:
        if intent["tag"] == tag:
            return random.choice(intent["responses"])
    
    return "I understand your question, but I need more context. Please try again."

def get_chatbot_response(message, user_id=None, firebase_db=None):
    """
    Main function to get chatbot response
    Can fetch personalized data from Firebase if provided
    """
    # Predict intent
    intents_list = predict_intent(message)
    
    if not intents_list:
        return "I'm having trouble understanding. Please try again."
    
    tag = intents_list[0]["intent"]
    response = get_response(intents_list)
    
    # 🔥 Personalize response with Firebase data
    if user_id and firebase_db:
        try:
            if tag == "CheckLeaveBalance":
                user_data = firebase_db.get(f'users/{user_id}')
                if user_data and isinstance(user_data, dict):
                    leave_balance = user_data.get('leaveBalance', 0)
                    response = f"You have {leave_balance} days of leave remaining."
            
            elif tag == "GetDutySchedule":
                from datetime import datetime
                today = datetime.now().strftime('%Y-%m-%d')
                
                duties = firebase_db.get('duties')
                user_duties = []
                
                if duties and isinstance(duties, dict):
                    for duty_id, duty in duties.items():
                        if isinstance(duty, dict) and duty.get('employeeId') == user_id:
                            if duty.get('date') == today:
                                user_duties.append(duty)
                
                if user_duties:
                    duty = user_duties[0]
                    response = f"Your duty today is '{duty.get('title')}' from {duty.get('startTime')} to {duty.get('endTime')} at {duty.get('location', 'Main Branch')}."
                else:
                    response = "You have no duties scheduled for today."
            
            elif tag == "ShowAttendance":
                # Could implement attendance check here
                pass
                
        except Exception as e:
            print(f"Error personalizing response: {e}")
    
    return response