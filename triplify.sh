export data_folder=/media/btran/Data970/CANDELA/data/
#Triplify normal dataset with arguments received from the shell command.
#$1: Dataset name, $2: Input data file
#The data file must be locally accessible
#Ex: triplify.sh admin zones.json
#Ex: triplify.sh tile tile.shp
#Ex: triplify.sh event events.json
#Ex: triplify.sh natura natura.shp
#Ex: triplify.sh station station.json

docker run -v "$data_folder:/var/data" \
    -e OUTPUT_FOLDER=/var/data/rdf/ \
    -e COMMAND=triplify \
    -e DATASET_NAME=$1 \
    -e INPUT_FILE1=/var/data/download/$2 \
    --rm \
    707ba0f36f3e

