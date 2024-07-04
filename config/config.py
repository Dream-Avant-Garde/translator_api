import yaml

class Config:
    def __init__(self, config_file):
        with open(config_file, 'r') as file:
            self.config = yaml.safe_load(file)

seamless_config = Config('config/seamless_m4t.yml').config
translator_config = Config('config/translator.yml').config