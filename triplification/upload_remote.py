import argparse
from os import listdir
from os.path import isfile, isdir, join, abspath, splitext
import requests
import sys
import time
import math
import getpass
from requests.auth import HTTPBasicAuth
from rdflib import Graph
import logging

logger = logging.getLogger('triplification')

def uploadFile(file, n, url, login, pwd): 
    logger.debug("Validating file: ", abspath(file))
    g = Graph()
    try:
        g.parse(file, format='turtle')
    except Exception as e:
        logger.debug("Error loading file: ", e)
        return

    logger.debug("Uploading file: ", abspath(file))
    lines = ""
    count = 0
    part = 1
    prefixes = "" 
    data = g.serialize(destination=None, format='nt') 
    triples = data.decode().split('\n')       
    for line in triples:
        lines = lines + line
        count = count + 1
        if count >= n:
            r = requests.post(url, data={
                        'format': 'N-Triples',
                        'view': 'HTML',
                        'dsubmit': 'Store Input',
                        'url':'',
                        'data': lines
                            },
                            auth=HTTPBasicAuth(login, pwd), 
                            verify=False, 
                            timeout=120
                        )
            logger.debug("Part", part, "(", math.floor(sys.getsizeof(lines)/1024), "KB) : Response ", r.status_code, r.reason)
            msg= r.text.split("\n")
            rs = msg[162].strip()
            rs = rs[11:-13]
            if "successfully" not in rs:
                logger.debug("Result:", msg[160][36:-13])
            else:
                logger.debug("Result:", rs)
            part = part + 1
            count = 0
            lines = ""
            time.sleep(5)
            #logger.debug(prefixes)           

    r = requests.post(url, data={
        'format': 'N-Triples',
        'view': 'HTML',
        'dsubmit': 'Store Input',
        'url':'',
        'data':  lines
                 },
                            auth=HTTPBasicAuth(login, pwd),
                            verify=False, 
                            timeout=120
                        )
    logger.debug("Part", part, "(", math.floor(sys.getsizeof(lines)/1024), "KB) :")
    logger.debug("Connection:", r.status_code, r.reason)
    msg= r.text.split("\n")
    rs = msg[162].strip()
    rs = rs[11:-13]
    
    if "successfully" not in rs:
        logger.debug("Result:", msg[160][36:-13])
    else:
        logger.debug("Result:", rs)
    

def upload_dataset(input_file, endpoint, login, ntriples=5000):

    startEpoch = time.time()
    #url = 'https://185.178.85.62/semsearch/ep/Store'
    #url = 'http://melodi.irit.fr/ep/Store'
    pwd = ""
    try: 
        logger.debug("Enter enpoint password: ")
        pwd = getpass.getpass() 
    except Exception as error: 
        pwd = 'melodi'
        logger.debug('ERROR', error)
        logger.debug('Use default password') 
 
    if isfile(input_file):
        uploadFile(input_file, ntriples, endpoint, login, pwd )
    elif isdir(input_file):
        for f in listdir(input_file):
            stFile = join(input_file, f)
            if isfile(stFile):
                if splitext(stFile)[1] == ".ttl":
                    uploadFile(stFile, ntriples, endpoint, login, pwd )

    endEpoch = time.time()
    elapsedTime = endEpoch - startEpoch
    if elapsedTime < 60:
        logger.debug('Elapsed time : ', elapsedTime, ' seconds')
    else:
        logger.debug('Elapsed time : ', math.floor(elapsedTime / 60), ' minutes and ', elapsedTime % 60, ' seconds' )








   

   
