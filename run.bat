@ECHO OFF

rem Activate the virtual environment
call .venv\Scripts\activate

rem Build & install package
python src/edlParser/edl_parser.py && (
    rem Deactivate the virtual environment (optional)
    deactivate
)
