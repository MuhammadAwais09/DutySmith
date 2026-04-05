import json
import random

# Define the intents based on the SRS document
intents_config = [
    {
        "tag": "greeting",
        "patterns": [
            "Hi", "Hello", "Hey", "Good morning", "Good afternoon", "Good evening",
            "Is anyone there?", "How are you?", "Greetings", "What's up?",
            "Hi there", "Hello bot", "Hey assistant", "Morning", "Evening"
        ],
        "responses": [
            "Hello! How can I assist you today?",
            "Hi there! I'm your Employee Assistance Chatbot. What can I do for you?",
            "Greetings! How can I help you with your schedule or leave today?",
            "Hello! I'm here to help you with your duty and appointment information."
        ]
    },
    {
        "tag": "goodbye",
        "patterns": [
            "Bye", "Goodbye", "See you later", "I'm done", "Thanks, bye",
            "Talk to you later", "Have a good day", "Catch you later", "Bye bye"
        ],
        "responses": [
            "Goodbye! Have a great day at work.",
            "See you later! Feel free to ask if you need anything else.",
            "Bye! Stay productive!",
            "Have a nice day! I'm here whenever you need assistance."
        ]
    },
    {
        "tag": "thanks",
        "patterns": [
            "Thanks", "Thank you", "That's helpful", "Awesome, thanks",
            "Thanks for the help", "Much appreciated", "You're the best", "Great, thanks"
        ],
        "responses": [
            "You're welcome!", "Happy to help!", "Anytime!", "Glad I could assist you."
        ]
    },
    {
        "tag": "CheckLeaveBalance",
        "patterns": [
            "How many leaves do I have left?", "Check my leave balance", "What is my remaining leave?",
            "Show my leave status", "Can I see my leave balance?", "How much vacation time do I have?",
            "Tell me my remaining leaves", "Leave balance check", "Do I have any leaves left?",
            "I want to know my leave balance", "How many days of leave are remaining?"
        ],
        "responses": [
            "You have {n} days of leave remaining.",
            "Your current leave balance is {n} days.",
            "According to our records, you have {n} leaves left for this period.",
            "You still have {n} days of leave available."
        ]
    },
    {
        "tag": "GetDutySchedule",
        "patterns": [
            "What is my schedule for today?", "Show my duty for tomorrow", "When is my next shift?",
            "What are my appointments for this week?", "Show my duty schedule", "When do I work next?",
            "Tell me my shift timings", "What is my duty for {date}?", "Check my schedule",
            "Am I on duty today?", "What time is my shift starting?", "Give me my duty details"
        ],
        "responses": [
            "Your duty for {date} is from {start} to {end}.",
            "You are scheduled for {description} on {date} at {start}.",
            "Your next shift is on {date}, starting at {start}.",
            "Here is your schedule: {description} from {start} to {end} on {date}."
        ]
    },
    {
        "tag": "ShowAttendance",
        "patterns": [
            "Show my attendance for this month", "Check my attendance record", "Was I marked present yesterday?",
            "Show my attendance status", "How is my attendance looking?", "Check attendance for {date}",
            "Am I present today?", "Show my attendance history", "What is my attendance for last week?",
            "Verify my attendance", "Did I miss any days this month?"
        ],
        "responses": [
            "Your attendance status for {date} is {status}.",
            "On {date}, you were marked as {status}.",
            "Your attendance record shows you were {status} on {date}.",
            "For the requested date {date}, your status is {status}."
        ]
    },
    {
        "tag": "ApplyLeaveInfo",
        "patterns": [
            "How do I apply for leave?", "I want to take a leave", "Can I apply for leave here?",
            "Process for leave application", "Where can I submit a leave request?", "I need a day off",
            "How to request vacation?", "Tell me how to apply for leave", "Leave application process"
        ],
        "responses": [
            "You can apply for leave through the 'Apply for Leave' section in your mobile app.",
            "To apply for leave, please navigate to the leave request form in the app and specify your dates.",
            "You can submit a digital leave application right here in the app. Just go to the Leave menu.",
            "Simply use the 'Apply for Leave' feature in the app to send a request to your administrator."
        ]
    },
    {
        "tag": "Help",
        "patterns": [
            "What can you do?", "Help me", "How to use this chatbot?", "What are your features?",
            "Can you help me with my schedule?", "I need assistance", "Show me what you can do",
            "List of commands", "What information can I get here?"
        ],
        "responses": [
            "I can help you check your duty schedule, leave balance, and attendance records.",
            "You can ask me about your shifts, remaining leaves, or attendance status.",
            "I'm here to assist with your work-related queries. Try asking 'What is my schedule today?' or 'Check my leave balance'.",
            "I can provide instant access to your personalized information like duty timings and leave status."
        ]
    }
]

# Variations for patterns to reach 1k
# We will expand the patterns by adding variations in phrasing, dates, and entities.
dates = ["today", "tomorrow", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday", "next week", "this month", "yesterday"]
departments = ["HR", "IT", "Sales", "Marketing", "Operations", "Finance"]
leave_types = ["sick leave", "casual leave", "vacation", "emergency leave", "maternity leave", "paternity leave"]

def generate_dataset(target_count=1000):
    dataset = []
    
    # First, add the base intents
    for config in intents_config:
        intent = {
            "tag": config["tag"],
            "patterns": list(config["patterns"]),
            "responses": list(config["responses"])
        }
        dataset.append(intent)

    # Now, expand patterns to reach roughly 1000 total patterns across all intents
    # We'll distribute the 1000 patterns among the intents
    patterns_per_intent = target_count // len(intents_config)
    
    for intent in dataset:
        current_patterns = intent["patterns"]
        tag = intent["tag"]
        
        while len(current_patterns) < patterns_per_intent:
            base_pattern = random.choice(current_patterns)
            
            # Apply variations
            new_pattern = base_pattern
            
            # Replace/Add date variations
            if "{date}" in new_pattern:
                new_pattern = new_pattern.replace("{date}", random.choice(dates))
            elif any(d in new_pattern.lower() for d in ["today", "tomorrow", "yesterday"]):
                for d in ["today", "tomorrow", "yesterday"]:
                    if d in new_pattern.lower():
                        new_pattern = new_pattern.lower().replace(d, random.choice(dates))
            
            # Add polite words
            polite_prefix = random.choice(["Please ", "Can you ", "Could you ", "Kindly ", "I would like to ", ""])
            if not new_pattern.startswith(polite_prefix):
                new_pattern = polite_prefix + new_pattern
            
            # Add question marks or periods
            if not new_pattern.endswith("?") and not new_pattern.endswith("."):
                new_pattern += random.choice(["?", ".", "!", ""])
            
            # Avoid duplicates
            if new_pattern not in current_patterns:
                current_patterns.append(new_pattern)
                
    return {"intents": dataset}

# Generate and save
final_data = generate_dataset(1000)

# Verify count
total_patterns = sum(len(i["patterns"]) for i in final_data["intents"])
print(f"Total patterns generated: {total_patterns}")

with open('/home/ubuntu/intents.json', 'w') as f:
    json.dump(final_data, f, indent=4)
