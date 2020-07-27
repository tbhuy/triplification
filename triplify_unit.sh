export data_folder=/home/btran/data
export dockerregistry=registry.test.candela.eu/candela
#export service=$dockerregistry/triplification
export service=0f459b171354

docker run -v "$data_folder:/var/data" \
    -e OUTPUT_FOLDER=/var/data/rdf/ \
    -e COMMAND=triplify \
    -e DATASET_NAME=unit\
    -e FEATURE_FILE=/var/data/download/torun.geojson$2 \
    -e FEATURE_TYPE=ForestUnit \
    --rm \
    $service

