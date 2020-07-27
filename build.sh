export dockerregistry=registry.test.candela.eu/candela
docker build -t triplification:latest -f Dockerfile .
docker tag triplification:latest $dockerregistry/triplification:latest
docker push $dockerregistry/triplification:latest

