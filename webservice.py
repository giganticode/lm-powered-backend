import sys
import os
import hashlib 
import mimetypes
import time
from datetime import datetime
from decimal import Decimal
# RegEx
import re
# Flask webservice
from flask import Flask, render_template, request, json, redirect
from json import JSONEncoder
import pickle
from decimal import Decimal
from base64 import b64encode, b64decode

# check if the path of the needed Languagemodel is defined
langModelPath = os.environ.get('LANG_MODEL_PATH')
if langModelPath is None or not os.path.isdir(langModelPath):
    print("the variable 'LANG_MODEL_PATH' is not defined")
    exit()

sys.path.insert(0, langModelPath)
# def get_entropy_for_each_line(trained_model: TrainedModel, file: str, verbose: bool = False, only_aggregated_entropies: bool = True)
from langmodels.inference.entropies import get_entropy_for_each_line
from langmodels.model import TrainedModel
from langmodels.evaluation.common import EvaluationResult
from dataprep.parse.model.metadata import PreprocessingMetadata

PORT = 8080
global rootPath
global model
global completionModel
global root
global files

rootPath = os.path.dirname(os.path.realpath(__file__))

app = Flask(__name__)
app.debug = True

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
    return render_template("home.html", list = list, lmpath = langModelPath, modelzoopath = os.environ.get('MODEL_ZOO_PATH'))

@app.route('/entropy')
def entropy_page():
    return render_template("entropy.html")      

@app.route('/completion')
def completion_page():
	return render_template("completion.html")    

@app.route('/overview')
def overview_page():
    return render_template("projectoverview.html", files = files)         

@app.route('/search')
def search_page():
    return render_template("search.html")     

@app.route('/overview/<projecthash>')
def overview_project(projecthash):
    return render_template("fileoverview.html", projecthash = projecthash, project = files[projecthash])   

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
    
    return render_template("filedetail.html", file = file, fileContent = fileContent, entropyContentJson = json.dumps(entropyContent), entropyContent = entropyContent, projecthash = projecthash, filehash = filehash)   

@app.route('/search', methods = ['POST'])
def search():
    data = json.loads(request.data)
    content = data.get('content', '')
    search = data.get('search', '')
    searchInterval = int(data.get('searchInterval', 10))

    lines = content.splitlines()

    originalContent = lines.copy()
    searchContent = lines.copy()
    i = 0
    while i < len(originalContent):
        originalContent.insert(i, '//')
        searchContent.insert(i, '//' + search)
        i += (searchInterval + 1)

    originalEntropies = calculatelEntropiesOfString("\n".join(originalContent), 'original.java')
    searchEntropies = calculatelEntropiesOfString("\n".join(searchContent), 'search.java')

    ret = {}
    ret['originalContent'] = (originalContent)
    ret['searchContent'] = (searchContent)
    ret['originalEntropy'] = [custom_to_dict(custom) for custom in originalEntropies]
    ret['searchEntropy'] = [custom_to_dict(custom) for custom in searchEntropies]

    encoded = json.dumps(ret)
    return encoded

# Calculates and retun the entopies of a given inputfile
def calculatelEntropies(inputPath):
    only_aggregated_entropies = False
    if only_aggregated_entropies :
        entropies = get_entropy_for_each_line(model, inputPath, False, True)  
        return entropies
    else:
        entropies = get_entropy_for_each_line(model, inputPath, False, False)  
        print("Entropies Calculated....======================================") 
        # print(entropies)

    return entropies

# Calculates and retun the entopies of a given string - the string is saved to a file (name specified) in the temp folder
def calculatelEntropiesOfString(string, name):
    inputFile = os.path.join(rootPath, 'cache', 'temp', name)

    with open(inputFile, 'w') as outfile:		
        outfile.write(string)
        outfile.close()	

    return calculatelEntropies(inputFile)

@app.route('/autocompletion', methods = ['POST'])
def autocompletion():
    data = json.loads(request.data)
    content = data.get('content', '')
    proposalsCount = int(data.get('proposalsCount', 10))

    completionModel.feed_text(content)

    # this does not change the state of the completionModel:
    predictions = completionModel.predict_next_full_token(n_suggestions = proposalsCount)
    completionModel.reset()

    encoded = json.dumps(predictions)
    return encoded

@app.route('/languagemodel', methods = ['POST'])
def user():
    print("GOT LM REQUEST ========================================================")
    data = json.loads(request.data)

    extension = data.get('extension', '')
    languageId = data.get('languageId', '')
    filePath = data.get('filePath', '')
    noReturn = data.get('noReturn', 'false') == "true"
    timestamp = float(data.get('timestamp', 1))/1000
    content = data.get('content', '')
    workspaceFolder = data.get('workspaceFolder', None)

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

        entropies = calculatelEntropies(savePath) 
        print("entropies calculated")
        
        # write entropies to file (json-format)
        with open(path, 'w') as f:
            json.dump([custom_to_dict(custom) for custom in entropies], f)
            f.close()	

    if noReturn == True:
        print("NO return data...")
    else:
        with open(path, 'r') as content_file:
            return content_file.read()

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
    print("Loading Language Model")
    model = TrainedModel.get_default_model() # get_tiny_model()
    print("Loading Completion-Language Model")
    completionModel = TrainedModel.get_default_model() # get_tiny_model()
    print("Language Model loaded")

    app.run(use_reloader=True, port=PORT) #host='0.0.0.0'
