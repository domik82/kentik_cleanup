import json
import os
import pathlib
import random


class ConfigGenerator:

    def generate_random_retention(self):
        retention_list = [10, 30, 60, 90, 120]
        return random.choice(retention_list)

    def generate_configuration(self, default_retention, company_retention):
        config = {}
        retention = {'default': default_retention, **company_retention}
        config['retention'] = retention
        return config

    @staticmethod
    def write_configuration(config_file_path, configuration_dict):
        # Serializing json
        json_object = json.dumps(configuration_dict, indent=4)

        if config_file_path is None:
            config_file_name = "config.json"
            config_directory = "config"
            current_working_dir = pathlib.Path().resolve()
            config_file_path = os.path.normpath(os.path.join(current_working_dir, config_directory))
            config_file_path = os.path.join(config_file_path, config_file_name)

        if not os.path.exists(os.path.dirname(os.path.abspath(config_file_path))):
            os.makedirs(os.path.dirname(os.path.abspath(config_file_path)), exist_ok=True)

        with open(config_file_path, 'w+') as outfile:
            outfile.write(json_object)
