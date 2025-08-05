@echo off
title Persona 3 Reload Save Editor (Enhanced Edition)
echo Starting Enhanced Persona 3 Reload Save Editor...
python enhanced_p3r_editor_fixed.py
if %ERRORLEVEL% neq 0 (
  echo.
  echo Error occurred. Press any key to exit.
  pause > nul
)
