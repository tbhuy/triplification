import os
import urllib.request
import gzip
import tarfile
import zipfile
import lzma
from triplification import *
import ast
import logging


cwd =  os.getcwd()
config_folder = os.getenv('CONFIG_FOLDER', cwd)
log_file = os.getenv('LOG_FILE', 'test_triplification.log')

log_file_path = os.path.join(config_folder, log_file)
FORMAT = '%(asctime)s %(levelname)s %(message)s'

logger = logging.getLogger('triplification')
logger.setLevel(level=logging.DEBUG)
fh = logging.FileHandler(log_file_path)
fh.setLevel(level=logging.DEBUG)
fh.setFormatter(logging.Formatter(FORMAT))
logger.addHandler(fh)





triplification.triplify_dataset(feature_file=os.path.join(os.getenv("INPUT_FOLDER"), os.getenv("FEATURE_FILE")), 
                                raster_file=os.path.join(os.getenv("INPUT_FOLDER"), os.getenv("RASTER_FILE")), 
                                output_folder=os.getenv("OUTPUT_FOLDER", None),  
                                agent=os.getenv("AGENT", None),
                                ftype=os.getenv("FEATURE_TYPE"), 
                                threshold1=float(os.getenv("THRESHOLD1", 0)),
                                threshold2=float(os.getenv("THRESHOLD2", 0)),
                                threshold3=float(os.getenv("THRESHOLD3", 0))
                                )  
