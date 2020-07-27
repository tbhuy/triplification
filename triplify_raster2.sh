export data_folder=/home/btran/data
export dockerregistry=registry.test.candela.eu/candela
#export service=$dockerregistry/triplification
export service=9ac52d055163


docker run -v "$data_folder:/var/data" \
    -e OUTPUT_FOLDER=/var/data/rdf/ \
    -e COMMAND=triplify \
    -e DATASET_NAME=raster \
    -e RASTER_FILE=/var/data/download/CLC2018.tif \
    -e FEATURE_FILE=/var/data/download/torun.geojson \
    -e END_DATE=2017-01-01 \
    -e START_DATE=2018-12-31 \
    -e PRODUCT1= \
    -e PRODUCT2= \
    -e FEATURE_TYPE=ForestUnit \
    -e DS=LC_Corine \
    --rm \
    $service

