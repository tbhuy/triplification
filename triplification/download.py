import urllib.request
import gzip
import tarfile
import zipfile
import lzma
import ast
import logging

logger = logging.getLogger('triplification')

def download(dataset, output_folder):
    with open("./links.ds", "r") as data:
        ds = ast.literal_eval(data.read())
    if dataset not in ds.keys():
        logger.debug("Unrecognized dataset. Please retry.")
        return
    logger.debug("Downloading dataset", dataset, "...")
    fn = os.getenv("OUTPUT_FOLDER") + "/" + ds[dataset]['fn']
    urllib.request.urlretrieve(ds[dataset]['link'], fn)
    if zipfile.is_zipfile(fn):
        logger.debug("Decompressing dataset...")
        zf = zipfile.ZipFile(fn)
        zf.extractall(output_folder)
    elif fn[-2:] == "xz":
        logger.debug("Decompressing dataset...")
        with lzma.open(fn) as f:
            with tarfile.open(fileobj=f) as tar:
                tar.extractall(os.getenv("OUTPUT_FOLDER"))

    elif tarfile.is_tarfile(fn):
        logger.debug("Decompressing dataset...")
        tf = tarfile.TarFile(fn)
        tf.extractall(os.getenv("OUTPUT_FOLDER"))
    logger.debug("Done.")

