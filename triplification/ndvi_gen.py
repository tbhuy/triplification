
import time
import math
import argparse
import rasterio
from rasterio.mask import mask
import geopandas as gpd
from triplification.functions import writeToFile, triplify, readTemplate
import pyproj
from shapely.ops import transform
from functools import partial
import numpy as np
import logging
# 24s
# Data source file: https://www.data.gouv.fr/en/datasets/geozones/#_
templateFile = './templates/template_NDVI_dept.ttl'
URIBase = '<http://melodi.irit.fr/resource/'
maxRecordsPerFile = 15000



logger = logging.getLogger('triplification')

def compute_ndvi(red_file, nir_file, output_file='./download/ndvi_30TYQ_20170406.tif'): # start_date="2017-04-19", end_date="2017-04-29"):
    startEpoch = time.time()
    logger.debug('Compute and triplify NDVI vegetation index from S2ST image')

    #red = red if red else '/home/btran/candela/data/ndvi/L2A_T30TYQ_20170429T105651_B04_10m.jp2'
    #nir = nir if nir else '/home/btran/candela/data/ndvi/L2A_T30TYQ_20170429T105651_B08_10m.jp2'
    #parcel = parcel if parcel else '/home/btran/candela/data/cadastre/dept47/parcelles.shp'
    redFile=rasterio.open(red_file)
    nirFile=rasterio.open(nir_file)
    red=redFile.read(1)
    nir=nirFile.read(1)   

    #ndvi=np.divide(divident, divisor, out=np.zeros(divident.shape, dtype=float), where=divisor!=0)
    #ndvi[ndvi<0] = 0.0
  
    ndvi = (np.float16(nir) - np.float16(red)) / \
            (np.float16(nir) + np.float16(red))
    ndvi[ndvi == np.inf] = 0.0
    ndvi = np.nan_to_num(ndvi)
    ndvi[ndvi<0] = 0.0
        
    with rasterio.Env():

    # Write an array as a raster band to a new 8-bit file. For
    # the new file's profile, we start with the profile of the source
        profile = redFile.profile

    # And then change the band count to 1, set the
    # dtype to uint8, and specify LZW compression.
        profile.update(
        dtype=rasterio.float32,
        crs=redFile.crs,
        driver='GTiff',
        count=1,
        compress='lzw')

        with rasterio.open(output_file, 'w', **profile) as dst:
            dst.write(ndvi.astype(rasterio.float32), 1)


    
    return output_file
