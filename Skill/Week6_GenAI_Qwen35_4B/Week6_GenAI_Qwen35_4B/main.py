"""
WEEK 6 - GENERATIVE AI PROGRAMMING PRACTICAL
Golden Question Set + First Baseline Run (Release v0.1)

Model: qwen3.5:4b (local Ollama)
API: http://localhost:11434/api/generate

Reliability:
- Each question is isolated in its own try/except.
- A failed question is recorded as ERROR and the loop continues.
- Every completed question is appended to CSV immediately.
- Previous rows remain in the CSV if the run is interrupted.
"""

import csv
import json
import time
from datetime import datetime
from pathlib import Path

import requests

# ---------------- CONFIGURATION ----------------
BASE_DIR = Path(__file__).resolve().parent
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen3.5:4b"
INPUT_FILE = BASE_DIR / "golden_set.json"
OUTPUT_FILE = BASE_DIR / "baseline_results.csv"

REQUEST_TIMEOUT = 180
MAX_RETRIES = 1
PASS_THRESHOLD = 60.0  # 60% threshold used in the supplied Week 6 practical
RELEASE_VERSION = "v0.1"

FIELDNAMES = [
    "Run_ID",
    "Release",
    "Evaluation_Date",
    "Question_ID",
    "Question",
    "Expected_Answer",
    "LLM_Answer",
    "Required_Keywords",
    "Matched_Keywords",
    "Missing_Keywords",
    "Score_Percent",
    "Status",
    "Source",
    "Model",
    "Prompt_Tokens",
    "Output_Tokens",
    "Total_Tokens",
    "Latency_Seconds",
    "Error",
]


def load_golden_questions():
    """Load and validate the golden question JSON file."""
    with INPUT_FILE.open("r", encoding="utf-8") as file:
        questions = json.load(file)

    if not isinstance(questions, list) or not questions:
        raise ValueError("golden_set.json must contain a non-empty JSON list.")

    required_fields = {"id", "question", "expected_answer", "keywords", "source"}
    for index, item in enumerate(questions, start=1):
        missing = required_fields - set(item)
        if missing:
            raise ValueError(
                f"Question at position {index} is missing fields: {sorted(missing)}"
            )
        if not isinstance(item["keywords"], list):
            raise ValueError(f"{item['id']} keywords must be a list.")

    return questions


def get_llm_answer(question):
    """Call the local Ollama generate endpoint; retry transient failures."""
    payload = {
        "model": MODEL_NAME,
        "prompt": (
            "Answer the following question accurately and clearly in 2 to 5 sentences. "
            "Use standard GenAI terminology. Do not claim to have used a source unless "
            "the source content was provided.\n\n"
            f"Question: {question}\n\nAnswer:"
        ),
        "stream": False,
        "options": {"temperature": 0}
    }

    last_error = None
    for attempt in range(MAX_RETRIES + 1):
        try:
            response = requests.post(
                OLLAMA_URL,
                json=payload,
                timeout=REQUEST_TIMEOUT
            )
            response.raise_for_status()
            data = response.json()

            answer = data.get("response", "").strip()
            if not answer:
                raise ValueError("Ollama returned an empty response.")

            usage = {
                "prompt_tokens": data.get("prompt_eval_count", ""),
                "output_tokens": data.get("eval_count", ""),
            }
            return answer, usage

        except requests.exceptions.Timeout:
            last_error = f"Request timed out after {REQUEST_TIMEOUT} seconds."
        except requests.exceptions.ConnectionError:
            last_error = (
                "Cannot connect to Ollama. Check that Ollama is running "
                "at http://localhost:11434."
            )
        except requests.exceptions.HTTPError as exc:
            details = ""
            if exc.response is not None:
                details = exc.response.text[:500]
            last_error = f"Ollama HTTP error: {exc}. {details}"
        except (ValueError, requests.exceptions.RequestException) as exc:
            last_error = f"{type(exc).__name__}: {exc}"
        except Exception as exc:
            last_error = f"Unexpected {type(exc).__name__}: {exc}"

        if attempt < MAX_RETRIES:
            time.sleep(2)

    raise RuntimeError(last_error or "Unknown Ollama request error.")


def calculate_score(answer, expected_keywords):
    """Case-insensitive keyword matching and coverage score."""
    normalized_answer = " ".join((answer or "").casefold().split())
    matched = []
    missing = []

    for keyword in expected_keywords:
        normalized_keyword = " ".join(str(keyword).casefold().split())
        if normalized_keyword and normalized_keyword in normalized_answer:
            matched.append(keyword)
        else:
            missing.append(keyword)

    total = len(expected_keywords)
    score = (len(matched) / total * 100.0) if total else 0.0
    return round(score, 2), matched, missing


