import requests

OLLAMA_HOST = "http://localhost:11434"
OLLAMA_MODEL = "deepseek-r1:8b"

def query_ollama(prompt):
    response = requests.post(
        f"{OLLAMA_HOST}/api/generate",
        json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False}
    )
    return response.json().get("response", "⚠️ Ollama 응답 오류")

response = query_ollama("DeepSeek R1 8B 모델은 어떤 특징을 가지고 있나요?")
print(response)