import sys
import os
import math
import hashlib 
import mimetypes
import time
import pickle
from datetime import datetime
from decimal import Decimal
import re
from flask import Flask, render_template, request, json, redirect, jsonify
from flask_cors import CORS
from decimal import Decimal
from base64 import b64encode, b64decode
from controller.util import check_or_create

# check if the path of the needed Languagemodel is defined
langModelPath = os.environ.get('LANG_MODEL_PATH')
if langModelPath is None or not os.path.isdir(langModelPath):
    print("the variable 'LANG_MODEL_PATH' is not defined")
    exit()

sys.path.insert(0, langModelPath)
import langmodels.modelregistry as modelRegistry

from util.modelinstance import ModelInstance
from util.entropyresult import EntropyResult, EntropyLine, Token
from controller.project_overview_controller import ProjectOverviewController
from controller.entropy_controller import EntropyController

PORT = 8080
global rootPath
global files
global models

rootPath = os.path.dirname(os.path.realpath(__file__))

models = {}
registeredModels = modelRegistry.query_all_models(cached = True)

for model_description in registeredModels:
    models[model_description.id] = ModelInstance(model_description)

app = Flask(__name__, static_folder='')

# enable CORS for api endpoint
app.debug = True
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

files = {}
files_json_path = os.path.join(rootPath, 'files.json')
if os.path.exists(files_json_path):
    with open(files_json_path, 'r') as json_files:
        try:
            files = json.load(json_files)
        except:
            files = {}
        json_files.close()

# controllers
project_overview_controller = ProjectOverviewController(rootPath, files)
entropy_controller = EntropyController(rootPath, models, files)

@app.route('/')
def default():
    return redirect("/home", code=302)

@app.route('/home')
def home_page():
    return app.send_static_file('static/index.html')

@app.errorhandler(404) #redirect 404 errors to the client (VueJS)
def page_not_found(e):
    return app.send_static_file('static/index.html')    

# API-routes
@app.route('/api/models')
def api_models():
    serialized_models = [models[key].serialize_model() for key in models]
    response = jsonify({
                'models': serialized_models,
            })
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route('/api/projects', methods = ['GET'])
def api_projects():
    return project_overview_controller.get_projects()
    
@app.route('/api/project/<projecthash>', methods = ['GET'])
def api_project_files(projecthash):
    return project_overview_controller.get_project_files(projecthash)

@app.route('/api/project/<projecthash>/<filehash>', methods = ['GET'])
def api_project_file_detail(projecthash, filehash):
    return project_overview_controller.get_project_file_detail(projecthash, filehash)

@app.route('/api/autocompletion', methods = ['POST'])
def api_autocompletion():
    return entropy_controller.get_predictions(request, models)

@app.route('/api/languagemodel', methods = ['POST'])
def api_languagemodel():
    return entropy_controller.get_entropies(request, models)

@app.route('/api/compare', methods = ['POST'])
def api_compare():
    return entropy_controller.get_compare(request, models)

@app.route('/api/search', methods = ['POST'])
def api_search():
    return entropy_controller.get_search(request, models)

check_or_create(os.path.join(rootPath, 'cache'))

if __name__ == '__main__':
    print("Starting WebServer on Port ", PORT)
    app.run(use_reloader=True, port=PORT) #host='0.0.0.0'
