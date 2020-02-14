import argparse
import logging
import os
from multiprocessing.managers import BaseManager

from codeprep.tokens.rootclasses import ParsedToken
from flask import Flask
from flask import request, json, jsonify
from flask import session
from flask_cors import CORS
from flask_session import Session
from langmodels import repository
from langmodels.evaluation.customization import all_subclasses

from controller.risk import risk
from controller.search import search
from core import calculate_entropies_of_string

logger = logging.getLogger()

PORT = 8080

app = Flask(__name__, static_folder='')
SESSION_TYPE = 'memcached'
app.config.from_object(__name__)
Session(app)

cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
rootPath = os.path.dirname(os.path.realpath(__file__))
manager = BaseManager(('', 37844), b'password')


def load_files(path):
    files_json_path = os.path.join(path, 'files.json')
    if os.path.exists(files_json_path):
        with open(files_json_path, 'r') as json_files:
            try:
                return json.load(json_files)
            except:
                return {}


@app.before_first_request
def init():
    manager.register('get_model_for_user')
    manager.register('release_model')
    manager.register('change_preferred_model')
    manager.connect()


@app.route('/api/models')
def api_models():

    response = jsonify({
                'models': repository.query_all_models(),
            })
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


@app.route('/api/token-types')
def api_token_types():
    response = jsonify(list(map(lambda c: c.__name__, all_subclasses([ParsedToken]))))
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


@app.route('/api/projects', methods=['GET'])
def api_projects():
    files = load_files(rootPath)
    projects = [{'name': files[hash]['name'],
                 'path': files[hash]['uri']['path'],
                 'url': hash} for hash in files.keys()]
    response = jsonify(projects)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


@app.route('/api/project/<projecthash>', methods = ['GET'])
def api_project_files(projecthash):
    files = load_files(rootPath)
    project = files[projecthash]
    response = jsonify(project)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


@app.route('/api/project/<projecthash>/<filehash>', methods = ['GET'])
def api_project_file_detail(projecthash, filehash):
    files = load_files(rootPath)
    project = files[projecthash]
    file = project['files'][filehash]

    file_entropy_path = os.path.join(rootPath, 'cache', projecthash, filehash)
    entropies = []

    if os.path.isfile(file_entropy_path):
        with open(file_entropy_path, 'r') as f:
            entropies = json.load(f)

    response = jsonify({
        'file': file,
        'entropies': entropies
    })

    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


@app.route('/api/autocompletion', methods=['POST'])
def api_autocompletion():
    model = manager.get_model_for_user(session.sid, 'autocompletion')

    data = json.loads(request.data)
    content = data.get('content', '')
    language_id = data.get('languageId', '')
    proposals_count = int(data.get('proposalsCount', 10))

    model.feed_text(content, extension=language_id)
    predictions = model.predict_next_full_token(n_suggestions=proposals_count)
    model.reset()

    response = jsonify({'predictions': predictions})
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


@app.route('/api/risk', methods=['POST'])
def api_risk():
    data = json.loads(request.data)
    language_id = data.get('languageId', '')
    file_path = data.get('filePath', '')
    no_return = data.get('noReturn', 'false') == "true"
    timestamp = float(data.get('timestamp', 1))/1000
    content = data.get('content', '')
    metrics = data.get('metrics', 'full_token_entropy')
    workspace_folder = data.get('workspaceFolder', None)

    model = manager.get_model_for_user(session.sid, 'risk')

    if not language_id.lower() in ['java']:
        logger.warning("language " + language_id + " not supported")
        return {'error': 'language not supported yet'}, 406

    files = load_files(rootPath)

    entropies = risk(workspace_folder, file_path, content, files, rootPath, timestamp, model, language_id, metrics)

    response = {jsonify({})} if no_return else jsonify({'entropies': entropies})
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


@app.route('/api/compare', methods=['POST'])
def api_compare():
    data = json.loads(request.data)

    language_id = data.get('languageId', '')
    content = data.get('content', '')
    metrics = data.get('metrics', 'full_token_entropy')
    model1_id = data.get('model1', '')
    model2_id = data.get('model2', '')

    manager.change_preferred_model(session.sid, 'compare.1', model1_id)
    manager.change_preferred_model(session.sid, 'compare.2', model2_id)

    model = manager.get_model_for_user(session.sid, 'compare.1')
    model2 = manager.get_model_for_user(session.sid, 'compare.2')

    if not language_id.lower() in ['java']:
        logger.warning("language " + language_id + " not supported")
        return {'error': 'language not supported yet'}, 406

    entropies1 = calculate_entropies_of_string(model, content, language_id, metrics = metrics)
    model.reset()

    entropies2 = calculate_entropies_of_string(model2, content, language_id, metrics = metrics)
    model2.reset()

    manager.release_model(model)
    manager.release_model(model2)

    response = jsonify({
        'entropies1': entropies1,
        'entropies2': entropies2
    })
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


@app.route('/api/search', methods=['POST'])
def api_search():

    data = json.loads(request.data)

    content = data.get('content', '')
    search_phrase = data.get('search_phrase', '')
    metrics = data.get('metrics', 'full_token_entropy')
    search_interval = int(data.get('searchInterval', 10))

    model = manager.get_model_for_user(session.sid, 'search')

    original_entropies, search_entropies = search(content, search_phrase, model, search_interval, metrics)
    response = jsonify({
        'entropies': {'original': original_entropies, 'search': search_entropies},
        'searchquery': search_phrase,
    })
    response.headers.add('Access-Control-Allow-Origin', '*')

    manager.release_model(session.sid, 'search')
    return response


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', default=False, action='store_true', help='Start the server in debug mode.')
    parser.add_argument('--port', default=PORT, type=int, action='store', help='Set the port for of the web server.')
    parser.add_argument('--host', default='127.0.0.1', type=str, action='store', help='Set the host of the web server.')
    parser.set_defaults()
    args = parser.parse_args()

    app.run(use_reloader=args.debug, port=args.port, debug=args.debug, host=args.host)

    logging.info(f"LM-powered server strated at {args.host}:{args.port}")
