from abc import ABC, abstractmethod
import os

import requests
from google import genai


class LLMProvider(ABC):
    """Common interface for every LLM provider."""

    @abstractmethod
    def generate(self, prompt: str) -> str:
        raise NotImplementedError


class GeminiProvider(LLMProvider):
    """Hosted Gemini provider."""

    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)

    def generate(self, prompt: str) -> str:
        response = self.client.models.generate_content(
            model="gemini-3.8-flash",
            contents=prompt,
        )
        return response.text or ""


class OllamaProvider(LLMProvider):
    """Local Ollama provider (configured for Qwen 3.5 4B)."""

    def __init__(self, model: str | None = None):
        self.model = model or os.getenv("OLLAMA_MODEL", "qwen3.5:4b")
        self.url = os.getenv(
            "OLLAMA_URL",
            "http://localhost:11434/api/generate",
        )

    def generate(self, prompt: str) -> str:
        try:
            response = requests.post(
                self.url,
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                },
                timeout=180,
            )
            response.raise_for_status()
        except requests.exceptions.ConnectionError as exc:
            raise RuntimeError(
                "Cannot connect to Ollama. Start Ollama and try again."
            ) from exc
        except requests.exceptions.Timeout as exc:
            raise RuntimeError(
                "Ollama took too long to respond. Try a shorter prompt."
            ) from exc
        except requests.exceptions.HTTPError as exc:
            raise RuntimeError(
                f"Ollama returned an error: {response.text}"
            ) from exc

        return response.json().get("response", "")


class LLMClient:
    """Application-facing client; provider can be swapped without changing callers."""

    def __init__(self, provider: LLMProvider):
        self.provider = provider

    def generate(self, prompt: str) -> str:
        return self.provider.generate(prompt)
