@echo off
echo ========================================
echo AI PR Review Assistant
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org/
    pause
    exit /b 1
)

REM Check if .env file exists
if not exist .env (
    echo Warning: .env file not found
    echo Creating from .env.example...
    copy .env.example .env
    echo.
    echo Please edit .env file with your API keys:
    echo - CLAUDE_API_KEY (required)
    echo - GITHUB_TOKEN (optional, for private repos)
    echo.
    pause
)

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt
echo.

REM Run installation test
echo Running installation test...
python test_install.py
echo.

REM Start the application
echo Starting AI PR Review Assistant...
echo Open http://localhost:5000 in your browser
echo.
echo Press Ctrl+C to stop the server
echo.
python app.py
