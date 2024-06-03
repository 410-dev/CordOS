# Open etc/config.json and check if the config is valid
# If etc/config.json does not exist, copy defaults/config.json to etc/config.json

import json
import shutil
import os
import sys

# Read if commandline argument contains: --fix-corruption
fixCorruption: bool = False
if len(sys.argv) > 1:
    for arg in sys.argv:
        if arg == '--fix-corruption':
            fixCorruption = True
            break

# Open etc/servers.json
fileFound: bool = False
servers = None
try:
    with open('etc/servers.json') as f:
        servers = json.load(f)
        fileFound = True
        
except FileNotFoundError:
    fileFound = False
    

except:
    if fixCorruption:
        # Delete etc/servers.json
        print("Deleting etc/servers.json")
        try:
            os.remove('etc/servers.json')
        except:
            print("Error deleting etc/servers.json")
        fileFound = False
    else:
        print("Error opening etc/servers.json")
        exit(3)

if not fileFound:
    print('etc/servers.json does not exist. Copying defaults/servers.json to etc/servers.json')
    shutil.copy('defaults/servers.json', 'etc/servers.json')
    
    # Remove default=True from etc/servers.json
    with open('etc/servers.json') as f:
        servers = json.load(f)
        servers.pop('default')
        servers['servers'] = []
        
        with open('etc/servers.json', 'w') as f:
            json.dump(servers, f, indent=4)


# Open etc/config.json
fileFound: bool = False
config = None
try:
    with open('etc/config.json') as f:
        config = json.load(f)
        config_parser = config['config_parser']
        envVarKeyword = config_parser['env_trigger']
        fileFound = True
        
except FileNotFoundError:
    fileFound = False
    
except:
    if fixCorruption:
        # Delete etc/config.json
        print("Deleting etc/config.json")
        try:
            os.remove('etc/config.json')
        except:
            print("Error deleting etc/config.json")
        fileFound = False
    else:
        print("Error opening etc/config.json")
        exit(4)
    
if not fileFound:
    print('etc/config.json does not exist. Copying defaults/config.json to etc/config.json')
    shutil.copy('defaults/config.json', 'etc/config.json')
    
    # Remove default=True from etc/config.json
    with open('etc/config.json') as f:
        config = json.load(f)
        config.pop('default')
        
        with open('etc/config.json', 'w') as f:
            json.dump(config, f, indent=4)
            
    exit(1)

for key in config:
    print("Checking key", key, "for environment variable")
    get = config[key]
    if isinstance(get, str):
        if get.startswith(envVarKeyword):
            envVar = get.replace(envVarKeyword, '')
            print("Checking environment variable", envVar)
            if envVar not in os.environ:
                print('Environment variable', envVar, 'not found.')


print("Checking required keys for configurations...")
requiredKeys = ["registry", "config_parser"]
requiredKeysMissing: bool = False
for key in requiredKeys:
    print(f"Checking config key: {key}")
    if key not in config:
        print("\nAssertion Error: Key", key, "not found in config")
        requiredKeysMissing = True
if requiredKeysMissing:
    exit(5)

import kernel.registry as Registry

if not os.path.exists(config['registry']) or not os.path.isdir(config['registry']):
    print(f"{config['registry']} does not exist or is not a directory. Creating {config['registry']}")
    os.mkdir(config['registry'])
    Registry.build('defaults/registry.cordreg', config['registry'])

print("Checking required registries...")

blueprintList: list = []
with open("defaults/registry.cordreg", 'r') as f:
    conf: list = f.readlines()
    for line in conf:
        if line.startswith("#"):
            continue
        if line.strip() == "":
            continue
        blueprintList.append(line.strip())

for reg in blueprintList:
    try:
        regn = reg.split("=")[0]

        # If registry is optional, it starts with a question mark
        optional = regn.startswith("?")
        if optional: regn = regn[1:]

        regVal = Registry.read(regn)
        if regVal == None or not optional:
            value = reg.split("=")[1] if len(reg.split("=")) > 1 else None
            Registry.write(regn, value, config['registry'])
            if not optional:
                print("[  Passed  ] " + regn)
            else:
                print("[ Upgraded ] " + regn)
        else:
            print("[  Passed  ] " + regn)
        
    except Exception as e:
        print("Upgrade Error")

# Check for dependencies installed in pip
# read requirements.txt
print("Checking for dependencies...")
missingDependencies: list = []
try:
    with open('requirements.txt', 'r') as f:
        reqs = f.readlines()

        # Read the result of "pip3 list" and check if the dependencies are installed
        listInstalled: list = []
        try:
            import subprocess
            result = subprocess.run(['pip3', 'list'], capture_output=True, text=True)
            listInstalled = result.stdout.split("\n")
        except:
            print("Error reading pip3 list")
            exit(7)
        
        for index, installed in enumerate(listInstalled):
            if installed.startswith("Package"):
                continue
            if installed.strip() == "":
                continue
            if installed.startswith("["):
                continue
            if installed.startswith("-"):
                continue
            listInstalled[index] = installed.split(" ")[0]
            print(f"[  Found   ] {listInstalled[index]}")

        for req in reqs:
            req = req.strip()
            if req == "":
                continue
            if req.startswith("#"):
                continue
            if req in listInstalled:
                print(f"[  Passed  ] Found: {req}")
            else:
                print(f"\033[0;31m[  Failed  ] Missing: {req}\033[0m")
                missingDependencies.append(req)

                
except FileNotFoundError:
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    print("[WARNING] requirements.txt not found")
    print("          Failed checking for dependencies, and may corrupt the configuration")
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

if len(missingDependencies) > 0:
    print("\033[0;31mMissing dependencies found in requirements.txt\033[0m")
    print("\033[0;31mMissing dependencies:", missingDependencies, "\033[0m")
    exit(8)

# Success  
exit(0)
