#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import time
import argparse
import requests
import math
from triplification.functions import writeToFile, triplify, readTemplate
import logging

logger = logging.getLogger('triplification')

iRecordsPerPage = 100
templateFile = './templates/template_Sentinel.ttl'
URIBase = '<http://melodi.irit.fr/resource/'


def processQuery(stQuery):
    iCountPages = 1
    itemsPerPage = 0
    lsFeaturesTotal = []
    data = requests.get(stQuery).json()
    dictProperties = data.get('properties')
    totalResults = dictProperties.get('totalResults')
    itemsPerPage = dictProperties.get('itemsPerPage')
    lsFeatures = data.get('features')
    lsFeaturesTotal = lsFeaturesTotal + lsFeatures
    if totalResults < iRecordsPerPage:
        pass
    else:
        while itemsPerPage > 0:
            iCountPages = iCountPages + 1
            stNewQuery = stQuery + '&page=' + str(iCountPages)
            data = requests.get(stNewQuery).json()
            dictProperties = data.get('properties')
            totalResults = dictProperties.get('totalResults')
            itemsPerPage = dictProperties.get('itemsPerPage')
            lsFeatures = data.get('features')
            lsFeaturesTotal = lsFeaturesTotal + lsFeatures
    return lsFeaturesTotal


def triplify_dataset(output_folder, start_date="2017-04-01", end_date="2017-06-01", keyword="France", collection="Sentinel2" ):
    startEpoch = time.time()
    logger.debug('Triplifying Creodias sentinel metadata')
    
    query = 'https://finder.creodias.eu/resto/api/collections/{}/search.json?q={}&startDate={}&completionDate={}&maxRecords={}'.format(
        collection, keyword, start_date + 'T00:00:00.000Z', end_date + 'T00:00:00.000Z', iRecordsPerPage)

    lsMetadataDocs = processQuery(query)

    lsNameSpaces, lsTriplesTemplate = readTemplate(templateFile)
    maxRecordsPerFile = 30000
    triples = []
    iFiles = 0
    iTriples = 0
    iObs = 1
    for m in lsMetadataDocs:
        logger.debug(m)
        iObs = iObs + 1
        uriDummy = URIBase + 'EarthObservation/' + m['id']+">"
        m['properties']['tile'] = m['properties']['title'][39:44]
        m['properties']['sensor'] = m["properties"]["instrument"] + "_" + m["properties"]["platform"]
        triplesRow = triplify(m, lsTriplesTemplate, uriDummy, "s"+m['id'])
        triples = triples + triplesRow
        logger.debug('Number of triples', len(triples))
        if len(triples) > maxRecordsPerFile:
            file = output_folder + 'Sentinel' + str(iFiles) + '.ttl'
            writeToFile(lsNameSpaces, triples, file)
            iFiles = iFiles + 1
            iTriples = iTriples + len(triples)
            triples = []

    logger.debug('Number of triples', iTriples)
    file = output_folder + 'Sentinel' + str(iFiles) + '.ttl'
    writeToFile(lsNameSpaces, triples, file) 

    endEpoch = time.time()
    elapsedTime = endEpoch-startEpoch
    if elapsedTime < 60:
        logger.debug('Elapsed time : ', elapsedTime, ' seconds')
    else:       
        logger.debug('Elapsed time : ', math.floor(elapsedTime / 60), ' minutes and ', elapsedTime % 60, ' seconds' )
