#!/bin/sh
python lmpowered/load_model_pool.py &
python lmpowered/webservice.py
$SHELL