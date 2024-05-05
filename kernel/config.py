import json
import os

def load() -> dict:
    with open('data/config.json') as f:
        
        config = json.load(f)
        
        config_parser = config['config_parser']
        envVarKeyword = config_parser['env_trigger']

        for key in config:
            value = config[key]
            if isinstance(value, str):
                if value.startswith(envVarKeyword):
                    envVar = value.replace(envVarKeyword, '')
                    config[key] = os.environ[envVar]
        
        return config


def get(key: str, default=None):
    config = load()
    return config[key] if key in config else default
    

def save(config: dict):
    with open('data/config.json', 'w') as f:
        json.dump(config, f, indent=4)
