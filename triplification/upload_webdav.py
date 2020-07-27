import argparse
from os import listdir
from os.path import isfile, isdir, join, abspath, splitext, getsize, basename
import requests
import sys
import time
import math
import getpass
from requests.auth import HTTPBasicAuth
from rdflib import Graph
import pycurl
import logging
from webdav3.client import Client

logger = logging.getLogger('triplification')

def upload_webdav(fn, url, login, pwd):
    logger.debug("Uploading file to webdav")
    #logger.debug("URL: "+ url)
    #logger.debug("Filename: "+ fn)
    options = {'webdav_hostname': url,
    'webdav_login':    login,
    'webdav_password': pwd}
    client = Client(options)
    client.verify = False   
    client.upload_sync(remote_path=basename(fn), local_path=fn)
    return True

def upload_store(fn, url, login, pwd):
    logger.debug("Uploading file to Strabon: "+ fn)
    if fn[0] == '.':
        fn = fn[1:]
    r = requests.post(url, data={
                'format':'Turtle',
                'view':'HTML',
                'fromurl':'Store from URI',
                'url': 'file:///' + fn
                }, auth=(login, pwd), verify=False, timeout=240)           
           
    logger.debug("Connection status: "+ str(r.status_code))
    msg= r.text.split("\n")
    rs = msg[162].strip()
    rs = rs[11:-13]
    
    if "successfully" not in rs:
        logger.debug("Result:" +  msg[160][36:-13])
    else:
        logger.debug("Result:" + rs)
   

def upload_dataset(input_file, server_path, endpoint, webdav, endpoint_login="candela", webdav_login="admin", endpoint_pwd="melodiH2020", webdav_pwd="melodiH2020" ):
    startEpoch = time.time()
    #url = 'https://185.178.85.62/semsearch/ep/Store'
    #url = 'http://melodi.irit.fr/ep/Store'
    if isfile(input_file):
        if upload_webdav(abspath(input_file), webdav, webdav_login, webdav_pwd):
            time.sleep(2)
            upload_store(server_path + basename(input_file), endpoint, endpoint_login, endpoint_pwd )
            time.sleep(2)
    elif isdir(input_file):
        for f in listdir(input_file):
            stFile = join(input_file, f)
            if isfile(stFile):
                if upload_webdav(abspath(stFile), webdav + f , webdav_login, webdav_pwd ):
                    time.sleep(2)
                    upload_store(server_path + f, endpoint, endpoint_login, endpoint_pwd )
                    time.sleep(2)  
           









   

   
