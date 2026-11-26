# WEEK 6 - Generative AI Programming Practical
## Golden Question Set and First Baseline Run - Release v0.1

This folder follows the supplied Week 6 practical handout:
- 30 golden questions (Q001-Q030)
- Expected answers
- Required keywords
- Reference source URLs
- First baseline evaluation
- CSV output file
- Release label v0.1

**Configured local model:** `qwen3.5:4b` using Ollama.

## Folder structure

```text
Week6_GenAI_Qwen35_4B/
├── golden_set.json
├── main.py
├── requirements.txt
├── baseline_results.csv
└── README.md
```

## 1. Verify Ollama and model

Open PowerShell:

```powershell
ollama --version
ollama list
```

Confirm the model tag is exactly `qwen3.5:4b`. If it is not listed, run:

```powershell
ollama pull qwen3.5:4b
```

Test the model:

```powershell
ollama run qwen3.5:4b
```

Type a question, then exit the chat with `/bye`.

Ollama normally runs in the background on Windows. The script expects its local API at `http://localhost:11434`.

## 2. Open the project in VS Code

Extract the ZIP file. In VS Code, open the extracted `Week6_GenAI_Qwen35_4B` folder. Open Terminal > New Terminal.

## 3. Create and activate a virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If activation is blocked by PowerShell policy, use the virtual-environment Python directly in the next commands:

```powershell
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

If activation works, these commands are also valid:

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Wait for pip to finish. Do not press Ctrl+C during installation.

## 4. Run the Week 6 baseline

With the virtual environment active:

```powershell
python main.py
```

Or use the environment's Python explicitly:

```powershell
.\.venv\Scripts\python.exe main.py
```

## 5. Output

The program calls Qwen 3.5:4B locally for all 30 questions and writes results to `baseline_results.csv`.

The CSV includes:
- Question ID and question
- Expected answer and generated LLM answer
- Required keywords
- Matched keywords
- Missing keywords
- Keyword coverage score
- PASS / FAIL / ERROR status
- Source URL and model name
- Prompt/output token counts when Ollama provides them
- Latency and error details

## 6. Scoring

The supplied handout's sample program uses a 60% keyword-coverage threshold. This project retains that threshold:
- PASS: score >= 60%
- FAIL: answer was generated but score < 60%
- ERROR: request or response processing failed

Score = (matched required keywords / total required keywords) * 100.

Keyword matching is case-insensitive substring matching. It is a simple baseline metric and does not prove factual correctness. Check the answer against the expected answer and reference source.

## 7. Error handling and saved progress

Each question has its own error handler. If Ollama is unavailable, a request times out, or one response fails:
- The question is recorded with status `ERROR`.
- The error is stored in the CSV.
- The script proceeds to the next question.
- Each completed question is saved immediately.

If you press Ctrl+C, already saved CSV rows remain. Re-running appends another run; use the `Run_ID` column to distinguish runs.

## Troubleshooting

**Cannot connect to Ollama**
1. Open the Ollama Windows application.
2. Run `ollama list`.
3. Check that `qwen3.5:4b` is installed.
4. Retry `python main.py`.

**ModuleNotFoundError: requests**
```powershell
python -m pip install -r requirements.txt
```

**PowerShell shows `>>`**
The shell is waiting for an unfinished command or quote. Press Ctrl+C once, then enter the command again.

**Permission denied for CSV**
Close the CSV in Excel and check that the project folder is writable.

## Deliverable

The first completed evaluation is identified as **Release v0.1**. Keep the generated `baseline_results.csv` as the evidence of your actual baseline run.
