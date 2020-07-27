export data_folder=/home/btran/data
export dockerregistry=registry.test.candela.eu/candela
#export service=$dockerregistry/triplification
export service=707ba0f36f3e

#Download and Triplify Sentinel metadata with arguments: keyword: France, Start_date:2017-04-01, End_date:2017-06-01
docker run -v "$data_folder:/var/data" \
    -e OUTPUT_FOLDER=/var/data/rdf/ \
    -e COMMAND=triplify \
    -e DATASET_NAME=sentinel2\
    -e KEYWORD=France\
    -e START_DATE=2017-04-01\
    -e END_DATE=2017-06-01\
    --rm $service\
    

