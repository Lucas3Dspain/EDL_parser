@ECHO OFF

rem   REM Create | Activate | Update the virtual environment
rem   echo Creating virtual env...
rem   python -m venv .venv
rem   call .venv\Scripts\activate
rem   python -m pip install --upgrade pip
rem
rem   REM Installing Packages
rem   echo Installing packages...
rem   pip install PySide2
rem   pip install QtPy
rem   pip install qtawesome

REM Notify user and wait for 15 seconds
echo Installation complete! Press 'Y' + Enter to open the tool...
timeout /t 5 >nul

REM Check if the user pressed 'o' during the 15 seconds
set /p "choice="
if /i "%choice%"=="Y" (
    start run.bat
) else (
    exit
)