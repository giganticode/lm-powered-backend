# LM-Powered: bringing neural language models to your IDE - Backend

## Quick start

### Prerequirements
Python version >= 3.6 required.
Download and install Python from the official website https://www.python.org/downloads/


### Installation

Clone the project
```
git clone https://github.com/giganticode/lm-powered-backend.git
```

#### Windows
Run the 'install_and_run.bat'-Script - it will install all dependencies and start the webservice.
```
cd lm-powered-backend
.\install_and_run.bat
```

#### Unix
Run the 'install_and_run.sh'-Script - it will install all dependencies and start the webservice.
```
cd lm-powered-backend
sh install_and_run.sh
```

### Manual installation
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

--port=8080 => Set the port of the webservice (default 8080)

--host=127.0.0.1 => Set the host of the webservice (default 127.0.0.1 )

--debug => Enable the debug mode (default false)

--use-cache => Use only cached models

--no-cache => Download all available models from the server


#### Start the webservice with the provided script
run the run.bat-script (Windows) or the run.sh-script (UNIX)

Running this script will start the webservice.

Note: on Windows you have to install PyTorch (See section 'Windows only')

## Install the extension for Visual Studio Code
Open Visual Studio Code and open the Extensions-page (Ctrl + Shift + X)

Click on 'More actions' (...) on the right top corner of the extensions sidebar, select 'Install from VSIX...' and select the file 'lmpowered-0.0.1.vsix'. Activate the extension afterwards.