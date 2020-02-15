import hashlib
import json
import logging
import os
from typing import Dict

import jsons

from lmpowered.core import calculate_entropies_of_string

logger = logging.getLogger()


def is_file_empty(path: str) -> bool:
    with open(path, 'r') as f:
        return f.read() == ''


def risk(workspace_folder: Dict, file_path: str, content: str, files: Dict, root_path: str,
         timestamp, model, language_id, metrics):
    should_calculate_entropies = True

    # distinguish debugging requests and requests from VSC
    if workspace_folder:
        hashed_name = hashlib.md5(file_path.encode()).hexdigest()
        project_hash = hashlib.md5(workspace_folder['uri']['fsPath'].encode()).hexdigest()
        cached_file = os.path.join(root_path, 'cache', project_hash, hashed_name)

        if files.get(project_hash, None) is None:
            files[project_hash] = workspace_folder
            files[project_hash]['files'] = {}

        files[project_hash]['files'][hashed_name] = {
            'path': file_path,
            'name': os.path.basename(file_path),
            'relpath': os.path.relpath(file_path, workspace_folder['uri']['fsPath'])}

        _save_files(files, os.path.join(root_path, 'files.json'))

        if os.path.isfile(cached_file) and not is_file_empty(cached_file):
            modTimesinceEpoc = os.path.getmtime(cached_file)

            if modTimesinceEpoc < timestamp:
                logger.debug(f"File {file_path} has been modified -> recalculate entropies")
            else:
                should_calculate_entropies = False

    if should_calculate_entropies:
        entropies = calculate_entropies_of_string(model, content, language_id, metrics = metrics)

        if workspace_folder:
            _save_entropies_to_file(entropies, cached_file)
    else:
        with open(cached_file, 'r') as content_file:
            content = content_file.read()
            entropies = json.loads(content)
    return entropies


def _save_entropies_to_file(entropies, output_path):
    path = os.path.dirname(output_path)
    if not os.path.exists(path):
        os.makedirs(path)

    with open(output_path, 'w') as f:
        f.write(jsons.dumps(entropies))


def _save_files(files, files_json_path):
    with open(files_json_path, 'w') as outfile:
        outfile.write(jsons.dumps(files))