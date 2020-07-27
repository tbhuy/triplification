import time
import math
from datetime import datetime
import os
import argparse
import geopandas as gpd
from shapely.ops import transform
from functools import partial
from triplification.functions import triplify, readTemplate, writeToFile
from urllib.parse import quote
import logging
import numpy
from shapely.geometry import box

# 24s
# Data source file: https://www.data.gouv.fr/en/datasets/geozones/#_
template_vector = './triplification/template_Vector.ttl'
template_vector_DS = './triplification/template_Vector_DS.ttl'
URIBase = '<http://melodi.irit.fr/resource/'
maxRecordsPerFile = 40000

logger = logging.getLogger('triplification')

def triplify_dataset(feature_file, feature_type, output_folder='./rdf/'):
    startEpoch = time.time()
    logger.debug('Triplifying features information')
    #logger.debug("Reading file: "+ feature_file)
    triples = []
    files = []
    iFiles = 0
    iTriples = 0
    ds = {}
    file_name =  os.path.splitext(os.path.basename(feature_file))[0]
    features = gpd.read_file(feature_file)  
    #logger.debug("Feature CRS: "+ features.crs.srs)
    #logger.debug("Total of features: "+ str(len(features)))
    project_flag = 0
    if features.crs.srs != "epsg:4326":
        #logger.debug("Project from "+ features.crs.srs + "to EPSG:4326")
        wgs84 = partial(
                pyproj.transform,
                pyproj.Proj(init=features.crs),
                pyproj.Proj(init='EPSG:4326'))
        project_flag = 1
    bounding_box = features.total_bounds    
    ds['bbox'] = box(bounding_box[0], bounding_box[1],
                     bounding_box[2], bounding_box[3]).wkt
    ds['crs'] = features.crs.srs[5:]
    ds['size'] = os.path.getsize(feature_file)
    ds['creationdate'] = datetime.fromtimestamp(os.path.getmtime(feature_file)).strftime('%Y-%m-%dT%H:%M:%S')
    ds['format'] = "application/octet-stream"
    if os.path.splitext(feature_file)[1]=="geojson":
        ds['format'] = "json"
    ds['title'] = file_name
    ds['description'] = "Vector file for" + feature_type
        
    lsNameSpaces, lsTriplesTemplate = readTemplate(template_vector_DS)
    URI = URIBase + 'Dataset/' + feature_type + "_" + file_name +">"
    triplesRow = triplify(ds, lsTriplesTemplate, URI,  feature_type + "_" + file_name)            
    triples = triples + triplesRow
    triples.append([URIBase + 'GeoFeatureType/'+ feature_type + '>', 'a', 'tom:GeoFeatureType'])
    triples.append([URIBase + 'GeoFeatureType/'+ feature_type + '>', 'tom:name', '"' + feature_type + '"^^xsd:string'])
            
    lsNameSpaces, lsTriplesTemplate = readTemplate(template_vector)
    for index, row in features.iterrows():
        if row['geometry'] is not None: 
            feat = {}
            feat['id'] = row.get('id', 'null')       
            feat['wkt'] = row['geometry']
            if project_flag:
                feat['wkt'] = transform(project, feat['wkt'])
            feat['type'] = feature_type
            URI = URIBase +  'GeoFeature/' + feature_type + "_" + feat['id']+">"
            triplesRow = triplify(feat, lsTriplesTemplate,
                                  URI,  feature_type + "_" + feat['id'])            
            triples = triples + triplesRow
            if len(triples) > maxRecordsPerFile:
                file = os.path.join(output_folder, feature_type + '_' + datetime.now().strftime("%m-%d-%Y-%H-%M")+'_' + str(iFiles) + '.ttl')
                logger.debug("Writing file: "+ file)
                writeToFile(lsNameSpaces, triples, file)
                files.append(file)          
                iFiles = iFiles + 1
                iTriples = iTriples + len(triples)
                triples = []

    
    file = os.path.join(output_folder, feature_type + '_' + datetime.now().strftime("%m-%d-%Y-%H-%M")+'_' + str(iFiles) + '.ttl')
    files.append(file)
    logger.debug("Writing file: "+ file)
    logger.debug('Number of triples: '+ str(iTriples))
    writeToFile(lsNameSpaces, triples, file)
    return files
