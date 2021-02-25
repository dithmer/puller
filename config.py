import yaml
import os

CONFIG_PATH = os.getenv('PULLER_CONFIG_PATH')

def get_config():
    with open(CONFIG_PATH) as f:
        config = yaml.load(f, Loader=yaml.Loader)

    return config