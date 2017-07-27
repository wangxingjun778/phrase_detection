#!/usr/bin/env python
#coding:utf-8

import sys,os
import json
from set_logger import set_logger
import socket
import logging
import time

cur_dir = os.path.dirname(os.path.abspath(__file__)) or os.getcwd()
par_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) 
#sys.path.append(cur_dir)
from phrase_detection import Phrase_Detection

from bfd.harpc import server
from bfd.harpc.common import config
from gen.phrase.PhraseService import Processor

phrase_detect_obj = None

class PhraseHander(object):
    def __init__(self):
        pass
 
    def phrase_detect(self, text, topN=7):
        d_res = {}
        res = phrase_detect_obj.process(text, topN)
        for (k,v) in res:
            d_res[k] = v
        return d_res

def callback():
    print '\n-----init server object phrase_detect-----\n'
    global phrase_detect_obj
    phrase_detect_obj = Phrase_Detection()


def setLogger():
    filename = "logs/server.log"
    return set_logger(filename)

if __name__=='__main__':
    branch=sys.argv[1]
    conf_path='etc/server.conf.'+branch
    conf = config.Config(conf_path)
    server_demo = server.GeventProcessPoolThriftServer(Processor,PhraseHander(), conf)
    server_demo.set_post_fork_callback(setLogger)
    server_demo.set_post_fork_callback(callback)
    print "\n*** Start server ***\n"
    server_demo.start()

