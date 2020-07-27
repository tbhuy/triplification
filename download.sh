export data_folder=/media/btran/Data970/CANDELA/data/

docker run -v "$data_folder:/home/btran/data/download" \
    -e OUTPUT_FOLDER=/home/btran/data/download \
    -e COMMAND=download \
    -e DATASET_NAME=$1 \
    --rm \
    c8baf86b2265

