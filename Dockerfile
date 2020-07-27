FROM python:3.7
MAINTAINER Ba Huy Tran "ba-huy.tran@irit.fr"
ENV SERVER_PATH '/usr/local/tomcat/webapps/ep/permanent_data/'
ENV WEBDAV 'http://platform.candela-h2020.eu/semsearch/ep/permanent_data/permanent_data/'
ENV WEBDAV_LOGIN 'admin'
ENV ENDPOINT 'http://platform.candela-h2020.eu/semsearch/ep/Store'
ENV NTRIPLES 10000

RUN apt-get update -y
RUN apt-get install -y software-properties-common
RUN apt-get update -y
RUN apt-get upgrade -y
RUN apt-get install -y python-numpy gdal-bin libgdal-dev
RUN pip3 install rasterio shapely geopandas geojson jsonpath pandas pycurl pyshp rdflib requests webdavclient3 matplotlib
RUN pip3 show rasterio geopandas
 
#copy the directory containing python code to the container
COPY triplification /application/triplification
#COPY templates /application/templates
#copy the actual application main script to the container
COPY main.py /application/main.py
COPY links.ds /application/links.ds
#Run app.py when the container launches
WORKDIR /application
CMD ["python3", "main.py"]

