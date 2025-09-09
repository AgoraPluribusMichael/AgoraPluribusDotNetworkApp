@echo off
echo Starting stt_keybind.py...

REM Start Python process in the background
start /B "" "./venv/Scripts/python.exe" "./src/stt_keybind.py"

echo STT processes started. Press any key to terminate and exit.
pause

REM Kill all Python processes started by this script
taskkill /F /IM python.exe /T 2>nul