@echo off
title BUILD SUPER RED CYBER TERMINAL
python -m pip install pyinstaller
python -m PyInstaller --onefile --windowed --name SUPER_RED_CYBER_TERMINAL main.py
echo.
echo EXE created inside the dist folder.
pause
