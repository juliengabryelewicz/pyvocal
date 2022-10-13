import glob
import os
import yaml

class Configuration:

    config_list = {}

    def __init__(self,fileConfiguration):
        with open(fileConfiguration) as file:
            self.config_list = yaml.load(file, Loader=yaml.FullLoader)