import json
import os

import kernel.config as Config

def read(key: str, regloc: str = Config.get("registry"), default=None, writeDefault=False):
    key = key.replace(".", "/")
    if not os.path.exists(os.path.join(regloc, key)):
        if writeDefault:
            write(key, default, regloc)
        return default

    # If regloc is directory, read list of files excluding directory and names starting with .
    if os.path.isdir(os.path.join(regloc, key)):
        listOfFiles: list = []
        for file in os.listdir(os.path.join(regloc, key)):
            if os.path.isfile(os.path.join(regloc, key, file)) and not file.startswith("."):
                listOfFiles.append(file + "=" + read(os.path.join(key, file).replace("/", "."), regloc))
            elif os.path.isdir(os.path.join(regloc, key, file)) and not file.startswith("."):
                listOfFiles.append(file)
                
        return listOfFiles
        
    with open(os.path.join(regloc, key), 'r') as f:
        if os.path.isfile(os.path.join(regloc, key)):
            return f.read()
        
        else:
            if writeDefault:
                write(key, default, regloc)
            return default

def isKey(key: str, regloc: str = Config.get("registry")) -> int:
    key = key.replace(".", "/")
    if not os.path.exists(os.path.join(regloc, key)):
        return 0
    if os.path.isdir(os.path.join(regloc, key)):
        return 1
    else:
        return 2
    
def write(key: str, value = None, regloc: str = Config.get("registry")):
    key = key.replace(".", "/")

    # If key starts with ? and already exists, return
    if key.startswith("?") and os.path.exists(os.path.join(regloc, key[1:])):
        return
    
    # If parent directory does not exist, create all parent directories
    for i in range(len(key.split("/"))):
        if not os.path.exists(os.path.join(regloc, "/".join(key.split("/")[:i]))):
            os.mkdir(os.path.join(regloc, "/".join(key.split("/")[:i])))
    
    
    # If value is none, create directory
    if value is None:
        os.mkdir(os.path.join(regloc, key))
        return
    
    else:
        with open(os.path.join(regloc, key), 'w') as f:
            if type(value) is list:
                f.write("\n".join(value))
            elif type(value) is dict:
                f.write(json.dumps(value))
            else:
                f.write(value)

def delete(key: str, deleteSubkeys: bool = False, regloc: str = Config.get("registry")):
    key = key.replace(".", "/")
    if not os.path.exists(os.path.join(regloc, key)):
        return
    
    if os.path.isfile(os.path.join(regloc, key)):
        os.remove(os.path.join(regloc, key))
    else:
        if deleteSubkeys:
            for file in os.listdir(os.path.join(regloc, key)):
                if os.path.isfile(os.path.join(regloc, key, file)):
                    os.remove(os.path.join(regloc, key, file))
                else:
                    delete(os.path.join(key, file), deleteSubkeys, regloc)
        os.rmdir(os.path.join(regloc, key))
                
def listSubKeys(key: str, subdirectories: list = [], regloc: str = Config.get("registry")) -> list:
    key = key.replace(".", "/")
    if not os.path.exists(os.path.join(regloc, key)):
        return []
        
    listOfFiles: list = []
    for file in os.listdir(os.path.join(regloc, key)):
        if os.path.isfile(os.path.join(regloc, key, file)) and not file.startswith("."):
            listOfFiles.append(file.replace("/", ".") + "=" + read(os.path.join(key, file).replace("/", "."), regloc))
        elif os.path.isdir(os.path.join(regloc, key, file)) and not file.startswith("."):
            listSubKeys(os.path.join(key, file), subdirectories, regloc)
            
    return listOfFiles
    

def build(blueprintPath: str, registryPath: str = Config.get("registry"), silent=False):
    lines: list = []
    with open(blueprintPath, 'r') as f:
        conf: list = f.readlines()
        for line in conf:
            if line.startswith("#"):
                continue
            if line.strip() == "":
                continue
            lines.append(line.strip())
            
    for line in lines:
        key = line.split("=")[0]
        value = line.split("=")[1] if len(line.split("=")) > 1 else None
        if not silent: print(f"[ Generate ] {key}")
        write(key, value, registryPath)
        
