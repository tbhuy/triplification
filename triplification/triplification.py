import time
import os
from datetime import datetime
import math
import rasterio
from rasterio.mask import mask
import geopandas as gpd
import triplification.unit as unit
from triplification.functions import writeToFile, triplify, readTemplate
import pyproj
from shapely.ops import transform
from functools import partial
from collections import Counter
import numpy as np
import logging
from triplification import upload_webdav
from shapely.geometry import box
import matplotlib.image as mpimg

template_Raster = './triplification/template_Raster.ttl'
template_Raster_DS = './triplification/template_Raster_DS.ttl'
URIBase = '<http://melodi.irit.fr/resource/'
maxRecordsPerFile = 50000
scale = 16
endpoint_URL = 'http://platform.candela-h2020.eu/semsearch/ep/Store'
endpoint_pass ='xxx'
endpoint_login = 'xxx'
webdav_URL = 'http://platform.candela-h2020.eu/semsearch/ep/permanent_data/permanent_data/'
webdav_login = 'xxx'
webdav_pass = 'xxx' 
webdav_path = '/usr/local/tomcat/webapps/ep/permanent_data/'

logger = logging.getLogger('triplification')


def triplify_dataset(feature_file, raster_file, ftype=None, agent='IRIT', output_folder='./rdf/', threshold1=0, threshold2=0, threshold3=0):
    startEpoch = time.time()    
    files = []
    logger.debug('Compute and triplify raster file data')
    logger.debug('Raster file: '+ raster_file)
    logger.debug('Feature file: '+feature_file)
    triples = []
    iFiles = 0
    iTriples = 0
    rasterfile = rasterio.open(raster_file)   
    features = gpd.read_file(feature_file) 
    
    #check bounds intersection
    bounding_box = features.total_bounds    
    fbox = box(bounding_box[0], bounding_box[1],
                     bounding_box[2], bounding_box[3])
    
    bounding_box = rasterfile.bounds
    rbox = box(bounding_box[0], bounding_box[1],
                     bounding_box[2], bounding_box[3])    
     
    project = partial(
                pyproj.transform,
                pyproj.Proj(init=features.crs),
                pyproj.Proj(init=rasterfile.crs))
    
    fbox = transform(project, fbox)
    if not fbox.intersects(rbox):
        logger.debug("The vector box does not intersect the raster one.")
        return
    
    file_name =  os.path.splitext(os.path.basename(raster_file))[0]
    ffile_name =  os.path.splitext(os.path.basename(feature_file))[0]
    quicklook_fn = os.path.join(output_folder, file_name + '.png')

    rasterfile = rasterio.open(raster_file)   
    features = gpd.read_file(feature_file) 
    quicklook = rasterfile.read(1, out_shape=(1, int(rasterfile.height // scale), int(rasterfile.width // scale)))
    mpimg.imsave(quicklook_fn, quicklook, cmap = 'gray')
    lsNameSpaces, lsTriplesTemplate = readTemplate(template_Raster_DS)
    
    try:
        tags=rasterfile.tags()
        #logger.debug(tags)
        raster_start_date="{}-{}-{}".format(tags.get('Start_date')[0:4], tags.get('Start_date')[4:6], tags.get('Start_date')[6:])
        if tags.get('End_date', None) != None:
            raster_end_date = "{}-{}-{}".format(tags.get('End_date')[0:4], tags.get('End_date')[4:6], tags.get('End_date')[6:])
        else:
            raster_end_date = None
        product1 = tags.get('Product_id1', None)
        product2 = tags.get('Product_id2', None)
        agent = tags.get('Agent', agent)                
        ds = tags.get("Category")
    except:
        logger.debug("Cannot process the files. The metadata is not valid!")
        logger.debug("Please check attribute name and value. Example:")
        logger.debug("Start_date='20170409'")
        logger.debug("Category='LC_DM'")
        logger.debug("Product_id1='S2A_MSIL2A_20170409T105651_N0204_R094_T30TYQ_20170409T110529.SAFE'")
        return None

        
    raster_ds = {}  
    raster_ds['productID1'] = product1
    raster_ds['productID2'] = product2
    raster_ds['agent'] = agent
    raster_ds['bg'] = datetime.strptime(raster_start_date, '%Y-%m-%d').timestamp()
    if raster_end_date != None:
        raster_ds['end'] = datetime.strptime(raster_end_date, '%Y-%m-%d').timestamp()
    raster_ds['crs'] = rasterfile.crs.to_string()
    bounding_box = rasterfile.bounds
    raster_ds['bbox'] = box(bounding_box[0], bounding_box[1],
                     bounding_box[2], bounding_box[3]).wkt
    
    raster_ds['size'] = os.path.getsize(raster_file)
    raster_ds['creationdate'] = datetime.fromtimestamp(os.path.getmtime(raster_file)).strftime('%Y-%m-%dT%H:%M:%S')
    raster_ds['format'] = "application/x-geotiff"
    raster_ds['title'] = file_name
    raster_ds['description'] = "Raster file for " + ds + " - " + agent
    raster_ds['resolution'] = rasterfile.res[0]
    raster_ds['URI'] = ds + "_" + file_name
    raster_ds['quicklook'] = webdav_URL  + file_name + '.png'
    #logger.debug(raster_ds['bbox'])
    #logger.debug(raster_ds['quicklook'])

    URI = URIBase + 'EOAnalysis/' + ds + "_" + file_name +">"
    triplesRow = triplify(raster_ds, lsTriplesTemplate, URI,  ds + "_" + file_name)            
    triples = triples + triplesRow
    
    
    triples.append([URIBase + 'GFObservedPropertyType/'+ ds + '>', 'a', 'tom:GFObservedPropertyType'])
    triples.append([URIBase + 'GFObservedPropertyType/'+ ds + '>', 'tom:name', '"' + ds + '"^^xsd:string'])
   
    if ds[0:2] != "LC":
        labels = ["VeryLow", "Low", "Middle", "High"]
        for i in range(1, 5):
            triples.append([URIBase + 'GFObservedProperty/'+ ds + '_'+ str(i) + '>', 'a', 'tom:GFObservedProperty']) 
            triples.append([URIBase + 'GFObservedProperty/'+ ds + '_'+ str(i) + '>', 'tom:hasType', URIBase + 'GFObservedPropertyType/'+ ds + '>']) 
            triples.append([URIBase + 'GFObservedProperty/'+ ds + '_'+ str(i) + '>', 'tom:name', '"' + labels[i-1] + "_" + ds + '"^^xsd:string'])
    else:
        values = np.unique(rasterfile.read(1))
        for v in values:
            triples.append([URIBase + 'GFObservedProperty/'+ ds + '_'+ str(v) + '>', 'a', 'tom:GFObservedProperty']) 
            triples.append([URIBase + 'GFObservedProperty/'+ ds + '_'+ str(v) + '>', 'tom:hasType', URIBase + 'GFObservedPropertyType/'+ ds + '>']) 
           
            
        
    lsNameSpaces, lsTriplesTemplate = readTemplate(template_Raster)
  
    if ds[0:2] != "LC":     
        band=rasterfile.read(1)
        #logger.debug(band.shape)
        min_raster = band.min()
        max_raster = band.max()       
        logger.debug("Max raster: " + str(max_raster))
        logger.debug("Min raster: " + str(min_raster))
        if threshold1==0 and threshold2==0 and threshold3==0:      
            bins=np.linspace(min_raster, max_raster, num=5, endpoint=True)
            logger.debug("Use computed bins: " + str(bins))
        else:          
            thresholds=[min_raster, threshold1, threshold2, threshold3, max_raster]
            bins=np.array(thresholds)
            logger.debug("Use custom bins: " + str(bins))
        
    outside = 0
    toosmall = 0
    featuresize = []
    wgs84 = partial(
                pyproj.transform,
                pyproj.Proj(init=features.crs),
                pyproj.Proj(init='EPSG:4326'))
    if rasterfile.crs.to_string().lower() != features.crs.srs:
        logger.debug("Project features from "+ features.crs.srs + " to " + rasterfile.crs.to_string())
        project = partial(
                pyproj.transform,
                pyproj.Proj(init=features.crs),
                pyproj.Proj(init=rasterfile.crs))
       
    for index, row in features.iterrows():
        #clear_output()
        #logger.debug(str(index) + '/' + str(len(features)))
        feat = {}
        feat['id'] = str(row['id'])

        try:           
            if rasterfile.crs.to_string().lower() != features.crs.srs:
                geom = transform(project, row['geometry'])
            else:
                geom = row['geometry']
            featureSem, _ = mask(rasterfile, [geom], all_touched=False, crop=True, indexes=1, nodata=0)
        except ValueError as  err:
            #logger.debug(err)
            outside = outside +1
            continue
     
   
        total = featureSem[featureSem>0].size
        if total <= 0:
            #logger.debug("Too small! Change all_touch for mask to True.")
            toosmall = toosmall + 1
            #Change mask settings
            featureSem, _ = mask(rasterfile, [geom], all_touched=True, crop=True, indexes=1, nodata=0)
            total= featureSem[featureSem>0].size
            
        if ds[0:2] != "LC":
            for x in np.nditer(featureSem, op_flags = ['readwrite']):
                if x[...] > 0:
                    x[...] = int(np.digitize(x, bins))
            #logger.debug(x)
            #logger.debug(featureSem)
          
            
        counter = Counter(featureSem.ravel())
        feat['type'] = ds
        feat['vector'] = ftype + "_" + os.path.splitext(os.path.basename(feature_file))[0]
        feat['raster'] = ds + "_" + os.path.splitext(os.path.basename(raster_file))[0]
        feat['interval'] = raster_start_date + " " + (raster_end_date  if raster_end_date != None else raster_start_date) 
        rStart = datetime.strptime(raster_start_date, '%Y-%m-%d')
        rEnd = datetime.strptime(raster_end_date, '%Y-%m-%d') if raster_end_date != None else ''
        feat['foi'] = ftype + "_" + feat['id'] 
        
        URI = URIBase + 'GFObservationCollection/'+ ds + "_" + ftype + "_" + feat['id'] + "_" + str(int(rStart.timestamp())) + "_" + (str(int(rEnd.timestamp()))  if raster_end_date != None else '') + ">"
        triplesRow = triplify(feat, lsTriplesTemplate, URI, os.path.splitext(os.path.basename(raster_file))[0])
        triples = triples + triplesRow
        
        for c in counter:
            if c>0:
                value = round(counter[c] / total, 2)
                semclass = int(c)
                GFObs = URIBase + 'GFObservation/'+ ds + "_" + ftype+"_"+feat['id']+"_"+ str(semclass) + "_" + str(int(rStart.timestamp())) + "_" + (str(int(rEnd.timestamp()))  if raster_end_date != None else '') + ">" 
                
                triples.append([GFObs, 'a', 'tom:GFObservation'])
                triples.append([URI, 'sosa:hasMember', GFObs])           
                triples.append([GFObs, 'sosa:hasSimpleResult', '"' + str(value) + '"^^xsd:float'])
                triples.append([GFObs, 'sosa:observedProperty', URIBase + "GFObservedProperty/" + ds + "_" + str(semclass)+">"])          
         
        if len(triples) > maxRecordsPerFile:
            fn =  os.path.join(output_folder, 'Obs_' + ds + "_" + ftype + "_" + ffile_name + "_" + raster_start_date + "_"+ (raster_end_date  if raster_end_date != None else '')  + "_" + str(iFiles) + '.ttl')
                #logger.debug(file)
            logger.debug("Writing file: "+ fn)
            writeToFile(lsNameSpaces, triples, fn) 
            files.append(fn)
            iFiles = iFiles + 1
            iTriples = iTriples + len(triples)
            triples = []
        
     
          
        #show(parcelChange)   
   
    fn =  os.path.join(output_folder, 'Obs_' + ds + "_" + ftype + "_" + ffile_name + "_" + raster_start_date + "_" + (raster_end_date  if raster_end_date != None else '')  + "_" + str(iFiles) + '.ttl')
    logger.debug("Writing file: " + fn)
    files.append(fn)
    writeToFile(lsNameSpaces, triples, fn)
    #clear_output()
    iTriples = iTriples + len(triples)
    logger.debug('Number of triples: ' + str(iTriples))
    
    
    
    files2=unit.triplify_dataset(feature_file, ftype, output_folder)

    
    #logger.debug('Number of parcel', len(features))
    #logger.debug('Too small', toosmall)
    #logger.debug('Outside', outside)
    #logger.debug('size', featuresize)
    upload_webdav.upload_webdav(quicklook_fn, webdav_URL, webdav_login, webdav_pass)
   
    for upfile in files + files2:
        upload_webdav.upload_dataset(upfile, webdav_path, endpoint_URL, webdav_URL, endpoint_login, webdav_login, endpoint_pass, webdav_pass)     
    logger.debug(files + [quicklook_fn])
    return files + files2 + [quicklook_fn]
