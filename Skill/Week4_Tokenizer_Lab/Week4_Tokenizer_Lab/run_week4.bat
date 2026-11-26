@echo off
echo WEEK 4 - TOKENIZER LAB
if exist "..\.MyEnv\Scripts\activate.bat" (
    call "..\.MyEnv\Scripts\activate.bat"
) else if exist ".venv\Scripts\activate.bat" (
    call ".venv\Scripts\activate.bat"
) else (
    echo No existing parent .MyEnv or local .venv found.
    echo Create one using the commands in README.md.
    pause
    exit /b 1
)
python tokenizer_comparison.py
pause
