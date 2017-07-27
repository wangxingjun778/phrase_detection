#coding:utf-8

import os
cur_dir = os.path.dirname( os.path.abspath(__file__)) or os.getcwd()

class Config(object):
    def __init__(self):
        self.stop_file   = cur_dir+"/model/stopwords"
        self.phrase_file = cur_dir+"/model/phrase_mapping"
        self.idf_file    = cur_dir+"/model/idf_file"
