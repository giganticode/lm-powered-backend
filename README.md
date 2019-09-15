# Visualizing Contextual Information within Visual Studio Code

<!-- [![Build Status](https://travis-ci.org/giganticode/langmodels.svg?branch=master)](https://travis-ci.org/giganticode/langmodels)

**Applying machine learning to large source code corpora** -->

# Quick start

Python version >= 3.6 required!

## Building from source

### Prerequirements
clone the languagemodel from https://github.com/giganticode/langmodels

### Clone the extension

```
git clone https://github.com/giganticode/vsc-extension-backend
```

set `LANG_MODEL_PATH` env variable to point to the languagemodel repo, e.g.:
```
`Linux:` export LANG_MODEL_PATH="$HOME/dev/langmodel"
`Windows:` setx -m LANG_MODEL_PATH "%HOME%\langmodel"
```

# Starting the webservice
run the run.sh-script