def append_result(row):
    """Append one row immediately; do not wait until all 30 questions finish."""
    file_exists = OUTPUT_FILE.exists() and OUTPUT_FILE.stat().st_size > 0

    with OUTPUT_FILE.open("a", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDNAMES)
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)
        file.flush()


def main():
    questions = load_golden_questions()
    run_id = datetime.now().strftime("WEEK6-%Y%m%d-%H%M%S")

    print("\n" + "=" * 68)
    print("WEEK 6 - GOLDEN QUESTION SET & BASELINE EVALUATION")
    print("=" * 68)
    print(f"Release       : {RELEASE_VERSION}")
    print(f"Model         : {MODEL_NAME}")
    print(f"Total questions: {len(questions)}")
    print(f"Pass threshold: {PASS_THRESHOLD:.0f}%")
    print(f"Output file   : {OUTPUT_FILE}")
    print("=" * 68)

    passed = 0
    failed = 0
    errors = 0
    completed = 0

    for index, item in enumerate(questions, start=1):
        question_id = item["id"]
        question = item["question"]
        expected_answer = item["expected_answer"]
        keywords = item["keywords"]
        source = item["source"]

        answer = ""
        error_message = ""
        matched = []
        missing = list(keywords)
        score = 0.0
        prompt_tokens = ""
        output_tokens = ""
        started = time.perf_counter()

        print(f"\n[{index:02d}/{len(questions):02d}] {question_id}: {question}")

        try:
            answer, usage = get_llm_answer(question)
            prompt_tokens = usage["prompt_tokens"]
            output_tokens = usage["output_tokens"]

            score, matched, missing = calculate_score(answer, keywords)
            status = "PASS" if score >= PASS_THRESHOLD else "FAIL"

            if status == "PASS":
                passed += 1
            else:
                failed += 1

            print(f"Answer: {answer}")
            print(f"Matched keywords: {matched}")
            print(f"Missing keywords: {missing}")
            print(f"Score: {score:.2f}%")
            print(f"Status: {status}")

        except Exception as exc:
            # Record this question's error and continue with the next question.
            status = "ERROR"
            error_message = str(exc)
            errors += 1
            print(f"ERROR: {error_message}")
            print("Continuing to the next question...")

        latency = round(time.perf_counter() - started, 3)

        prompt_count = int(prompt_tokens) if str(prompt_tokens).isdigit() else 0
        output_count = int(output_tokens) if str(output_tokens).isdigit() else 0

        row = {
            "Run_ID": run_id,
            "Release": RELEASE_VERSION,
            "Evaluation_Date": datetime.now().isoformat(timespec="seconds"),
            "Question_ID": question_id,
            "Question": question,
            "Expected_Answer": expected_answer,
            "LLM_Answer": answer,
            "Required_Keywords": " | ".join(keywords),
            "Matched_Keywords": " | ".join(matched),
            "Missing_Keywords": " | ".join(missing),
            "Score_Percent": score,
            "Status": status,
            "Source": source,
            "Model": MODEL_NAME,
            "Prompt_Tokens": prompt_tokens,
            "Output_Tokens": output_tokens,
            "Total_Tokens": (
                prompt_count + output_count
                if prompt_tokens != "" or output_tokens != ""
                else ""
            ),
            "Latency_Seconds": latency,
            "Error": error_message,
        }

        try:
            append_result(row)
        except OSError as exc:
            # A disk/write error cannot be safely recovered by this script.
            print(f"FATAL: Could not save {question_id} to CSV: {exc}")
            print("Stop here and check folder permissions/disk space.")
            raise

        completed += 1

    print("\n" + "=" * 68)
    print("BASELINE EVALUATION SUMMARY")
    print("=" * 68)
    print(f"Release version       : {RELEASE_VERSION}")
    print(f"Model                 : {MODEL_NAME}")
    print(f"Total questions       : {len(questions)}")
    print(f"Completed             : {completed}")
    print(f"PASS                  : {passed}")
    print(f"FAIL                  : {failed}")
    print(f"ERROR                 : {errors}")
    print(f"Results saved to      : {OUTPUT_FILE}")
    print("BASELINE RUN COMPLETED")
    print("=" * 68)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(
            "\nRun interrupted by user. Rows already written to "
            "baseline_results.csv are preserved."
        )
    except Exception as exc:
        print(f"\nPROJECT SETUP ERROR: {type(exc).__name__}: {exc}")
        raise
