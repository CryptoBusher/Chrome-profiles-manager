@if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
) else (
    echo [INFO] Virtual environment not found, running without it...
)

python -m main
pause