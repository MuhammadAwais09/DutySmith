import json
import numpy as np
import nltk
import random
import pickle
import matplotlib.pyplot as plt
from datetime import datetime

from nltk.stem import WordNetLemmatizer
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, Input
from tensorflow.keras.optimizers import SGD

# ===================== NLTK SETUP =====================
def download_nltk():
    try:
        nltk.data.find('tokenizers/punkt_tab')
    except LookupError:
        nltk.download('punkt_tab')

    try:
        nltk.data.find('corpora/wordnet')
    except LookupError:
        nltk.download('wordnet')

download_nltk()
lemmatizer = WordNetLemmatizer()

# ===================== TRAINING FUNCTION =====================
def train_model(intents_file='intents.json'):
    # ---------- Load dataset ----------
    with open(intents_file, 'r', encoding='utf-8') as file:
        intents = json.load(file)

    words = []
    classes = []
    documents = []
    ignore_letters = ['!', '?', ',', '.']

    # ---------- Preprocessing ----------
    for intent in intents['intents']:
        for pattern in intent['patterns']:
            tokens = nltk.word_tokenize(pattern)
            words.extend(tokens)
            documents.append((tokens, intent['tag']))
            if intent['tag'] not in classes:
                classes.append(intent['tag'])

    words = sorted(set(
        lemmatizer.lemmatize(w.lower())
        for w in words if w not in ignore_letters
    ))
    classes = sorted(set(classes))

    # Save vocabulary
    pickle.dump(words, open('words.pkl', 'wb'))
    pickle.dump(classes, open('classes.pkl', 'wb'))

    # ---------- Create training data ----------
    training = []
    output_empty = [0] * len(classes)

    for tokens, tag in documents:
        tokens = [lemmatizer.lemmatize(w.lower()) for w in tokens]
        bag = [1 if word in tokens else 0 for word in words]

        output_row = output_empty[:]
        output_row[classes.index(tag)] = 1
        training.append([bag, output_row])

    random.shuffle(training)

    # ✅ FIX: convert explicitly to numeric arrays
    train_x = np.array([item[0] for item in training], dtype=np.float32)
    train_y = np.array([item[1] for item in training], dtype=np.float32)

    # ---------- Build model ----------
    model = Sequential([
        Input(shape=(len(train_x[0]),)),
        Dense(128, activation='relu'),
        Dropout(0.5),
        Dense(64, activation='relu'),
        Dropout(0.5),
        Dense(len(train_y[0]), activation='softmax')
    ])

    optimizer = SGD(
        learning_rate=0.01,
        momentum=0.9,
        nesterov=True
    )

    model.compile(
        loss='categorical_crossentropy',
        optimizer=optimizer,
        metrics=['accuracy']
    )

    # ---------- Train ----------
    history = model.fit(
        train_x,
        train_y,
        epochs=150,
        batch_size=8,
        validation_split=0.1,
        verbose=1
    )

    # ---------- Save model ----------
    model.save('chatbot_model.keras')

    # ---------- Save history ----------
    with open('training_history.json', 'w') as f:
        json.dump(history.history, f, indent=4)

    # ---------- Save report ----------
    with open('training_report.txt', 'w') as f:
        f.write("CHATBOT TRAINING REPORT\n")
        f.write("=======================\n")
        f.write(f"Date: {datetime.now()}\n")
        f.write(f"Epochs: {len(history.history['accuracy'])}\n")
        f.write(f"Final Training Accuracy: {history.history['accuracy'][-1]:.4f}\n")
        f.write(f"Final Validation Accuracy: {history.history['val_accuracy'][-1]:.4f}\n")
        f.write(f"Vocabulary Size: {len(words)}\n")
        f.write(f"Number of Intents: {len(classes)}\n")

    # ---------- Plot graphs ----------
    plt.figure(figsize=(12, 5))

    # Accuracy
    plt.subplot(1, 2, 1)
    plt.plot(history.history['accuracy'], label='Train Accuracy')
    plt.plot(history.history['val_accuracy'], label='Validation Accuracy')
    plt.title('Model Accuracy')
    plt.xlabel('Epoch')
    plt.ylabel('Accuracy')
    plt.legend()

    # Loss
    plt.subplot(1, 2, 2)
    plt.plot(history.history['loss'], label='Train Loss')
    plt.plot(history.history['val_loss'], label='Validation Loss')
    plt.title('Model Loss')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.legend()

    plt.tight_layout()
    plt.savefig('accuracy_loss_plot.png')
    plt.close()

    print("\n✅ Model trained and all outputs saved successfully!")

# ===================== RUN =====================
if __name__ == "__main__":
    train_model()
