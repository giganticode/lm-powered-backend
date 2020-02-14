#!/bin/sh
python load_model_pool.py &
python webservice.py 
$SHELL