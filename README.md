# Visualizing Contextual Information within Visual Studio Code

# Quick start

Python version >= 3.6 required

## Build from source

### Prerequirements
clone the languagemodel from https://github.com/giganticode/langmodels (follow instructions)

### Clone the webservice

```
git clone https://github.com/giganticode/vsc-extension-backend
```

Set `LANG_MODEL_PATH` env variable to point to the languagemodel repo, e.g.:
```
Linux: export LANG_MODEL_PATH="$HOME/dev/langmodel"
Windows: setx -m LANG_MODEL_PATH "%HOME%\langmodel"
```

# Install python dependencies
pip install -r requirements.txt

# Start the webservice
run the run.sh-script

or

open a shell and run 'python webservice.py '

