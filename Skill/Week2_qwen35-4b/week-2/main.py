import os

from dotenv import load_dotenv

from llm_client import GeminiProvider, LLMClient, OllamaProvider


def main():
    load_dotenv()

    provider_name = input(
        "Choose provider (ollama/gemini) [ollama]: "
    ).strip().lower() or "ollama"

    if provider_name == "ollama":
        model = os.getenv("OLLAMA_MODEL", "qwen3.5:4b")
        provider = OllamaProvider(model)
        print(f"Using local Ollama model: {model}")

    elif provider_name == "gemini":
        api_key = os.getenv("GEMINI_API_KEY", "").strip()
        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY is missing. Add your key to the .env file."
            )
        provider = GeminiProvider(api_key)

    else:
        raise ValueError("Invalid provider. Enter 'ollama' or 'gemini'.")

    client = LLMClient(provider)
    prompt = input("\nEnter your question: ").strip()

    if not prompt:
        raise ValueError("The prompt cannot be empty.")

    answer = client.generate(prompt)
    print("\nLLM Response:\n")
    print(answer)


if __name__ == "__main__":
    try:
        main()
    except (ValueError, RuntimeError) as error:
        print(f"\nError: {error}")
