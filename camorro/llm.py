import os
import requests


class LLMClient:
    """يتصل بـ Ollama (محلي) أو أي خادم متوافق مع OpenAI API"""

    def __init__(self, base_url=None, model=None, api_key=None):
        self.base_url = base_url or os.getenv("CAMORRO_LLM_URL", "http://localhost:11434")
        self.model = model or os.getenv("CAMORRO_MODEL", "qwen2.5:14b")
        self.api_key = api_key or os.getenv("CAMORRO_API_KEY", "")
        self.is_ollama = "11434" in self.base_url or "ollama" in self.base_url

    def chat(self, messages, tools=None):
        if self.is_ollama:
            return self._ollama_chat(messages, tools)
        return self._openai_chat(messages, tools)

    def _ollama_chat(self, messages, tools):
        payload = {"model": self.model, "messages": messages, "stream": False}
        if tools:
            payload["tools"] = tools
        r = requests.post(f"{self.base_url}/api/chat", json=payload, timeout=600)
        r.raise_for_status()
        return r.json()

    def _openai_chat(self, messages, tools):
        payload = {"model": self.model, "messages": messages, "stream": False}
        if tools:
            payload["tools"] = tools
        headers = {"Authorization": f"Bearer {self.api_key}"}
        url = self.base_url.rstrip("/") + "/chat/completions"
        r = requests.post(url, json=payload, headers=headers, timeout=600)
        r.raise_for_status()
        data = r.json()
        msg = data["choices"][0]["message"]
        return {
            "message": {
                "role": "assistant",
                "content": msg.get("content") or "",
                "tool_calls": [
                    {"function": {"name": tc["function"]["name"],
                                  "arguments": tc["function"]["arguments"]}}
                    for tc in msg.get("tool_calls", [])
                ] or None,
            }
      }
