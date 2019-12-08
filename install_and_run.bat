@ECHO OFF

cmd

:: check if Python is installed
ECHO Checking if python is installed

python --version
if errorlevel 1 goto errorNoPython
ECHO Python is installed...

:: check version
ECHO Checking Python version...
for /f "tokens=*" %%a in ('python versioncheck.py') do set _PythonVersionOK=%%a

IF "%_PythonVersionOK%"=="True" (
    ECHO Python version >= 3.6
) ELSE (
    ECHO Python version < 3.6
    ECHO Please install Python >= 3.6
    start https://www.python.org/downloads/
    PAUSE
    EXIT
)

:: virutal environment
ECHO Creating virtual environment...
python -m venv lmpowered-venv
ECHO Virutal environment created...
ECHO Activating virtual environment...
lmpowered-venv\Scripts\activate.bat
ECHO Virutal environment activated...

:: install depencies
ECHO Installing Dependencies...
@pip install -r requirements.txt > nul
ECHO Dependencies installed...

:: instal pytorch
ECHO Installing PyTorch...
@pip3 install torch===1.3.1 torchvision===0.4.2 -f https://download.pytorch.org/whl/torch_stable.html > nul
ECHO PyTorch installed...

:: start server
ECHO Starting API-Server...
python webservice.py

goto :eof

errorNoPython:
ECHO.
ECHO Error^: Python not installed
ECHO Install Python and add it to the PATH environment variable
start https://www.python.org/downloads/

PAUSE