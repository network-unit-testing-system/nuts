import os
import yaml


class Settings(object):
    def __init__(self):
        self.cfg = {}

    def from_envvar(self, variable_names):
        if isinstance(variable_names, str):
            variable_names = [variable_names]
        for vn in variable_names:
            rv = os.environ.get(vn)
            if rv:
                self.cfg[vn] = rv

    def from_file(self, config_file):
        with open(config_file, 'r') as ymlfile:
            cfg = yaml.safe_load(ymlfile)
        self.add(cfg)

    def add(self, dictionary):
        self.cfg.update(dictionary)

    def get_variable(self, name, default=None):
        try:
            return self.cfg[name]
        except KeyError:
            return default

    def dump_yaml(self):
        print(yaml.dump(self.cfg, default_flow_style=False))

settings = Settings()
