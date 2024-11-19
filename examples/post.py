import json
import requests


url = "http://127.0.0.1:8080/v1/chat/completions"
headers = {"Content-Type": "application/json"}

data = {
    "model": "gpt-3.5-turbo",
    "messages": [
        {"role": "user", "content": "Did Trump win the 2024 US election?"}
    ],
    "temperature": 0.95,
    "max_tokens": 1024,
    "stream": True
}

chat_response = requests.post(url, json=data, stream=True)
for line in chat_response.iter_lines():
    if line:
        decoded_line = line.decode("utf-8").replace("data: ", "")
        if decoded_line == "[DONE]":
            break
        if decoded_line[:6] == ": ping": # skip ping info
            continue
        chunk = json.loads(decoded_line)
        content = chunk["choices"][0]["delta"].get("content", "")
        print(content, end="", flush=True)
