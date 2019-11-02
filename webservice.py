import sys
import os
import math
import hashlib 
import mimetypes
import time
import pickle
from datetime import datetime
from decimal import Decimal

from util.stopwatch import StopWatch

# RegEx
import re
# Flask webservice
from flask import Flask, render_template, request, url_for, json, redirect, jsonify
from flask_cors import CORS
from json import JSONEncoder
from decimal import Decimal
from base64 import b64encode, b64decode

# check if the path of the needed Languagemodel is defined
langModelPath = os.environ.get('LANG_MODEL_PATH')
if langModelPath is None or not os.path.isdir(langModelPath):
    print("the variable 'LANG_MODEL_PATH' is not defined")
    exit()

sys.path.insert(0, langModelPath)
import langmodels.modelregistry as modelRegistry
from langmodels.inference.entropies import get_entropy_for_each_line
from langmodels.evaluation.common import EvaluationResult
from langmodels.evaluation.evaluation import evaluate_model_on_string, evaluate_model_on_file, evaluate_model_on_path
from dataprep.parse.model.metadata import PreprocessingMetadata
from langmodels.model import TrainedModel, ModelDescription

from util.modelinstance import ModelInstance

PORT = 8080
global rootPath
global completionModel
global root
global files

MODEL_ZOO_PATH_ENV_VAR = 'MODEL_ZOO_PATH'
if MODEL_ZOO_PATH_ENV_VAR in os.environ:
    MODEL_ZOO_PATH = os.environ[MODEL_ZOO_PATH_ENV_VAR]
else:
    MODEL_ZOO_PATH = os.path.join(os.environ['HOME'], 'modelzoo')

rootPath = os.path.dirname(os.path.realpath(__file__))



models = {}
registeredModels = modelRegistry.query_all_models(cached = True)

for model_description in registeredModels:
    models[model_description.id] = ModelInstance(model_description)

default_color_mapping = [
    {'min': 0, 'max': 2, 'color': "green"},
    {'min': 2, 'max': 4, 'color': "rgb(126, 128, 0)"},
    {'min': 4, 'max': 8, 'color': "orange"},
    {'min': 8, 'max': 16, 'color': "rgb(255, 72, 0)"},
    {'min': 16, 'max': 25, 'color': "red"},
]

app = Flask(__name__)
app.debug = True

cors = CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})

def print_json(value):
    return json.dumps(value, sort_keys=True, indent=2)

app.jinja_env.filters['print_json'] = print_json

@app.context_processor
def override_url_for():
    return dict(url_for=dated_url_for)

def dated_url_for(endpoint, **values):
    if endpoint == 'static':
        filename = values.get('filename', None)
        if filename:
            file_path = os.path.join(app.root_path, endpoint, filename)
            values['q'] = int(os.stat(file_path).st_mtime)
    return url_for(endpoint, **values)

@app.route('/')
def default():
    return redirect("/home", code=302)

@app.route('/home')
def home_page():
    list = [
        {'url': "/entropy", 'name': "Entropy", 'description': "Debug a single file in a web editor", 'icon': "code"},
        {'url': "/completion", 'name': "Auto completion", 'description': "Show proposals based on some context", 'icon': "future"},
        {'url': "/search", 'name': "Contextual search", 'description': "Perform contextual search queries", 'icon': "search"},
        {'url': "/overview", 'name': "Project overview", 'description': "Show all cached projects and files", 'icon': "database"},
    ]
    return render_template("home.html", list = list, lmpath = langModelPath, modelzoopath = os.environ.get('MODEL_ZOO_PATH'), models = models, default_color_mapping = default_color_mapping)  

