"""
Enhanced Chatbot Training Script for Duty Smith
Includes employee-specific intents
"""

import json
import numpy as np
import nltk
import random
import pickle
import matplotlib.pyplot as plt
from datetime import datetime

from nltk.stem import WordNetLemmatizer
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, Input, BatchNormalization
from tensorflow.keras.optimizers import SGD
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau

# ===================== NLTK SETUP =====================
def download_nltk():
    try:
        nltk.data.find('tokenizers/punkt_tab')
    except LookupError:
        nltk.download('punkt_tab', quiet=True)

    try:
        nltk.data.find('corpora/wordnet')
    except LookupError:
        nltk.download('wordnet', quiet=True)

download_nltk()
lemmatizer = WordNetLemmatizer()

# ===================== ENHANCED INTENTS =====================
DEFAULT_INTENTS = {
    "intents": [
        {
            "tag": "greeting",
            "patterns": ["Hi", "Hello", "Hey", "Good morning", "Good afternoon", "Good evening", "Howdy", "Hi there"],
            "responses": ["Hello! How can I assist you today?", "Hi there! What can I help you with?", "Hey! Ready to help you with employee data."]
        },
        {
            "tag": "goodbye",
            "patterns": ["Bye", "Goodbye", "See you", "See you later", "Thanks bye", "That's all", "Exit", "Quit"],
            "responses": ["Goodbye! Have a great day!", "See you later! Let me know if you need anything else.", "Bye! Feel free to come back anytime."]
        },
        {
            "tag": "thanks",
            "patterns": ["Thanks", "Thank you", "That's helpful", "Thanks a lot", "Appreciate it", "Great help"],
            "responses": ["You're welcome!", "Happy to help!", "Anytime! Let me know if you need more info.", "Glad I could assist!"]
        },
        {
            "tag": "help",
            "patterns": ["Help", "What can you do", "What do you know", "How do you work", "Features", "Capabilities", "Commands"],
            "responses": ["I can help you with:\n• Employee leave balances\n• Duty schedules\n• Attendance reports\n• Performance summaries\n• Contact information\n\nJust select an employee or type their name!"]
        },
        {
            "tag": "CheckLeaveBalance",
            "patterns": [
                "What is my leave balance", "How many leaves do I have", "Leave balance", 
                "Check my leave", "Remaining leaves", "Vacation days left", "How many days off do I have",
                "Show leave balance", "Tell me my leave", "Leave days remaining"
            ],
            "responses": ["I'll check the leave balance for you.", "Let me pull up the leave information."]
        },
        {
            "tag": "GetDutySchedule",
            "patterns": [
                "What is my duty today", "Show my duties", "Duty schedule", "What am I assigned to",
                "My shifts", "Work schedule", "What do I have to do today", "Upcoming duties",
                "Tell me my duties", "What tasks are assigned to me", "My assignments"
            ],
            "responses": ["Let me check the duty schedule.", "I'll pull up the assigned duties."]
        },
        {
            "tag": "ShowAttendance",
            "patterns": [
                "Show my attendance", "My attendance record", "How is my attendance", 
                "Attendance report", "Am I present regularly", "Check my attendance",
                "Attendance stats", "My punctuality", "Show attendance summary"
            ],
            "responses": ["I'll generate the attendance report.", "Let me check the attendance records."]
        },
        {
            "tag": "EmployeeInfo",
            "patterns": [
                "Show employee info", "Employee details", "Contact information", 
                "Department info", "Employee profile", "Who is this employee", "Tell me about",
                "Employee data", "Staff information", "Worker details"
            ],
            "responses": ["I'll fetch the employee information.", "Let me pull up the employee profile."]
        },
        {
            "tag": "PerformanceSummary",
            "patterns": [
                "Performance report", "How is the performance", "Employee performance", 
                "Work summary", "Performance stats", "Analytics", "Productivity report",
                "Overall performance", "Performance review", "Work statistics"
            ],
            "responses": ["I'll generate a comprehensive performance summary.", "Let me analyze the performance metrics."]
        },
        {
            "tag": "ListEmployees",
            "patterns": [
                "Show all employees", "List employees", "Who works here", "Employee list",
                "Staff directory", "Show me the team", "All workers", "Employee roster"
            ],
            "responses": ["Here are all the employees in the system.", "Let me show you the employee directory."]
        },
        {
            "tag": "fallback",
            "patterns": [],
            "responses": ["I'm not sure I understand. Try asking about leaves, duties, attendance, or employee info."]
        }
    ]
}

