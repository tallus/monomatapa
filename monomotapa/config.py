import sys
import os.path
import json

class Config(object):
    """load config values e.g default css"""
    def __init__(self, conffile):
        try:
            config_file = self.get_config_file(conffile)
        except NameError:
            raise ConfigError("Config file %s not found" % conffile)
        with open(config_file, 'r') as cfile:
            self.config = json.load(cfile)

    def get_config_file(self, filename):
        """return first file found in path"""
        config_file = None
        path_to_app = sys.path[0]
        path = [
                filename, 
                os.path.join(path_to_app, filename), 
                os.path.join('/etc/monmotapa/', filename), 
                os.path.join('/etc', filename)
                ]
        for cfile in path:
            if os.path.exists(cfile):
                config_file = cfile
                break
        return config_file


class ConfigError(Exception):
    pass