def serialize_model(model:ModelInstance):
    return {
        'id': model.model_description.id,
        'bpe_merges': model.model_description.bpe_merges,
        'layers_config': model.model_description.layers_config,
        'arch': model.model_description.arch,
        'bin_entropy': model.model_description.bin_entropy,
        'training_time_minutes_per_epoch': model.model_description.training_time_minutes_per_epoch,
        'n_epochs': model.model_description.n_epochs,
        'best_epoch': model.model_description.best_epoch,
        'tags': model.model_description.tags,
    }

    #     id: str
    # bpe_merges: str
    # layers_config: str
    # arch: str
    # bin_entropy: float
    # training_time_minutes_per_epoch: int
    # n_epochs: int
    # best_epoch: int
    # tags: List[str]

# API-routes
@app.route('/api/models')
def api_models():
    serialized_models = [serialize_model(models[key]) for key in models]
    response = jsonify({
                'models': serialized_models,
            })
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route('/api/autocompletion', methods = ['POST'])
def api_autocompletion():
    sw = StopWatch()
    sw.start()
    stop_watch = StopWatch()
    stop_watch.start()

    data = json.loads(request.data)
    content = data.get('content', '')
    proposalsCount = int(data.get('proposalsCount', 10))
    selected_model_name = data.get('model', list(models.keys())[0])
    selected_model = models[selected_model_name]

    model = selected_model.get_model()
    sw_model_loading = stop_watch.elapsed()

    stop_watch.start()
    model.feed_text(content)
    sw_feed = stop_watch.elapsed()

    # this does not change the state of the completionModel:
    stop_watch.start()
    predictions = model.predict_next_full_token(n_suggestions = proposalsCount)
    model.reset()
    sw_predicions = stop_watch.elapsed()

    response = jsonify({
                'predictions': predictions,
                'metadata': {
                    'time_model_loading': sw_model_loading * 1000,
                    'time_feed': sw_feed * 1000,   
                    'time_predictions': sw_predicions * 1000,
                    'total': sw.elapsed() * 1000
                },
            })
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route('/api/languagemodel', methods = ['POST'])
def api_languagemodel():
    return user()

@app.route('/api/project', methods = ['GET'])
def api_project():
    projects = [{'name': files[hash]['name'], 'path': files[hash]['uri']['path'], 'url': hash} for hash in files.keys()]

    response = jsonify(projects)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response
    
@app.route('/api/project/<projecthash>', methods = ['GET'])
def api_project_files(projecthash):
    project = files[projecthash]
    
    # project_files = [{'name': project['files'][hash]['name'], 'path': project['files'][hash]['path'], 'relpath': project['files'][hash]['relpath'], 'hash': hash} for hash in project['files'].keys()]
    response = jsonify(project)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response    

@app.route('/api/project/<projecthash>/<filehash>', methods = ['GET'])
def api_project_files_detail(projecthash, filehash):
    project = files[projecthash]
    file = project['files'][filehash]
    # file_content_path = os.path.join(rootPath, 'cache', 'input', projecthash, filehash)
    file_entropy_path = os.path.join(rootPath, 'cache', 'output', projecthash, filehash)
    entropies = []

    if os.path.isfile(file_entropy_path):
        with open(file_entropy_path, 'r') as f:
            entropies = json.load(f)
            # file_ontent = content_file.read().splitlines()
            f.close()

    # project_files = project['files']
    response = jsonify({
        'file': file,
        'entropies': entropies
    })
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response       

