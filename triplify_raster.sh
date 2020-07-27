export data_folder=/home/btran/data
export dockerregistry=registry.test.candela.eu/candela
#export service=$dockerregistry/triplification
export service=c3f5a0999a82

docker run --cpus 8 --memory 8G -v "$data_folder:/home/btran/data" \
    -e INPUT_FOLDER=/home/btran/data/ \
    -e OUTPUT_FOLDER=/home/btran/data/ \
    -e RASTER_FILE=S1B_S1B_GRDH_1SVV_20170805_20170817_CD_KMEANS_SNGL.tif \
    -e FEATURE_FILE=torun.geojson \
    -e FEATURE_TYPE=ForestUnit \
    --rm \
    $service


