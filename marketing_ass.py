import os
from dotenv import load_dotenv
import sqlite3
from datetime import datetime
from openai import OpenAI

# Load environment variables
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI()

# Initialize conversation history
conversation_history = [
    {
        "role": "system",
        "content": "You are a digital marketing expert for a B2B SaaS AI company that specializes in inventory and merchandising solutions."
    }
]

# Function to get assistant response
def get_assistant_response(user_input):
    # Append user message to conversation history
    conversation_history.append({
        "role": "user",
        "content": user_input
    })
    
    # Create a chat completion request
    completion = client.chat.completions.create(
        model="gpt-4",
        messages=conversation_history
    )
    
    # Extract assistant's response
    assistant_message = completion.choices[0].message.content
    
    # Append assistant message to conversation history
    conversation_history.append({
        "role": "assistant",
        "content": assistant_message
    })
    
    # Print the assistant's response to the terminal
    print(f"Assistant: {assistant_message}")
    
    return assistant_message

# Function to save new conversation history to the database
def save_to_database(prompts, conversation_id, db_path="ass.db"):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Create table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS prompts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id TEXT,
                timestamp DATETIME,
                role TEXT,
                content TEXT,
                UNIQUE(conversation_id, role, content)
            )
        ''')

        # Insert only new data
        for prompt in prompts:
            try:
                cursor.execute('''
                    INSERT OR IGNORE INTO prompts (conversation_id, timestamp, role, content)
                    VALUES (?, ?, ?, ?)
                ''', (
                    conversation_id,
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    prompt["role"],
                    prompt["content"]
                ))
            except sqlite3.IntegrityError:
                # Skip duplicate entries
                pass

        conn.commit()
        conn.close()
        print(f"Conversation history saved to {db_path}")
    except Exception as e:
        print(f"Error saving to database: {e}")

# Main function
if __name__ == "__main__":
    # Generate a unique conversation ID
    conversation_id = f"conv_{datetime.now().strftime('%Y%m%d%H%M%S')}"

    # Prompt the user for input
    user_question = input("You: ")
    assistant_message = get_assistant_response(user_question)

    # Save only new conversation history
    save_to_database(conversation_history, conversation_id)