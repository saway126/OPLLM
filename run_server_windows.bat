@echo off
echo Starting Air-gapped LLM Server on Windows...

:: Check if venv exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

:: Activate venv
call venv\Scripts\activate

:: Install dependencies if needed (fast check)
if not exist "venv\Lib\site-packages\fastapi" (
    echo Installing dependencies...
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo Error installing dependencies.
        pause
        exit /b %errorlevel%
    )
)

:: Run Server
echo Server is starting at http://localhost:8000
echo Press Ctrl+C to stop.
python -m src.main
pause
