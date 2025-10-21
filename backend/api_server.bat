@echo off
echo Starting api_server.py...

REM Start Python process in the background
start /B "" "./venv/Scripts/python.exe" "./src/api_server.py"

echo API server started. Press any key to terminate and exit.
pause

REM Kill all Python processes started by this script
taskkill /F /IM python.exe /T 2>nul