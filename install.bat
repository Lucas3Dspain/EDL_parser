@ECHO OFF

REM Create | Activate | Update the virtual environment
echo Creating virtual env...
python -m venv .venv
call .venv\Scripts\activate
python -m pip install --upgrade pip

REM Installing Packages
echo Installing packages...
pip install PySide2
pip install QtPy
pip install qtawesome

REM Notify user and wait for 15 seconds
echo Installation complete! Press 'Y' + Enter to open the tool...
timeout /t 5 >nul

REM Check if the user pressed 'o' during the 15 seconds
set /p "choice="
if /i "%choice%"=="Y" (
    python src/edlParser/edl_parser.py
) else (
    exit
)