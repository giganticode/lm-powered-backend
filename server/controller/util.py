import os

def check_or_create(path): 
    if not os.path.exists(path):
        os.makedirs(path)