import json

def parse_config(file_path):
    """Parse the JSON configuration file."""
    with open(file_path, 'r') as file:
        config = json.load(file)
    return config
