import os
import hashlib 
from flask import Flask, render_template, request, url_for, json, redirect, jsonify
from flask_cors import CORS
from .stopwatch import StopWatch
from langmodels.evaluation.evaluation import evaluate_model_on_string, evaluate_model_on_file, evaluate_model_on_path
from langmodels.evaluation.metrics import EvaluationResult, TokenTypes, EvaluationScenario
from langmodels.model import TrainedModel, ModelDescription
from util.entropyresult import EntropyResult, EntropyLine, Token
from controller.util import check_or_create

class EntropyController:
    def __init__(self, root_path, models, files):
        self.root_path = root_path
        self.models = models

        self.files = files
        self.files_json_path = os.path.join(self.root_path, 'files.json')

    def save_files(self):
        with open(self.files_json_path, 'w') as outfile:		
            json.dump(self.files, outfile)	
            outfile.close()	

    def get_predictions(self, request, models):
        sw = StopWatch()
        sw.start()
        metadata = {}

        stop_watch = StopWatch()
        stop_watch.start()

        data = json.loads(request.data)
        language_id = data.get('languageId', '')
        content = data.get('content', '')
        reset_context = data.get('resetContext', 'false') == "true"
        proposals_count = int(data.get('proposalsCount', 10))
        selected_model_name = data.get('model', list(self.models.keys())[0])
        selected_model = self.models[selected_model_name]

        model = selected_model.get_model()
        metadata['time_model_loading'] = stop_watch.elapsed() * 1000

        stop_watch.start()
        model.feed_text(content)
        metadata['time_feed'] = stop_watch.elapsed() * 1000

        stop_watch.start()
        predictions = model.predict_next_full_token(n_suggestions = proposals_count)
        
        if reset_context == True:
            model.reset()

        metadata['time_predictions'] = stop_watch.elapsed() * 1000
        metadata['total'] = sw.elapsed() * 1000

        response = jsonify({
                    'predictions': predictions,
                    'metadata': metadata,
                    'languagemodel': selected_model_name
                })
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response       

    def get_search(self, request, models):
        sw = StopWatch()
        sw.start()
        stop_watch = StopWatch()
        stop_watch.start()
        metadata = {}

        data = json.loads(request.data)
        content = data.get('content', '')
        # timestamp = float(data.get('timestamp', 1))/1000
        language_id = data.get('languageId', '')
        search = data.get('search', '')
        reset_context = parse_bool(data.get('resetContext', False))
        metrics = data.get('metrics', 'full_token_entropy')
        token_type_raw = data.get('tokenType', 'all')
        token_type = parse_token_type(token_type_raw)
        search_interval = int(data.get('searchInterval', 10))
        selected_model_name = data.get('model', list(models.keys())[0])
        selected_model = models[selected_model_name]

        model = selected_model.get_model()
        metadata['time_model_loading'] = stop_watch.elapsed() * 1000

        lines = content.splitlines()
        originalContent = lines.copy()
        searchContent = lines.copy()

        i = 0
        while i < len(originalContent):
            originalContent.insert(i, '//')
            searchContent.insert(i, '//' + search)
            i += (search_interval + 1)

        stop_watch.start()
        original_entropies = calculatel_entropies_of_string(selected_model_name, model, "\n".join(originalContent), 'java', metrics = metrics, token_types = token_type)
        if reset_context == True:
            model.reset()
        metadata['time_original_entropies'] = stop_watch.elapsed() * 1000

        stop_watch.start()
        search_entropies = calculatel_entropies_of_string(selected_model_name, model, "\n".join(searchContent), 'java', metrics = metrics, token_types = token_type)
        if reset_context == True:
            model.reset()
        metadata['time_search_entropies'] = stop_watch.elapsed() * 1000

        ret = {}
        ret['original'] = original_entropies
        ret['search'] = search_entropies
        metadata['total'] = sw.elapsed() * 1000

        response = jsonify({
            'entropies': ret,
            'metadata': metadata,
            'searchquery': search,
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response        

    def get_compare(self, request, models):
        stop_watch = StopWatch()
        sw = StopWatch()
        sw.start()
        data = json.loads(request.data)
        metadata = {}

        language_id = data.get('languageId', '')
        content = data.get('content', '')
        reset_context = parse_bool(data.get('resetContext', False))
        metrics = data.get('metrics', 'full_token_entropy')
        token_type_raw = data.get('tokenType', 'all')
        token_type = parse_token_type(token_type_raw)
        selected_model_name1 = data.get('model1', list(models.keys())[0])
        selected_model_name2 = data.get('model2', list(models.keys())[0])

        selected_model1 = models[selected_model_name1]
        selected_model2 = models[selected_model_name2]

        stop_watch.start()
        model1 = selected_model1.get_model()
        metadata['time_model1_loading'] = stop_watch.elapsed() * 1000

        stop_watch.start()
        model2 = selected_model2.get_model()
        metadata['time_model2_loading'] = stop_watch.elapsed() * 1000

        if not language_id.lower() in ['java']:
            print("language " + language_id + " not supported")
            return {'error': 'language not supported yet'}, 406

        stop_watch.start()
        entropies1 = calculatel_entropies_of_string(selected_model_name1, model1, content, language_id, metrics = metrics, token_types = token_type) 
        if (reset_context):
            model1.reset()
        metadata['time_entropy1_calculation'] = stop_watch.elapsed() * 1000

        stop_watch.start()
        entropies2 = calculatel_entropies_of_string(selected_model_name2, model2, content, language_id, metrics = metrics, token_types = token_type) 
        if (reset_context):
            model2.reset()
        metadata['time_entropy2_calculation'] = stop_watch.elapsed() * 1000
        metadata['total'] = sw.elapsed() * 1000

        response = jsonify({
            'entropies1': entropies1,
            'entropies2': entropies2,
            'metadata': metadata,
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response   
        
    def get_entropies(self, request, models):
        print("GOT LM REQUEST ========================================================")
        sw = StopWatch()
        sw.start()
        stop_watch = StopWatch()
        stop_watch.start()
        metadata = {}

        data = json.loads(request.data)
        language_id = data.get('languageId', '')
        file_path = data.get('filePath', '')
        no_return = data.get('noReturn', 'false') == "true"
        timestamp = float(data.get('timestamp', 1))/1000
        content = data.get('content', '')
        reset_context = parse_bool(data.get('resetContext', False))
        metrics = data.get('metrics', 'full_token_entropy')
        token_type_raw = data.get('tokenType', 'all')
        token_type = parse_token_type(token_type_raw)
        workspace_folder = data.get('workspaceFolder', None)
        selected_model_name = data.get('model', list(models.keys())[0])
        selected_model = models[selected_model_name]
        model = selected_model.get_model()
        metadata['time_model_loading'] = stop_watch.elapsed() * 1000

        if not language_id.lower() in ['java']:
            print("language " + language_id + " not supported")
            return {'error': 'language not supported yet'}, 406

        shouldCalculateEntropies = True

        # distinguish debugging requests and requests from VSC
        if workspace_folder:
            hashed_name = hashlib.md5(file_path.encode()).hexdigest() 
            project_hash = hashlib.md5(workspace_folder['uri']['fsPath'].encode()).hexdigest()
            output_path = os.path.join(self.root_path, 'cache', project_hash, hashed_name)

            if self.files.get(project_hash, None) == None:
                self.files[project_hash] = workspace_folder
                self.files[project_hash]['files'] = {}

            self.files[project_hash]['files'][hashed_name] = {
                'path': file_path, 
                'name': os.path.basename(file_path), 
                'relpath': os.path.relpath(file_path, workspace_folder['uri']['fsPath'])}

            self.save_files()
        
            if os.path.isfile(output_path):
                modTimesinceEpoc = os.path.getmtime(output_path)
                
                if modTimesinceEpoc < timestamp:
                    print("file has been modified -> recalculate entropies")
                else:
                    print("file has NOT been modified -> recalculation not needed")
                    shouldCalculateEntropies = False

        entropies = None
        if shouldCalculateEntropies:
            stop_watch.start()
            entropies = calculatel_entropies_of_string(selected_model_name, model, content, language_id, metrics = metrics, token_types = token_type) 
            if (reset_context):
                model.reset()

            metadata['time_entropy_calculation'] = stop_watch.elapsed() * 1000

            # save file:
            if workspace_folder:
                check_or_create(os.path.dirname(output_path))
            
                # write entropies to file (json-format)
                with open(output_path, 'w') as f:
                    json.dump(entropies, f)
                    f.close()	

        metadata['total'] = sw.elapsed() * 1000

        if no_return == True:
            print("NO return data...")
            response = jsonify({'success': 'true'})
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response
        else:
            if entropies == None:
                # read cached values from cache-directory
                with open(output_path, 'r') as content_file:
                    entropies = content_file.read()
                    ret = {}
                    ret['entropies'] = json.loads(entropies)
                    ret['metadata'] = metadata
                    response = jsonify(ret)
                    content_file.close()
            else:
                response = jsonify({
                    'entropies': entropies,
                    'metadata': metadata,
                })

            response.headers.add('Access-Control-Allow-Origin', '*')
            return response

# calculates the entropy of a string: important -> only one type of metrics and tokentype
def calculatel_entropies_of_string(languagemodel_name: str, model: TrainedModel, text: str, extension = 'java', metrics = 'full_token_entropy', token_types = TokenTypes.ALL):
    entropies = evaluate_model_on_string(model, text, extension, metrics = {metrics}, token_types = {token_types}) #, token_types={TokenTypes.ALL, TokenTypes.ONLY_COMMENTS, TokenTypes.ALL_BUT_COMMENTS})  # full_token_entropy, subtoken_entropy, mrr

    # convert result to the predefined structure
    result = EntropyResult(languagemodel_name, metrics, token_types)
    scenario = EvaluationScenario(metric_name = metrics, token_types = token_types.value)
    for line in entropies:
        text = line.text
        average = line.scenarios[scenario].average
        l = EntropyLine(text, average)
        for (index, sub_token) in enumerate(line.scenarios[scenario].subtoken_values):
            t = line.prep_text[index]
            l.tokens.append(Token(t, sub_token))
        result.lines.append(l)

    return result
    
def parse_bool(s):
    if isinstance(s, bool):
        return s
    if s.lower() == 'true':
        return True
    else:
        return False

def parse_token_type(s) -> TokenTypes:
    if s.lower() == 'only_comments':
        return TokenTypes.ONLY_COMMENTS
    elif s.lower() == 'all_but_comments':
        return TokenTypes.ALL_BUT_COMMENTS
    else:
        return TokenTypes.ALL