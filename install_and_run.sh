#!/bin/bash
# check if python is installed
echo Checking if python is installed...

if command -v python3 &>/dev/null; then
    echo Python is installed...
else
    echo Python is not installed...
    echo Install Python and add it to the PATH environment variable
    xdg-open https://www.python.org/downloads/
    exit
fi

# check the version of pythn
echo Checking Python version...

VERSION_OK=$(python3 versioncheck.py)

if [ "$VERSION_OK" = "True" ]
then
    echo "Python version >= 3.6"
else
    echo "Python version < 3.6"
    echo "Please install Pathon >= 3.6"
    xdg-open https://www.python.org/downloads/
    exit
fi

# setup virtual environment
echo Creating virtual environment...
python3 -m venv lmpowered-venv
echo Virtual environment created...

echo Activating virtual environment...
source lmpowered-venv/bin/activate
echo Virtual environment activated...

# install dependencies
echo Installing dependencies...
pip install -r requirements.txt
echo Dependencies installed...

# start server
echo Starting API-Server at http://localhost:8080
python3 webservice.py