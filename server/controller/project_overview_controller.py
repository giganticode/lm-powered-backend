import os
from flask import Flask, render_template, request, url_for, json, redirect, jsonify
from flask_cors import CORS

class ProjectOverviewController:
    def __init__(self, root_path, files):
        self.root_path = root_path
        self.files = files

    def get_projects(self):
        projects = [{'name': self.files[hash]['name'], 'path': self.files[hash]['uri']['path'], 'url': hash} for hash in self.files.keys()]
        response = jsonify(projects)
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response

    def get_project_files(self, projecthash):
        project = self.files[projecthash]
        response = jsonify(project)
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response   

    def get_project_file_detail(self, projecthash, filehash):
        project = self.files[projecthash]
        file = project['files'][filehash]

        file_entropy_path = os.path.join(self.root_path, 'cache', 'output', projecthash, filehash)
        entropies = []

        if os.path.isfile(file_entropy_path):
            with open(file_entropy_path, 'r') as f:
                entropies = json.load(f)
                f.close()

        response = jsonify({
            'file': file,
            'entropies': entropies
        })

        response.headers.add('Access-Control-Allow-Origin', '*')
        return response         