@app.route('/api/compare', methods = ['POST'])
def api_compare():
    stop_watch = StopWatch()
    sw = StopWatch()
    sw.start()
    print("GOT COMPARE REQUEST ========================================================")
    data = json.loads(request.data)
    print(data)

    extension = data.get('extension', '')
    languageId = data.get('languageId', '')
    timestamp = float(data.get('timestamp', 1))/1000
    content = data.get('content', '')
    resetContext = data.get('resetContext', False)
    selected_model_name1 = data.get('model1', list(models.keys())[0])
    selected_model_name2 = data.get('model2', list(models.keys())[0])

    selected_model1 = models[selected_model_name1]
    selected_model2 = models[selected_model_name2]

    stop_watch.start()
    model1 = selected_model1.get_model()
    sw_model1_loading = stop_watch.elapsed()

    stop_watch.start()
    model2 = selected_model2.get_model()
    sw_model2_loading = stop_watch.elapsed()

    if not languageId in ['java', 'JAVA']:
        print("language " + languageId + " not supported")
        return {'error': 'language not supported yet'}, 404

    stop_watch.start()
    entropies1 = calculatelEntropiesOfString(model1, content, languageId) 
    entropies1 = [custom_to_dict(custom) for custom in entropies1]
    if (resetContext):
        model1.reset()
    sw_entropy1_calculation = stop_watch.elapsed()

    stop_watch.start()
    entropies2 = calculatelEntropiesOfString(model2, content, languageId) 
    entropies2 = [custom_to_dict(custom) for custom in entropies2]
    if (resetContext):
        model2.reset()
    sw_entropy2_calculation = stop_watch.elapsed()

    response = jsonify({
        'entropies1': entropies1,
        'entropies2': entropies2,
        'metadata': {
            'time_model1_loading': sw_model1_loading * 1000,
            'time_model2_loading': sw_model2_loading * 1000,
            'time_entropy1_calculation': sw_entropy1_calculation * 1000,   
            'time_entropy2_calculation': sw_entropy2_calculation * 1000,   
            'total': sw.elapsed() * 1000
        },
    })
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route('/api/search', methods = ['POST'])
def api_search():
    sw = StopWatch()
    sw.start()
    stop_watch = StopWatch()
    stop_watch.start()

    data = json.loads(request.data)
    content = data.get('content', '')
    search = data.get('search', '')
    searchInterval = int(data.get('searchInterval', 10))
    selected_model_name = data.get('model', list(models.keys())[0])
    selected_model = models[selected_model_name]

    model = selected_model.get_model()
    sw_model_loading = stop_watch.elapsed()

    lines = content.splitlines()

    originalContent = lines.copy()
    searchContent = lines.copy()
    i = 0
    while i < len(originalContent):
        originalContent.insert(i, '//')
        searchContent.insert(i, '//' + search)
        i += (searchInterval + 1)

    stop_watch.start()
    originalEntropies = calculatelEntropiesOfString(model, "\n".join(originalContent), 'java')
    model.reset()
    sw_original_entropies = stop_watch.elapsed()

    stop_watch.start()
    searchEntropies = calculatelEntropiesOfString(model, "\n".join(searchContent), 'java')
    model.reset()
    sw_search_entropies = stop_watch.elapsed()


    ret = {}
    ret['originalContent'] = (originalContent)
    ret['searchContent'] = (searchContent)
    ret['originalEntropy'] = [custom_to_dict(custom) for custom in originalEntropies]
    ret['searchEntropy'] = [custom_to_dict(custom) for custom in searchEntropies]

    response = jsonify({
        'metadata': {
                        'time_model_loading': sw_model_loading * 1000,
                        'time_original_entropies': sw_original_entropies * 1000,   
                        'time_search_entropies': sw_search_entropies * 1000,
                        'total': sw.elapsed() * 1000
                    },
        'entropies': ret
    })
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

# end API-routes

@app.route('/entropy')
def entropy_page():
    return render_template("entropy.html", models = models, default_color_mapping = default_color_mapping)      

@app.route('/completion')
def completion_page():
	return render_template("completion.html", models = models, default_color_mapping = default_color_mapping)       

@app.route('/overview')
def overview_page():
    return render_template("projectoverview.html", files = files, models = models, default_color_mapping = default_color_mapping)         

@app.route('/search')
def search_page():
    return render_template("search.html", models = models, default_color_mapping = default_color_mapping)  

@app.route('/overview/<projecthash>')
def overview_project(projecthash):
    return render_template("fileoverview.html", projecthash = projecthash, project = files[projecthash], models = models, default_color_mapping = default_color_mapping)    

