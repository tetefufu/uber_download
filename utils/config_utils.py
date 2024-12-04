import yaml


def read_config(file_path):
    with open(file_path, 'r') as file:
        config = yaml.safe_load(file)  # safely loads the yaml file
    return config