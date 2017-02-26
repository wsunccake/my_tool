import os
import sys


class PyConfig(object):
    def __init__(self, input_file):
        self.path = os.path.dirname(input_file)
        sys.path.append(self.path)
        config = __import__(os.path.basename(input_file[:-3]))

        for k in config.__dict__.keys():
            if not (k[0] is '_'):
                setattr(self, k, config.__dict__[k])

    def get_config_dict(self, distinguish='default'):
        att = {}

        for k in self.__dict__.keys():
            att[k] = self.__dict__[k]
            if isinstance(self.__dict__[k], dict):
                if distinguish in self.__dict__[k]:
                    att[k] = self.__dict__[k][distinguish]
                elif 'default' in self.__dict__[k]:
                    att[k] = self.__dict__[k]['default']

        return att