def train_model(intents_file=None, epochs=200, batch_size=8):
    """
    Train the chatbot model
    
    Args:
        intents_file: Path to intents.json (uses DEFAULT_INTENTS if None)
        epochs: Number of training epochs
        batch_size: Batch size for training
    """
    # Load or use default intents
    if intents_file:
        with open(intents_file, 'r', encoding='utf-8') as f:
            intents = json.load(f)
    else:
        intents = DEFAULT_INTENTS
        # Save default intents
        with open('intents.json', 'w', encoding='utf-8') as f:
            json.dump(intents, f, indent=4)
    
    words = []
    classes = []
    documents = []
    ignore_letters = ['!', '?', ',', '.', "'"]

    # ---------- Preprocessing ----------
    print("🔍 Preprocessing data...")
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

    print(f"📊 Vocabulary size: {len(words)}")
    print(f"📊 Number of intents: {len(classes)}")

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

    train_x = np.array([item[0] for item in training], dtype=np.float32)
    train_y = np.array([item[1] for item in training], dtype=np.float32)

    # ---------- Build enhanced model ----------
    print("🏗️  Building model...")
    model = Sequential([
        Input(shape=(len(train_x[0]),)),
        Dense(128, activation='relu'),
        BatchNormalization(),
        Dropout(0.5),
        Dense(64, activation='relu'),
        BatchNormalization(),
        Dropout(0.5),
        Dense(32, activation='relu'),
        Dropout(0.3),
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

    # ---------- Callbacks ----------
    early_stop = EarlyStopping(
        monitor='val_loss',
        patience=20,
        restore_best_weights=True,
        verbose=1
    )
    
    reduce_lr = ReduceLROnPlateau(
        monitor='val_loss',
        factor=0.5,
        patience=10,
        min_lr=0.0001,
        verbose=1
    )

    # ---------- Train ----------
    print(f"🚀 Training for up to {epochs} epochs...")
    history = model.fit(
        train_x,
        train_y,
        epochs=epochs,
        batch_size=batch_size,
        validation_split=0.1,
        callbacks=[early_stop, reduce_lr],
        verbose=1
    )

    # ---------- Save model ----------
    model.save('chatbot_model.keras')
    print("💾 Model saved as 'chatbot_model.keras'")

    # ---------- Save history ----------
    with open('training_history.json', 'w') as f:
        json.dump(history.history, f, indent=4)

    # ---------- Generate report ----------
    generate_report(history, words, classes, len(documents))
    
    # ---------- Plot graphs ----------
    plot_training_graphs(history)

    print("\n✅ Training complete! All files saved.")
    return model, history

def generate_report(history, words, classes, num_patterns):
    """Generate training report"""
    final_acc = history.history['accuracy'][-1]
    final_val_acc = history.history['val_accuracy'][-1]
    final_loss = history.history['loss'][-1]
    final_val_loss = history.history['val_loss'][-1]
    
    report = f"""
DUTY SMITH CHATBOT TRAINING REPORT
{'='*50}
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'='*50}

MODEL ARCHITECTURE:
- Input Layer: {len(words)} neurons (vocabulary size)
- Hidden Layer 1: 128 neurons (ReLU) + BatchNorm + Dropout(0.5)
- Hidden Layer 2: 64 neurons (ReLU) + BatchNorm + Dropout(0.5)
- Hidden Layer 3: 32 neurons (ReLU) + Dropout(0.3)
- Output Layer: {len(classes)} neurons (Softmax)

TRAINING PARAMETERS:
- Epochs: {len(history.history['accuracy'])}
- Batch Size: 8
- Optimizer: SGD (lr=0.01, momentum=0.9, nesterov=True)
- Loss: Categorical Crossentropy

DATASET:
- Total Patterns: {num_patterns}
- Vocabulary Size: {len(words)}
- Number of Intents: {len(classes)}

FINAL METRICS:
- Training Accuracy: {final_acc:.4f} ({final_acc*100:.2f}%)
- Validation Accuracy: {final_val_acc:.4f} ({final_val_acc*100:.2f}%)
- Training Loss: {final_loss:.4f}
- Validation Loss: {final_val_loss:.4f}

INTENTS COVERED:
{chr(10).join(f'  • {cls}' for cls in classes)}

FILES GENERATED:
  • chatbot_model.keras (model weights)
  • words.pkl (vocabulary)
  • classes.pkl (intent classes)
  • intents.json (training data)
  • training_history.json (metrics)
  • training_report.txt (this report)
  • accuracy_loss_plot.png (visualization)
{'='*50}
"""
    
    with open('training_report.txt', 'w') as f:
        f.write(report)
    
    print(report)

def plot_training_graphs(history):
    """Plot and save training graphs"""
    plt.figure(figsize=(15, 5))
    
    # Accuracy
    plt.subplot(1, 3, 1)
    plt.plot(history.history['accuracy'], label='Train', linewidth=2)
    plt.plot(history.history['val_accuracy'], label='Validation', linewidth=2)
    plt.title('Model Accuracy', fontsize=12, fontweight='bold')
    plt.xlabel('Epoch')
    plt.ylabel('Accuracy')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Loss
    plt.subplot(1, 3, 2)
    plt.plot(history.history['loss'], label='Train', linewidth=2)
    plt.plot(history.history['val_loss'], label='Validation', linewidth=2)
    plt.title('Model Loss', fontsize=12, fontweight='bold')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Learning Rate (if available)
    if 'lr' in history.history:
        plt.subplot(1, 3, 3)
        plt.plot(history.history['lr'], linewidth=2, color='green')
        plt.title('Learning Rate', fontsize=12, fontweight='bold')
        plt.xlabel('Epoch')
        plt.ylabel('LR')
        plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('accuracy_loss_plot.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("📊 Training graphs saved as 'accuracy_loss_plot.png'")

# ===================== RUN =====================
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Train Duty Smith Chatbot')
    parser.add_argument('--intents', '-i', help='Path to intents.json file')
    parser.add_argument('--epochs', '-e', type=int, default=200, help='Number of epochs')
    parser.add_argument('--batch-size', '-b', type=int, default=8, help='Batch size')
    
    args = parser.parse_args()
    
    print("\n" + "="*60)
    print("🤖 DUTY SMITH CHATBOT TRAINING")
    print("="*60 + "\n")
    
    train_model(
        intents_file=args.intents,
        epochs=args.epochs,
        batch_size=args.batch_size
    )