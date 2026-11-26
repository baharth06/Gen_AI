import unittest
from unittest.mock import Mock, patch

from llm_client import LLMClient, OllamaProvider


class FakeProvider:
    def generate(self, prompt):
        return "AI stands for Artificial Intelligence."


class TestLLMClient(unittest.TestCase):
    def test_generate_uses_provider(self):
        client = LLMClient(FakeProvider())
        result = client.generate("Explain AI")
        self.assertEqual(
            result,
            "AI stands for Artificial Intelligence.",
        )

    @patch("llm_client.requests.post")
    def test_ollama_sends_prompt_and_model(self, mock_post):
        mock_response = Mock()
        mock_response.json.return_value = {"response": "Hello from Qwen"}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        provider = OllamaProvider("qwen3.5:4b")
        result = provider.generate("Say hello")

        self.assertEqual(result, "Hello from Qwen")
        mock_post.assert_called_once()
        call_kwargs = mock_post.call_args.kwargs
        self.assertEqual(call_kwargs["json"]["model"], "qwen3.5:4b")
        self.assertEqual(call_kwargs["json"]["prompt"], "Say hello")


if __name__ == "__main__":
    unittest.main()
