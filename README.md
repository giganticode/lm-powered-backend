# Visualizing Contextual Information within Visual Studio Code - Backend

## Quick start

### Prerequirements
Python version >= 3.6 required.
Download and install Python from the official website https://www.python.org/downloads/


### Installation

Clone the project
```
git clone https://github.com/giganticode/vsc-extension-backend.git
cd vsc-extension-backend
python -m venv vsc-extension-backend-venv
source vsc-extension-backend-venv/bin/activate
```

#### Windows only
Install PyTorch
```
pip3 install torch===1.3.1 torchvision===0.4.2 -f https://download.pytorch.org/whl/torch_stable.html
```

#### Install python dependencies
```
pip install -r requirements.txt
```

### Start the webservice
```
python webservice.py 
```

Optional parameters:

--port => Set the port of the webservice (default 8080)

--serverhost => Set the host of the webservice (default 127.0.0.1 )

--debug => Enable the debug mode (default false)


### Install and start the webservice 
run the run.bat-script (Windows) or the run.sh-script (UNIX)

Running this script will install all depencies and start the webservice.

Note: on Windows you have to install PyTorch (See section 'Windows only')