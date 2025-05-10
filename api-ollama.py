import os
import time
import uuid
import requests
from flask import Flask, request, jsonify

DB_FILE = "database.txt"
APIKEYS_FILE = "apikeys.txt"
MODELS_FILE = "models.txt"
OLLAMA_API_KEY = "ollama"
OLLAMA_API_URL = "http://localhost:11434/api/generate"

app = Flask(__name__)

def load_models():
    models = {}
    if os.path.exists(MODELS_FILE):
        with open(MODELS_FILE, "r", encoding="utf-8") as file:
            for line in file.readlines():
                parts = line.strip().split(",", 1)
                if len(parts) == 2:
                    models[parts[0]] = {"ollama_name": parts[0], "system_prompt": parts[1]}
    return models

def load_apikeys():
    apikeys = {}
    if os.path.exists(APIKEYS_FILE):
        with open(APIKEYS_FILE, "r", encoding="utf-8") as file:
            for line in file.readlines():
                parts = line.strip().split(",")
                if len(parts) > 1:
                    apikeys[parts[0]] = set(parts[1:])
    return apikeys

def query_ollama(model_name, prompt, system_prompt):
    payload = {
        "model": model_name,
        "prompt": f"{system_prompt}\n{prompt}",
        "stream": False
    }
    headers = {"Authorization": f"Bearer {OLLAMA_API_KEY}"}
    start_time = time.time()
    response = requests.post(OLLAMA_API_URL, json=payload, headers=headers)
    response.raise_for_status()
    data = response.json()
    end_time = time.time()
    response_time = end_time - start_time
    token_count = len(data["response"].split())
    tokens_per_second = token_count / response_time if response_time > 0 else 0
    return data["response"].strip(), tokens_per_second

def load_database():
    if not os.path.exists(DB_FILE):
        return {}
    with open(DB_FILE, "r", encoding="utf-8") as file:
        lines = file.readlines()
    return dict(line.strip().split("|", 1) for line in lines if "|" in line)

def save_to_database(query, answer):
    with open(DB_FILE, "a", encoding="utf-8") as file:
        file.write(f"{query}|{answer.replace('\n', '\\n')}\n")

def validate_api_key(api_key, model_name, apikeys, models):
    if api_key not in apikeys:
        return False, "Invalid API key"
    allowed_models = apikeys[api_key]
    if model_name not in allowed_models:
        return False, f"Model '{model_name}' not allowed for this API key"
    ollama_model_name = models.get(model_name, {}).get("ollama_name", None)
    if not ollama_model_name:
        return False, f"Something is not right here! '{model_name}'"
    return True, ollama_model_name

def get_answer(model_name, user_message, system_prompt):
    user_message = user_message.replace("\n", "\\n")
    database = load_database()
    start_time = time.time()
    if user_message in database:
        answer = database[user_message].replace("\\n", "\n")
        response_time = time.time() - start_time
        tokens_per_second = len(answer.split()) / response_time if response_time > 0 else 0
        return answer, True, tokens_per_second
    answer, tps = query_ollama(model_name, user_message, system_prompt)
    save_to_database(user_message, answer)
    return answer, False, tps

@app.route("/v1/models", methods=["GET"])
def list_models():
    api_key = request.headers.get("api_key") or (request.headers.get("Authorization") and request.headers["Authorization"].split(" ")[-1])
    if not api_key:
        return jsonify({"error": "API key is required"}), 400
    apikeys = load_apikeys()
    models = load_models()
    if api_key not in apikeys:
        return jsonify({"error": "Invalid API key"}), 403
    allowed_models = apikeys[api_key]
    active_models = [{"id": model_name, "active": model_name in allowed_models} for model_name in models]
    return jsonify({"data": active_models}), 200

@app.route("/v1/completions", methods=["POST"])
def completions():
    api_key = request.headers.get("api_key") or (request.headers.get("Authorization") and request.headers["Authorization"].split(" ")[-1])
    if not api_key:
        return jsonify({"error": "API key is required"}), 400
    data = request.json
    if "model" not in data or "messages" not in data:
        return jsonify({"error": "Missing 'model' or 'messages' in request"}), 400
    model_name = data["model"]
    messages = data["messages"]
    if not isinstance(messages, list) or len(messages) == 0:
        return jsonify({"error": "Invalid 'messages' format"}), 400
    user_message = None
    for message in messages:
        if message["role"] == "user":
            user_message = message["content"]
            break
    if not user_message:
        return jsonify({"error": "Missing 'user' message"}), 400
    models = load_models()
    apikeys = load_apikeys()
    valid, actual_model_name = validate_api_key(api_key, model_name, apikeys, models)
    if not valid:
        return jsonify({"error": actual_model_name}), 403
    if model_name not in models:
        return jsonify({"error": f"Model '{model_name}' not available in models.txt"}), 404
    system_prompt = models[model_name]["system_prompt"]
    answer, cached, tokens_per_second = get_answer(actual_model_name, user_message, system_prompt)
    response_data = {
        "id": str(uuid.uuid4()),
        "object": "chat.completion",
        "created": int(time.time()),
        "model": model_name,
        "choices": [{"text": answer, "index": 0, "logprobs": None, "finish_reason": "stop"}],
        "cached": "yes" if cached else "no",
        "tokens_per_second": tokens_per_second
    }
    return jsonify(response_data)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
