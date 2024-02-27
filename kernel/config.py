import json
import os

def load() -> dict:
    with open('data/config.json') as f:
        
        config = json.load(f)
        
        config_parser = config['config_parser']
        envVarKeyword = config_parser['env_trigger']

        for key in config:
            get = config[key]
            if isinstance(get, str):
                if get.startswith(envVarKeyword):
                    envVar = get.replace(envVarKeyword, '')
                    config[key] = os.environ[envVar]
        
        return config


def get(key: str) -> str:
    config = load()
    return config[key]
    

def save(config: dict):
    with open('data/config.json', 'w') as f:
        json.dump(config, f, indent=4)