@app.route('/overview/<projecthash>/<filehash>')
def overview_file(projecthash, filehash):
    file = files[projecthash]['files'][filehash]

    contentFilePath = os.path.join(rootPath, 'cache', 'input', projecthash, filehash)
    entropyFilePath = os.path.join(rootPath, 'cache', 'output', projecthash, filehash)

    if os.path.isfile(contentFilePath):
        with open(contentFilePath, 'r') as content_file:
            fileContent = content_file.read().splitlines()
            content_file.close()
    else:
        fileContent = "File not found"

    if os.path.isfile(entropyFilePath):
        with open(entropyFilePath, 'r') as content_file:
            entropyContent = json.load(content_file)
            content_file.close()
    else:
        entropyContent = map(lambda x: "", fileContent)
    
    return render_template("filedetail.html", file = file, fileContent = fileContent, entropyContentJson = json.dumps(entropyContent), entropyContent = entropyContent, projecthash = projecthash, filehash = filehash, models = models, default_color_mapping = default_color_mapping)   

@app.route('/search', methods = ['POST'])
def search():
    data = json.loads(request.data)
    content = data.get('content', '')
    search = data.get('search', '')
    searchInterval = int(data.get('searchInterval', 10))
    selected_model_name = data.get('model', list(models.keys())[0])
    selected_model = models[selected_model_name]

    model = selected_model.get_model()

    lines = content.splitlines()

    originalContent = lines.copy()
    searchContent = lines.copy()
    i = 0
    while i < len(originalContent):
        originalContent.insert(i, '//')
        searchContent.insert(i, '//' + search)
        i += (searchInterval + 1)

    originalEntropies = calculatelEntropiesOfString(model, "\n".join(originalContent), 'java')
    searchEntropies = calculatelEntropiesOfString(model, "\n".join(searchContent), 'java')

    ret = {}
    ret['originalContent'] = (originalContent)
    ret['searchContent'] = (searchContent)
    ret['originalEntropy'] = [custom_to_dict(custom) for custom in originalEntropies]
    ret['searchEntropy'] = [custom_to_dict(custom) for custom in searchEntropies]

    model.reset()
    encoded = json.dumps(ret)
    return encoded

# Calculates and retun the entopies of a given inputfile
def calculatelEntropiesOfString(model: TrainedModel, text: str, extension = 'java'):
    entropies = evaluate_model_on_string(model, text, extension)
    return entropies

@app.route('/autocompletion', methods = ['POST'])
def autocompletion():
    data = json.loads(request.data)
    content = data.get('content', '')
    proposalsCount = int(data.get('proposalsCount', 10))
    selected_model_name = data.get('model', list(models.keys())[0])
    selected_model = models[selected_model_name]

    model = selected_model.get_model()

    model.feed_text(content)

    # this does not change the state of the completionModel:
    predictions = model.predict_next_full_token(n_suggestions = proposalsCount)
    model.reset()

    encoded = json.dumps(predictions)

    return encoded

