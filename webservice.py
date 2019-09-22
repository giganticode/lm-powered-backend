import hashlib 
import os
import mimetypes
import sys
from http.server import SimpleHTTPRequestHandler
import urllib.parse as urlparse
import time
from datetime import datetime
import json
from decimal import Decimal
from http.server   import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
import threading
# RegEx
import re

import sys
global rootPath

langModelPath = os.environ.get('LANG_MODEL_PATH')
if langModelPath is None or not os.path.isdir(langModelPath):
    print("the variable 'LANG_MODEL_PATH' is not defined")
    exit()

# demo image
# imgkit.from_string('Hello!', 'out.jpg')

rootPath = os.path.dirname(os.path.realpath(__file__))

old_path = "C:\\xamppServer\\htdocs\\webservice\\langmodels\\analysis"
sys.path.insert(0, old_path)
from langmodels.inference.entropies import get_entropy_for_each_line, word_average, word_entropy_list, subword_average
from langmodels.model import TrainedModel

sys.path.insert(0, langModelPath)
from langmodels.model import TrainedModel as CompletionModel

PORT = 8080
global model
global completionModel
global root
global files

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
    with open(filesJsonPath, 'r') as json_file:
        files = json.load(json_file)
        json_file.close()

checkOrCreate(os.path.join(rootPath, 'cache', 'input', 'full-token-average'))
checkOrCreate(os.path.join(rootPath, 'cache', 'input', 'full-token-entropies'))
checkOrCreate(os.path.join(rootPath, 'cache', 'input', 'subtoken-average'))
checkOrCreate(os.path.join(rootPath, 'cache', 'output', 'full-token-average'))
checkOrCreate(os.path.join(rootPath, 'cache', 'output', 'full-token-entropies'))
checkOrCreate(os.path.join(rootPath, 'cache', 'output', 'subtoken-average'))

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

    # Get-method: only for debugging
    def do_GET(self):
        parsed = urlparse.urlparse(self.path)

        if (self.path and os.path.splitext(self.path)[1]):
            try:
                filepath = self.path
                relPath = os.path.join(rootPath, filepath[1:])
                print(relPath)
                f = open(relPath, 'r')
            except IOError:
                self.send_error(404,'File Not Found: %s ' % filepath)

            else:
                self.send_response(200)
                mimetype, _ = mimetypes.guess_type(filepath)
                self.send_header('Content-type', mimetype)
                self.end_headers()
                for s in f:
                    self.wfile.write(str.encode(s))
                f.close()
            
            return

        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'<html><head><link rel="stylesheet" type="text/css" href="./style.css"></head><body>')

        if (parsed.query and urlparse.parse_qs(parsed.query)['file']):
            hashedName = urlparse.parse_qs(parsed.query)['file'][0]
            print(hashedName)
            self.wfile.write(str.encode("<h1>" + files[hashedName] + "</h1>"))
            self.wfile.write(b'<div class="container"><pre class="entropy">')
            aggregator = 'full-token-average'
            contentFilePath = os.path.join(rootPath, 'cache', 'input', aggregator, hashedName)
            entropyFilePath = os.path.join(rootPath, 'cache', 'output', aggregator, hashedName)
            print(entropyFilePath)

            with open(entropyFilePath, 'r') as content_file:
                s = '</span>\n<span>'
                self.wfile.write(b'<span>')
                self.wfile.write(str.encode(s.join(content_file.read().splitlines())))
                self.wfile.write(b'</span>')
                content_file.close()

            self.wfile.write(b'</pre><pre>')

            with open(contentFilePath, 'r') as content_file:
                s = '</span>\n<span>'
                self.wfile.write(b'<span>')
                self.wfile.write(str.encode(s.join(content_file.read().splitlines())))
                self.wfile.write(b'</span>')
                content_file.close()

            self.wfile.write(b'</pre></div>')

        else:
            for hash in files:
                filePath = files[hash]
                self.wfile.write(str.encode(hash + ' => <a target="_blank" href="/?file=' + hash + '">' + filePath + '</a><br><br>'))

        self.wfile.write(b'</html></body>')


    def do_POST(self):    
        print("Got post =================================================================")
        content_len = int(self.headers.get('Content-Length'))
        post_body = self.rfile.read(content_len).decode('utf-8')
        data = json.loads(post_body)

        # check if autocompletion
        if (self.path and os.path.splitext(self.path)[0]):
            route = os.path.splitext(self.path)[0]

            extension = data['extension']
            languageId = data['languageId']

            if not languageId in ['java', 'JAVA']:
                print("language " + languageId + " not supported")
                self.send_response(406)
                self.end_headers()
                return

            # autocompletion request
            if route.startswith('/autocompletion'):
                content = data['content']

                self.send_response(200)
                self.end_headers()

                completionModel.feed_text(content)

                # this does not change the state of the completionModel:
                predictions = completionModel.predict_next_full_token(n_suggestions=5)
                completionModel.reset()

                encoded = json.dumps(predictions)
                self.wfile.write(encoded.encode())
                return

            # search
            elif  route.startswith('/search'):
                content = data['content']
                search = data['search']
                time.sleep(0.2)
                lines = content.splitlines()
                
                ret = {}
                for index in range(len(lines)):    
                    line = lines[index]
                    x = re.findall(search, line)
                    if (len(x) > 0):
                        ret[index] = 100

                self.send_response(200)
                self.end_headers()

                encoded = json.dumps(ret)
                self.wfile.write(encoded.encode())
                return

            # highlight
            elif  route.startswith('/highlight'):
                # not implemented yet   
                return             

            # codelense
            elif  route.startswith('/codelense'):
                # not implemented yet 
                return

            # risk validation
            elif  route.startswith('/languagemodel'):
                extension = data['extension']
                languageId = data['languageId']
                filePath = data['filePath']
                noReturn = data['noReturn']
                timestamp = data['timestamp']/1000
                aggregator = data['aggregator']
                content = data['content']

                if not languageId in ['java', 'JAVA']:
                    print("language " + languageId + " not supported")
                    self.send_response(406)
                    self.end_headers()
                    return

                shouldCalculateEntropies = True

                #check if file is cached
                hashedName = hashlib.md5(filePath.encode()).hexdigest()  # str(hash(filePath))
                print(hashedName)
                path = os.path.join(rootPath, 'cache', 'output', aggregator, hashedName)
                
                files[hashedName] = filePath
                with open(os.path.join(rootPath, 'files.json'), 'w') as outfile:		
                    json.dump(files, outfile)	
                    outfile.flush()
                    outfile.close()	
                
                if os.path.isfile(path):
                    modTimesinceEpoc = os.path.getmtime(path)
                    
                    if modTimesinceEpoc < timestamp:
                        print("file has been modified...")
                        # calc entropies
                    else:
                        print("file has NOT been modified.")
                        shouldCalculateEntropies = False
                        # return

                if shouldCalculateEntropies:
                    # save file:
                    savePath = os.path.join(rootPath, 'cache', 'input', aggregator, hashedName)
                    f = open(savePath,"w")
                    f.write(content)
                    f.close()

                    entropies = get_entropy_for_each_line(model, savePath, word_average, False)     ## todo agregation function
                    with open(path, 'w') as f:
                        for entropy in entropies:
                            average = 0
                            if (len(entropy) > 0):
                                average = sum(entropy) / len(entropy)
                            
                            f.write(f'{average}\n')
                        f.close()
                        print("entropies written to file")
                    

                self.send_response(200)
                self.end_headers()

                if noReturn:
                    print("NO return data...")
                else:
                    with open(path, 'r') as content_file:
                        content = content_file.read().splitlines()
                        floatList = []
                        for item in content:
                            floatList.append(float(item))

                        encoded = json.dumps(floatList)
                        self.wfile.write(encoded.encode())
                    print("return")

if __name__ == '__main__':
    print("Starting WebServer on Port ", PORT)
    print("Loading Language Model")
    model = TrainedModel.get_default_model()
    completionModel = CompletionModel.get_default_model()
    print("Language Model loaded")

    with HTTPServer(('localhost', PORT), SimpleHTTPRequestHandler) as httpd:
        print("serving at port", PORT)
        httpd.serve_forever()
