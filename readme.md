Here's the updated `README.md` with some fun emojis added to make it more engaging:

```markdown
# AICache 🚀

AICache is a caching solution for AI model responses, allowing you to speed up response times by caching frequently used queries. This project consists of a set of Python scripts for handling interactions with AI models, saving responses in a local database, and exposing a REST API for querying cached responses.

## Features 🌟
- **AI model query interface**: Interact with different AI models and get responses. 🤖
- **Caching**: Cache AI responses to speed up future queries. ⚡
- **Token efficiency**: Track and display tokens-per-second (TPS) for API interactions. 💨
- **API Server**: Expose AI queries and caching functionalities via a REST API. 🌐
- **Discord bot integration**: Use the AICache system directly in Discord with a bot that queries the API. 💬

## Requirements 🛠️
- Python 3.7+
- Required libraries:
  - `discord.py`
  - `requests`
  - `flask`
  - `groq`
  - `python-dotenv`

## Setup (For discord bot) ⚙️

### 1. Install Dependencies
First, make sure to install the required dependencies by running:

```bash
pip install -r requirements.txt
```

### 2. Set Up Environment Variables 🌿
Create a `.env` file in the root of the project directory and add your credentials:

```dotenv
DISCORD_TOKEN=your-discord-bot-token
API_KEY=your-aicache-api-key
```

### 3. Configure API Keys and Models 🔑
- Add your API keys to the `APIKEYS.txt` file.
- Define available models in `models.txt` (e.g., `llama-3.3-70b-versatile`, `qwen-qwq-32b`).

### 4. Run the API Server 🚀
To start the API server, run:

```bash
python3 api.py
```

This will start a Flask server that listens on `localhost:5000` by default. 🌍

### 5. Run the Discord Bot 🤖
To start the Discord bot, run:

```bash
python3 openchatbot.py
```

This bot will listen for messages in the configured channel and send AI model responses.

### Local Mode (Command Line Interface) 💻
You can also query the AI models directly from the command line using `local.py`. Run the script:

```bash
python3 local.py
```

Enter your queries, and the AI will respond. You can exit by doing ctrl + c

## File Descriptions 📂

- **openchatbot.py**: Discord bot script that listens for messages and queries the AICache API for responses.
- **models.txt**: Contains a list of AI models and their configurations.
- **local.py**: Command line tool to interact with the AI models and the AICache database directly.
- **apikeys.txt**: A list of valid API keys with access to different models.
- **api.py**: Flask server exposing a REST API for interacting with the AICache system.
- **database.txt**: A local database for storing cached query results.

## Benchmark 📊

The benchmark results for AICache's token speed:

Lowest/Avg/Highest
- **Cached**: 99999/100,000/605,000 TPS (Depends on your storage) 😎
- **Non-Cached**: 99/200/450 TPS ⚡

**TPS (Tokens per Second)**

## Troubleshooting 🔧

- **Error: Invalid API Key**  
Ensure that your API key is correctly set in the `apikeys.txt` file.

- **Error: Model not available**  
Ensure that the model is correctly defined in the `models.txt` file and the associated Groq model is accessible.

## API Example using curl 👍
```
curl -X POST http://localhost:5000/v1/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {APIKEY}" \
  -d '{
    "model": "llama-3.3-70b-versatile",
    "messages": [
      {"role": "system", "content": "You are a helpful assistant."},
      {"role": "user", "content": "Write me a scary story about computers"}
    ]
  }'
```
Output (Non-cached)
```
{
  "cached": "no",
  "choices": [
    {
      "finish_reason": "stop",
      "index": 0,
      "logprobs": null,
      "text": "I logged in, and the screen flickered: \"I am your system now.\""
    }
  ],
  "created": 1741942075,
  "id": "54451171-d68f-4567-90c8-de9c7ac4c3f3",
  "model": "llama-3.3-70b-versatile",
  "object": "chat.completion",
  "tokens_per_second": 72.9844001496472
}
```
Output (cached)
```
{
  "cached": "yes",
  "choices": [
    {
      "finish_reason": "stop",
      "index": 0,
      "logprobs": null,
      "text": "I logged in, and the screen flickered: \"I am your system now.\""
    }
  ],
  "created": 1741942104,
  "id": "a251729a-8885-445a-9065-88b8fd80751f",
  "model": "llama-3.3-70b-versatile",
  "object": "chat.completion",
  "tokens_per_second": 12582912.0
}
```

## License 📜

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details. 📝
