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
import logging

logger = logging.getLogger('triplification')

def uploadFile(lfile, sfile, url, login, pwd): #validate localfile, upload the corresponding serverfile
    logger.debug("Validating file: ", abspath(lfile))
    g = Graph()
    try:
        g.parse(lfile, format='turtle')
    except Exception as e:
        logger.debug("Error loading file: ", e)
        return

    r = requests.post(url, data={
                'format':'Turtle',
                'view':'HTML',
                'fromurl':'Store from URI',
                'url': 'file://' + sfile
                }, auth=(login, pwd), verify=False, timeout=120)           
           
    logger.debug("Connection:", r.status_code, r.reason)
    msg= r.text.split("\n")
    rs = msg[162].strip()
    rs = rs[11:-13]
    
    if "successfully" not in rs:
        logger.debug("Result:", msg[160][36:-13])
    else:
        logger.debug("Result:", rs)

def upload_dataset(input_file, server_path, endpoint, login):
    logger.debug("Please upload the folder to the server before excuting the script")    
    startEpoch = time.time()
    #url = 'https://185.178.85.62/semsearch/ep/Store'
    #url = 'http://melodi.irit.fr/ep/Store'
    pwd = ""
    try: 
        logger.debug("Enter endpoint password")
        pwd = getpass.getpass() 
    except Exception as error: 
        pwd = 'xxx'
        logger.debug('ERROR', error)
        logger.debug('Use default password') 
  

    if isfile(input_file):
        uploadFile(input_file, server_path + basename(input), endpoint, login, pwd )
    else:
        logger.debug("Folder")
        for f in listdir(input_file):
            stFile = join(input_file, f)
            if isfile(stFile):
                if splitext(stFile)[1] == ".ttl":
                    uploadFile(input_file + f, server_path + f, endpoint, login, pwd )
                    time.sleep(5)
          

    endEpoch = time.time()
    elapsedTime = endEpoch - startEpoch
    if elapsedTime < 60:
        logger.debug('Elapsed time : ', elapsedTime, ' seconds')
    else:
        logger.debug('Elapsed time : ', math.floor(elapsedTime / 60), ' minutes and ', elapsedTime % 60, ' seconds' )
           









   

   
