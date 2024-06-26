import os
import subprocess
import sys
import shutil

python3 = None
pip3 = None

# Color variables for terminal output
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    NC = '\033[0m'  # No Color

# Function to check if a command exists
def command_exists(cmd):
    return shutil.which(cmd) is not None

# Function to install required components
def install_components():
    try:
        global pip3
        subprocess.check_call([pip3, 'install', '-r', 'requirements.txt'])
        print(f"{Colors.GREEN}Components installed.{Colors.NC}")
        open('etc/pip-done', 'a').close()  # Create the file to indicate components are installed
    except subprocess.CalledProcessError:
        print(f"{Colors.RED}Error: Failed to install components. Exiting...{Colors.NC}")
        sys.exit(2)

# Function to check configuration using preload.py script
def check_configuration(args):
    # result = subprocess.run(['python3', 'preload.py'] + args, capture_output=True)
    global python3
    result = subprocess.run([python3, 'preload.py'] + args)
    if result.returncode == 0:
        print(f"{Colors.GREEN}Configuration check passed.{Colors.NC}")
    elif result.returncode == 1:
        print(f"{Colors.YELLOW}etc/config.json created. Please edit it and run this script again.{Colors.NC}")
        sys.exit(0)
    elif result.returncode == 2:
        print(f"{Colors.RED}Configuration corrupted: Failed loading token value from etc/config.json. Exiting...{Colors.NC}")
        sys.exit(2)
    elif result.returncode == 3:
        print(f"{Colors.RED}etc/server.json seems to be corrupted. Please delete it and run this script again.{Colors.NC}")
        sys.exit(2)
    elif result.returncode == 4:
        print(f"{Colors.RED}etc/config.json seems to be corrupted. Please delete it and run this script again.{Colors.NC}")
        sys.exit(2)
    elif result.returncode == 5:
        print(f"{Colors.RED}etc/config.json has missing keys that are necessary. Read the output logs to check which key is missing.{Colors.NC}")
        sys.exit(2)
    elif result.returncode == 6:
        print(f"{Colors.RED}Registry has missing keys or values that are necessary. Read the output logs to check which key or value is missing.{Colors.NC}")
        sys.exit(2)
    elif result.returncode == 7:
        print(f"{Colors.RED}Error reading pip3 list. Exiting...{Colors.NC}")
        sys.exit(2)
    elif result.returncode == 8:
        print(f"{Colors.RED}Core dependencies missing. Unable to continue. Exiting...{Colors.NC}")
        sys.exit(2)
    else:
        print(f"{Colors.RED}Configuration check failed with unknown error: {result.returncode}. Exiting...{Colors.NC}")
        sys.exit(2)

# Function to clear cache
def clear_cache():
    for root, dirs, files in os.walk('.'):
        for dir in dirs:
            if dir == '__pycache__':
                shutil.rmtree(os.path.join(root, dir))
    if os.path.exists('tmp'):
        shutil.rmtree('tmp')
    os.makedirs('tmp', exist_ok=True)
    print(f"{Colors.GREEN}Cache cleared.{Colors.NC}")


def main(args):
    pipcmds = ['pip3', 'pip']
    pythoncmds = ['python3', 'python']

    global pip3
    global python3

    for cmd in pipcmds:
        if command_exists(cmd):
            pip3 = cmd
            break

    for cmd in pythoncmds:
        if command_exists(cmd):
            python3 = cmd
            break

    if pip3 is None:
        print(f"{Colors.RED}Error: pip3 is not installed. Please install it and try again.{Colors.NC}")
        sys.exit(2)

    if python3 is None:
        print(f"{Colors.RED}Error: python3 is not installed. Please install it and try again.{Colors.NC}")
        sys.exit(2)

    print(f"{Colors.NC}Creating required directories...{Colors.NC}")
    os.makedirs('tmp', exist_ok=True)
    os.makedirs('storage', exist_ok=True)
    os.makedirs('etc', exist_ok=True)
    clear_cache()

    if not os.path.isfile("etc/pip-done"):
        print(f"{Colors.NC}Installing required components...{Colors.NC}")
        install_components()

    print(f"{Colors.NC}Checking configuration...{Colors.NC}")
    check_configuration(args)

    print(f"{Colors.NC}Starting system...{Colors.NC}")

    # Check if python3 is available as a command
    import importlib
    module = importlib.import_module('kernel.system')
    importlib.reload(module)
    completion = 0
    if __name__ == '__main__':
        completion = module.main(args)


    if "--no-clear-cache" not in args:
        print(f"{Colors.YELLOW}Clearing cache...{Colors.NC}")
        clear_cache()

    print(f"{Colors.NC}Bot exited with code {completion}.{Colors.NC}")

    sys.exit(completion)

if __name__ == '__main__':
    main(sys.argv[1:])
