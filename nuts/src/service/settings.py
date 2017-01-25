import yaml
class Settings():
    def __init__(self):
        with open("config.yml", 'r') as ymlfile:
            cfg = yaml.safe_load(ymlfile)
        self.cfg = cfg 
    def getVariable(self,name):
        return self.cfg[name]