@app.route('/languagemodel', methods = ['POST'])
def user():
    sw = StopWatch()
    sw.start()
    print("GOT LM REQUEST ========================================================")
    data = json.loads(request.data)

    extension = data.get('extension', '')
    languageId = data.get('languageId', '')
    filePath = data.get('filePath', '')
    noReturn = data.get('noReturn', 'false') == "true"
    timestamp = float(data.get('timestamp', 1))/1000
    content = data.get('content', '')
    workspaceFolder = data.get('workspaceFolder', None)
    resetContext = data.get('resetContext', False)
    selected_model_name = data.get('model', list(models.keys())[0])
    selected_model = models[selected_model_name]

    stop_watch = StopWatch()

    stop_watch.start()
    model = selected_model.get_model()
    sw_model_loading = stop_watch.elapsed()
    sw_entropy_calculation = 0

    if not languageId in ['java', 'JAVA']:
        print("language " + languageId + " not supported")
        return {'error': 'language not supported yet'}, 404

    shouldCalculateEntropies = True

    #check if file is cached
    hashedName = hashlib.md5(filePath.encode()).hexdigest()  # str(hash(filePath))

    if workspaceFolder:
        projectHash = hashlib.md5(workspaceFolder['uri']['fsPath'].encode()).hexdigest()

        if files.get(projectHash, None) == None:
            files[projectHash] = workspaceFolder
            files[projectHash]['files'] = {}

        files[projectHash]['files'][hashedName] = {
            'path': filePath, 
            'name': os.path.basename(filePath), 
            'relpath': os.path.relpath(filePath, workspaceFolder['uri']['fsPath'])}

        with open(os.path.join(rootPath, 'files.json'), 'w') as outfile:		
            json.dump(files, outfile)	
            outfile.flush()
            outfile.close()	
        
        path = os.path.join(rootPath, 'cache', 'output', projectHash, hashedName)
    
    else:
        path = os.path.join(rootPath, 'cache', 'output', 'temp', hashedName)
    
    if os.path.isfile(path):
        modTimesinceEpoc = os.path.getmtime(path)
        
        if modTimesinceEpoc < timestamp:
            print("file has been modified -> recalculate entropies")
        else:
            print("file has NOT been modified -> recalculation not needed")
            shouldCalculateEntropies = False

    if shouldCalculateEntropies:
        # save file:
        if workspaceFolder:
            savePath = os.path.join(rootPath, 'cache', 'input', projectHash, hashedName)
        else:
            savePath = os.path.join(rootPath, 'cache', 'input', 'temp', hashedName)

        checkOrCreate(os.path.dirname(savePath))
        checkOrCreate(os.path.dirname(path))

        f = open(savePath,"w")
        f.write(content)
        f.close()

        stop_watch.start()
        entropies = calculatelEntropiesOfString(model, content, languageId) 
        sw_entropy_calculation = stop_watch.elapsed()
        print("entropies calculated")
        print("ENTROPIES")
        print(entropies)
        
        # write entropies to file (json-format)
        with open(path, 'w') as f:
            json.dump([custom_to_dict(custom) for custom in entropies], f)
            f.close()	

    if (resetContext):
        model.reset()

    if noReturn == True:
        print("NO return data...")
    else:
        with open(path, 'r') as content_file:
            entropies = content_file.read()
            entropies = json.loads(entropies)
            response = jsonify({
                'entropies': entropies,
                'metadata': {
                    'time_model_loading': sw_model_loading * 1000,
                    'time_entropy_calculation': sw_entropy_calculation * 1000,   
                    'total': sw.elapsed() * 1000
                },
            })
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response

    return "request processed"

def custom_to_dict(custom):
    return {
        'text': custom.text,
        'prep_text': custom.prep_text,
        'results': custom.results,
        'prep_metadata': {'word_boundaries': custom.prep_metadata.word_boundaries, 'nonprocessable_tokens': list(custom.prep_metadata.nonprocessable_tokens)},
        'aggregated_result': custom.aggregated_result,
    }

def checkOrCreateForFilepath(path):
    directory = os.path.dirname(path)
    if not os.path.exists(directory):
        os.makedirs(directory)

def checkOrCreate(path): 
    if not os.path.exists(path):
        os.makedirs(path)

# read cached files for debugging
files = {}
filesJsonPath = os.path.join(rootPath, 'files.json')
if os.path.exists(filesJsonPath):
    with open(filesJsonPath, 'r') as json_files:
        try:
            files = json.load(json_files)
        except:
            files = {}
        json_files.close()

checkOrCreate(os.path.join(rootPath, 'cache', 'input'))
checkOrCreate(os.path.join(rootPath, 'cache', 'temp'))
checkOrCreate(os.path.join(rootPath, 'cache', 'output'))

if __name__ == '__main__':
    print("Starting WebServer on Port ", PORT)
    print("Loading Completion-Language Model")
    #completionModel = load_model_by_name(SMALL_MODEL_NAME)
    print("Language Model loaded")

    app.run(use_reloader=True, port=PORT) #host='0.0.0.0'
