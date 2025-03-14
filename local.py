import os
import time
from groq import Groq

DB_FILE = "database.txt"
API_KEY = "" # Your Groq API Key
MODEL_NAME = "llama-3.3-70b-versatile"

client = Groq(api_key=API_KEY)

def load_database():
    if not os.path.exists(DB_FILE):
        return {}
    with open(DB_FILE, "r", encoding="utf-8") as file:
        lines = file.readlines()
    return dict(line.strip().split("|", 1) for line in lines if "|" in line)

def save_to_database(query, answer):
    with open(DB_FILE, "a", encoding="utf-8") as file:
        file.write(f"{query}|{answer}\n")

def query_groq(query):
    start_time = time.time()
    response = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": query},
        ],
        model=MODEL_NAME,
    )
    end_time = time.time()
    response_time = end_time - start_time
    token_count = len(response.choices[0].message.content.split())
    tokens_per_second = token_count / response_time if response_time > 0 else 0
    print(f"Tokens per second: {tokens_per_second:.2f}")
    return response.choices[0].message.content.strip()

def get_answer(query):
    database = load_database()
    if query in database:
        start_time = time.time()
        answer = database[query]
        end_time = time.time()
        response_time = end_time - start_time
        token_count = len(answer.split())
        tokens_per_second = token_count / response_time if response_time > 0 else 0
        print(f"Tokens per second (cached): {tokens_per_second:.2f}")
        return answer
    
    answer = query_groq(query)
    answer = answer.replace("\n", "\\n")
    save_to_database(query, answer)
    return answer

if __name__ == "__main__":
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            break
        response = get_answer(user_input)
        print("AI:", response.replace("\\n", "\n"))
