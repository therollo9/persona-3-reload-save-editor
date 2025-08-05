@echo off
title Persona 3 Reload Save Editor (Standard Edition)
echo Starting Persona 3 Reload Save Editor...
python p3r_editor.py
if %ERRORLEVEL% neq 0 (
  echo.
  echo Error occurred. Press any key to exit.
  pause > nul
)
