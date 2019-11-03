import os
from flask import Flask, render_template, request, url_for, json, redirect, jsonify
from flask_cors import CORS
from .stopwatch import StopWatch
from langmodels.evaluation.evaluation import evaluate_model_on_string, evaluate_model_on_file, evaluate_model_on_path
from langmodels.evaluation.common import EvaluationResult, TokenTypes
from langmodels.model import TrainedModel, ModelDescription

class EntropyController:
    def __init__(self, root_path, models):
        self.root_path = root_path
        self.models = models

    def get_predictions(self, request, models):
        sw = StopWatch()
        sw.start()
        metadata = {}

        stop_watch = StopWatch()
        stop_watch.start()

        data = json.loads(request.data)
        # extension = data.get('extension', '')
        # language_id = data.get('languageId', '')
        # timestamp = float(data.get('timestamp', 1))/1000
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
                    'metadata': metadata
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
        # extension = data.get('extension', '')
        # language_id = data.get('languageId', '')
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
        originalEntropies = calculatelEntropiesOfString(model, "\n".join(originalContent), 'java', metrics = {metrics}, token_types = {token_type})
        if reset_context == True:
            model.reset()
        metadata['time_original_entropies'] = stop_watch.elapsed() * 1000

        stop_watch.start()
        searchEntropies = calculatelEntropiesOfString(model, "\n".join(searchContent), 'java', metrics = {metrics}, token_types = {token_type})
        if reset_context == True:
            model.reset()
        metadata['time_search_entropies'] = stop_watch.elapsed() * 1000

        ret = {}
        ret['originalContent'] = (originalContent)
        ret['searchContent'] = (searchContent)
        ret['originalEntropy'] = [entropy_to_dict(custom) for custom in originalEntropies]
        ret['searchEntropy'] = [entropy_to_dict(custom) for custom in searchEntropies]
        metadata['total'] = sw.elapsed() * 1000

        response = jsonify({
            'entropies': ret,
            'metadata': metadata,
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response        

    def get_compare(self, request, models):
        stop_watch = StopWatch()
        sw = StopWatch()
        sw.start()
        data = json.loads(request.data)
        metadata = {}

        # timestamp = float(data.get('timestamp', 1))/1000
        # extension = data.get('extension', '')
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
            return {'error': 'language not supported yet'}, 404

        stop_watch.start()
        entropies1 = calculatelEntropiesOfString(model1, content, language_id, metrics = {metrics}, token_types = {token_type}) 
        entropies1 = [entropy_to_dict(custom) for custom in entropies1]
        if (reset_context):
            model1.reset()
        metadata['time_entropy1_calculation'] = stop_watch.elapsed() * 1000

        stop_watch.start()
        entropies2 = calculatelEntropiesOfString(model2, content, language_id, metrics = {metrics}, token_types = {token_type}) 
        entropies2 = [entropy_to_dict(custom) for custom in entropies2]
        if (reset_context):
            model2.reset()
        metadata['time_entropy2_calculation'] = stop_watch.elapsed() * 1000
        metadata['total'] = sw.elapsed() * 1000

        response = jsonify({
            'entropies1': entropies1,
            'entropies2': entropies2,
            'metadata': metadata
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
        # extension = data.get('extension', '')
        language_id = data.get('languageId', '')
        # file_path = data.get('filePath', '')
        # no_return = data.get('noReturn', 'false') == "true"
        # timestamp = float(data.get('timestamp', 1))/1000
        content = data.get('content', '')
        reset_context = parse_bool(data.get('resetContext', False))
        metrics = data.get('metrics', 'full_token_entropy')
        token_type_raw = data.get('tokenType', 'all')
        token_type = parse_token_type(token_type_raw)
        # workspaceFolder = data.get('workspaceFolder', None)
        selected_model_name = data.get('model', list(models.keys())[0])
        selected_model = models[selected_model_name]
        print(metrics)
        model = selected_model.get_model()
        metadata['time_model_loading'] = stop_watch.elapsed() * 1000

        # sw_entropy_calculation = 0

        if not language_id.lower() in ['java']:
            print("language " + language_id + " not supported")
            return {'error': 'language not supported yet'}, 404

        # shouldCalculateEntropies = True

        #check if file is cached
        # hashedName = hashlib.md5(filePath.encode()).hexdigest()  # str(hash(filePath))

        # if workspaceFolder:
        #     projectHash = hashlib.md5(workspaceFolder['uri']['fsPath'].encode()).hexdigest()

        #     if files.get(projectHash, None) == None:
        #         files[projectHash] = workspaceFolder
        #         files[projectHash]['files'] = {}

        #     files[projectHash]['files'][hashedName] = {
        #         'path': filePath, 
        #         'name': os.path.basename(filePath), 
        #         'relpath': os.path.relpath(filePath, workspaceFolder['uri']['fsPath'])}

        #     with open(os.path.join(rootPath, 'files.json'), 'w') as outfile:		
        #         json.dump(files, outfile)	
        #         outfile.flush()
        #         outfile.close()	
            
        #     path = os.path.join(rootPath, 'cache', 'output', projectHash, hashedName)
        
        # else:
        #     path = os.path.join(rootPath, 'cache', 'output', 'temp', hashedName)
        
        # if os.path.isfile(path):
        #     modTimesinceEpoc = os.path.getmtime(path)
            
        #     if modTimesinceEpoc < timestamp:
        #         print("file has been modified -> recalculate entropies")
        #     else:
        #         print("file has NOT been modified -> recalculation not needed")
        #         shouldCalculateEntropies = False

        # if shouldCalculateEntropies:
        #     # save file:
        #     if workspaceFolder:
        #         savePath = os.path.join(rootPath, 'cache', 'input', projectHash, hashedName)
        #     else:
        #         savePath = os.path.join(rootPath, 'cache', 'input', 'temp', hashedName)

        #     checkOrCreate(os.path.dirname(savePath))
        #     checkOrCreate(os.path.dirname(path))

        #     f = open(savePath,"w")
        #     f.write(content)
        #     f.close()

        #     stop_watch.start()
        #     entropies = calculatelEntropiesOfString(model, content, languageId) 
        #     sw_entropy_calculation = stop_watch.elapsed()
        #     print("entropies calculated")
        #     print("ENTROPIES")
        #     print(entropies)
            
        #     # write entropies to file (json-format)
        #     with open(path, 'w') as f:
        #         json.dump([entropy_to_dict(custom) for custom in entropies], f)
        #         f.close()	

        stop_watch.start()
        entropies = calculatelEntropiesOfString(model, content, language_id, metrics = {metrics}, token_types = {token_type}) 
        if (reset_context):
            model.reset()

        metadata['time_entropy_calculation'] = stop_watch.elapsed() * 1000
        metadata['total'] = sw.elapsed() * 1000

        # if no_return == True:
        #     print("NO return data...")
        # else:
        #     with open(path, 'r') as content_file:
        #         entropies = content_file.read()
        #         entropies = json.loads(entropies)
        #         response = jsonify({
        #             'entropies': entropies,
        #             'metadata': {
        #                 'time_model_loading': sw_model_loading * 1000,
        #                 'time_entropy_calculation': sw_entropy_calculation * 1000,   
        #                 'total': sw.elapsed() * 1000
        #             },
        #         })
        #         response.headers.add('Access-Control-Allow-Origin', '*')
        #         return response

        # return "request processed"
        # print("ENTROPIES CALCULATED")
        # print(entropies)

        # encoded_entropies = [entropy_to_dict(custom) for custom in entropies]
        # print("ENCODED")
        # print(encoded_entropies)
        response = jsonify({
                    'entropies': [entropy_to_dict(custom) for custom in entropies],
                    'metadata': metadata,
                })
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response

# REGION languagemode utilities
def calculatelEntropiesOfString(model: TrainedModel, text: str, extension = 'java', metrics = {'full_token_entropy'}, token_types = {TokenTypes.ALL}):
    entropies = evaluate_model_on_string(model, text, extension, metrics = metrics, token_types = token_types) #, token_types={TokenTypes.ALL, TokenTypes.ONLY_COMMENTS, TokenTypes.ALL_BUT_COMMENTS})  # full_token_entropy, subtoken_entropy, mrr
    return entropies
    
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

def entropy_to_dict(custom):
    scenarios = {}
    for key in list(custom.scenarios.keys()):
        evaluation_result = custom.scenarios.get(key)
        scenarios[str(key)] = {
            'subtoken_values': evaluation_result.subtoken_values,
            'average': evaluation_result.average,
            'n_samples': evaluation_result.n_samples,
        }
    return {
        'text': custom.text,
        'prep_text': custom.prep_text,
        'scenarios': scenarios,
        'prep_metadata': {'word_boundaries': custom.prep_metadata.word_boundaries, 'nonprocessable_tokens': list(custom.prep_metadata.nonprocessable_tokens)},
    }                