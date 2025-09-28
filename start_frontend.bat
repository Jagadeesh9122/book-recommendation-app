@echo off
echo Starting Book Recommendation System Frontend
echo ============================================

cd frontend

echo Installing frontend dependencies...
call npm install

if %errorlevel% neq 0 (
    echo Failed to install dependencies
    pause
    exit /b 1
)

echo Starting React development server...
call npm start

pause
