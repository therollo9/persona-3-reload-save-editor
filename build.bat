@echo off
REM ================================================
REM Persona 3 Reload Save Editor - Build Script
REM ================================================

echo.
echo Building Persona 3 Reload Save Editor Executables
echo ================================================
echo.

REM Create build directory if it doesn't exist
if not exist "build" mkdir build
echo [+] Build directory ready

REM Clean old builds
echo [+] Cleaning old build files...
if exist "dist\P3R_Save_Editor.exe" del "dist\P3R_Save_Editor.exe"
if exist "dist\P3R_Enhanced_Editor.exe" del "dist\P3R_Enhanced_Editor.exe"
if exist "build\*.*" del /Q "build\*.*"

echo.
echo [+] Starting to build Standard Editor...
echo ------------------------------------------------
pyinstaller --clean --onefile --name "P3R_Save_Editor" --distpath "build" p3r_editor.py
if %ERRORLEVEL% neq 0 (
    echo [-] Error building Standard Editor!
    goto error
)
echo [+] Standard Editor built successfully!

echo.
echo [+] Starting to build Enhanced Editor...
echo ------------------------------------------------
pyinstaller --clean --onefile --name "P3R_Enhanced_Editor" --distpath "build" enhanced_p3r_editor_fixed.py
if %ERRORLEVEL% neq 0 (
    echo [-] Error building Enhanced Editor!
    goto error
)
echo [+] Enhanced Editor built successfully!

REM Clean up PyInstaller artifacts
echo.
echo [+] Cleaning up temporary build files...
if exist "P3R_Save_Editor.spec" del "P3R_Save_Editor.spec"
if exist "P3R_Enhanced_Editor.spec" del "P3R_Enhanced_Editor.spec"
if exist "__pycache__" rmdir /S /Q "__pycache__"

echo.
echo ================================================
echo Build completed successfully!
echo.
echo Executables available in the "build" folder:
echo - build\P3R_Save_Editor.exe
echo - build\P3R_Enhanced_Editor.exe
echo ================================================
echo.
goto end

:error
echo.
echo ================================================
echo Build process failed! See errors above.
echo ================================================
echo.
exit /b 1

:end
echo Press any key to exit...
pause > nul
exit /b 0
