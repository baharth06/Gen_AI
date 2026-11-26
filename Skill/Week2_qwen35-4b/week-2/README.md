# Week 2 — Provider-Agnostic LLM Client

This project uses one `LLMClient` interface with two interchangeable providers:

- **Ollama (local):** configured for `qwen3.5:4b` on your Lenovo.
- **Gemini (hosted):** optional; requires your own Gemini API key in `.env`.

## 1. Requirements

- Windows
- Python 3.10+
- VS Code
- Ollama installed and running
- The Ollama model `qwen3.5:4b` already downloaded

Check the model in PowerShell:

```powershell
ollama list
```

If the exact model tag is not listed, check the tag shown by that command and set
`OLLAMA_MODEL` in `.env` to match it.

## 2. Open this folder in VS Code

Open this `week-2` folder in VS Code, then open Terminal > New Terminal.

## 3. Create and activate a virtual environment

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, run this once in that terminal:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.venv\Scripts\Activate.ps1
```

## 4. Install dependencies

```powershell
python -m pip install -r requirements.txt
```

## 5. Run with local Qwen

Make sure the Ollama desktop app is running. Then:

```powershell
ollama list
python main.py
```

At the provider prompt, enter `ollama` (or press Enter for the default).
Enter your question when prompted.

No Gemini API key or internet connection is needed for the local Ollama option.

## 6. Run tests

```powershell
python -m pytest -v
```

The tests use a fake provider and a mocked Ollama HTTP response. They do not
need to call a real AI model.

## 7. Optional Gemini provider

Add your own key to `.env`:

```env
GEMINI_API_KEY=your_actual_key_here
```

Run `python main.py` and choose `gemini`.

Never share your `.env` file or commit it to a public repository.

## Project files

- `llm_client.py` — provider interface, Gemini provider, Ollama provider, common client.
- `main.py` — chooses a provider and sends a prompt.
- `test_client.py` — automated unit tests.
- `requirements.txt` — Python dependencies.
- `.env` — local configuration (Gemini key is optional).
