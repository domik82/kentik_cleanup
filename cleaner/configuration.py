import json


class Configuration:

    def __init__(self, config_file_path):
        self.config_file_path = config_file_path
        self.config_data = self.load_configuration_file(self.config_file_path)
        if self.config_data is not None and 'retention' in self.config_data:
            self.retention_policy = self.config_data['retention']
        else:
            raise RuntimeError('Retention Policy not specified in config')

    @staticmethod
    def load_configuration_file(config_file_path):
        try:
            with open(config_file_path, 'r') as config_file:
                try:
                    return json.load(config_file)
                except ValueError:
                    raise RuntimeError('Config file seems to be broken')
        except IOError:
            raise RuntimeError(f'File not accessible. File:{config_file_path}')

    @staticmethod
    def write_configuration(config_file_path, configuration_dict):
        json_object = json.dumps(configuration_dict, indent=4)
        with open(config_file_path, "w") as outfile:
            outfile.write(json_object)

    def get_retention_policy(self):
        return self.retention_policy

    def get_default_retention_policy(self):
        try:
            return self.get_retention_by_id('default')
        except ValueError:
            raise ValueError('Default Retention Policy not specified in config')

    def get_retention_by_id(self, retention_id):
        try:
            retention = self.config_data['retention'][retention_id]
            if isinstance(retention, int):
                return retention
            else:
                raise TypeError('Defined retention is not an integer value')
        except KeyError:
            raise ValueError('Retention Policy not specified in config')

    def get_retention_by_id_or_default(self, retention_id):
        try:
            return self.get_retention_by_id(retention_id)
        except ValueError as e:
            if e.args[0] == 'Retention Policy not specified in config':
                return self.get_default_retention_policy()
            else:
                raise
