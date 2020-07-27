export data_folder=/home/btran/candela/data
#Upload remotely rdf files to endpoint (by splitting files content)

docker run -v "$data_folder:/var/data" \
    -e COMMAND=upload \
    -e ENDPOINT=http://platform.candela-h2020.eu/semsearch/ep/Store \
    -e INPUT_FILE1=/var/data/rdf/Tile.ttl \
    -e ENDPOINT_LOGIN=candela \
    -e METHOD=remote \
    -e NTRIPLES=1000 \
    --rm \
    1af25b3e5f02
