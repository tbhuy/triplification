from zipfile import ZipFile
import pandas as pd
import os
from triplification.functions import triplify, readTemplate, writeToFile
from triplification import upload_webdav
obs = {}
obs['hu'] = {
    'units': 'qudt-unit-1-1:Percent',
    'sensor': 'Higrometer',
    'observableProperty': 'Humidity',
    'unit':'',
    'cdt':'xsd:float'
}
obs['tx'] = {
    'units': 'qudt-unit-1-1:Celcius',
    'sensor': 'Thermometer',
    'observableProperty': 'Max_Temperature',
    'unit':'',
    'cdt':'xsd:float'
}
obs['tn'] = {
    'units': 'qudt-unit-1-1:Celcius',
    'sensor': 'Thermometer',
    'observableProperty': 'Min_Temperature',
    'unit':'',
    'cdt':'cdt:temperature'
}
obs['tg'] = {
    'units': 'qudt-unit-1-1:Celcius',
    'sensor': 'Thermometer',
    'observableProperty': 'Mean_Temperature',
    'unit':'',
    'cdt':'xsd:float'
    
}
obs['rr'] = {
    'units': 'qudt-unit-1-1:Millimeter',
    'sensor': 'Pluviometer',
    'observableProperty': 'Precipitation',
    'unit':'',
    'cdt':'xsd:float'
}
obs['fg'] = {
    'units': 'qudt-unit-1-1:MeterPerSecond',
    'sensor': 'Anemometer',
    'observableProperty': 'WindSpeed',
    'unit':'',
    'cdt':'xsd:float'
    
}

zips = ['ECA_blend_tx.zip',
        'ECA_blend_tn.zip',
        'ECA_blend_tg.zip', 
        'ECA_blend_hu.zip', 
        'ECA_blend_ss.zip',
        'ECA_blend_sd.zip', 
        'ECA_blend_rr.zip',
        'ECA_blend_cc.zip',
        'ECA_blend_dd.zip', 
        'ECA_blend_fg.zip',
       ]
 
template_ECAD = './triplification/template_Weather_ECAD.ttl'
template_Station_ECAD = './triplification/template_Station_ECAD.ttl'
URIBase = '<http://melodi.irit.fr/resource/'
maxRecordsPerFile = 10000
endpoint_URL = 'http://platform.candela-h2020.eu/semsearch/ep/Store'
endpoint_pass ='xxx'
endpoint_login = 'xxx'
webdav_URL = 'http://platform.candela-h2020.eu/semsearch/ep/permanent_data/permanent_data/'
webdav_login = 'xxx'
webdav_pass = 'xxx' 
webdav_path = '/usr/local/tomcat/webapps/ep/permanent_data/'


'''
endpoint_URL = 'http://melodi.irit.fr/weather/Store'
endpoint_pass ='melodi'
endpoint_login = 'candela'
webdav_URL = 'http://melodi.irit.fr/rdf/'
webdav_login = 'admin'
webdav_pass = 'noname' 
webdav_path = '/opt/tomcat/webapps/rdf/
'''


def triplify_Station(input_file,  station_id=34, output_folder='./rdf/'):
    stations = pd.read_csv(input_file, header=None, skiprows=19)
    station = stations.loc[stations[stations.columns[0]] == station_id]
   
    rdf = {}
    triples = []
    rdf['id'] = 'ECAD_' + str(station_id)
    rdf['alt'] = station.iloc[0, 5]   
    rdf['name'] = station.iloc[0, 1].strip()
    rdf['cn'] = station.iloc[0, 2]
    latd = station.iloc[0, 3]
    lond = station.iloc[0, 4]
    lat = int(latd[1:3]) + int(latd[4:6])/60 + int(latd[7:])/3600
    if latd[0:1] == '-':
        lat = lat * -1.0;        
    lon = int(lond[1:4]) + int(lond[5:7])/60 + int(lond[8:])/3600
    if lond[0:1] == '-':
        lon = lon * -1.0;
    rdf['wkt'] = 'POINT({} {})'.format(lon, lat)
    
    lsNameSpaces, lsTriplesTemplate = readTemplate(template_Station_ECAD)
    URI = URIBase +  'Station/' + "ECAD_" + str(station_id) + ">"
    triplesRow = triplify(rdf, lsTriplesTemplate, URI, "ECAD_" + str(station_id) )
    triples = triples + triplesRow
    for k, obsv in obs.items():
        triples.append([URI, 'sosa:hosts', '{}Sensor/ECAD_{}_{}>'.format(URIBase, str(station_id), obsv.get('sensor'))])
        triples.append(['{}Sensor/ECAD_{}_{}>'.format(URIBase, str(station_id), obsv.get('sensor')), 'a', 'wom:Sensor'])  
        triples.append(['{}Sensor/ECAD_{}_{}>'.format(URIBase, str(station_id), obsv.get('sensor')), 'sosa:observes', 
                        '{}ObservableProperty/{}>'.format(URIBase, obsv.get('observableProperty'))])  
        triples.append(['{}ObservableProperty/{}>'.format(URIBase, obsv.get('observableProperty')), 'a', 'wom:ObservableProperty'])  
        triples.append(['{}ObservableProperty/{}>'.format(URIBase, obsv.get('observableProperty')), 'rdfs:label', 
                                                          '"{}"^^xsd:string'.format(obsv.get('observableProperty'))])  
    
    file = os.path.join(output_folder, 'Station_ECAD' + '_' + str(station_id) + '.ttl')                   
    writeToFile(lsNameSpaces, triples, file)
    return file

#34 merignac #  2199  gourdon # 2027 torun
def triplify_dataset(input_folder, station_id=32, start_date=20170101, end_date=20171231, output_folder='./rdf/'):
    lsNameSpaces, lsTriplesTemplate = readTemplate(template_ECAD)
    triples = []
    files = []
    iFiles = 0
    iTriples = 0

    for zipf in zips:
        fn = list(zipf[-6:-4].upper() + '_STAID000000.txt')
        fn[14-len(str(station_id)):14] = str(station_id)
        fn = ''.join(fn)
        with ZipFile(os.path.join(input_folder, zipf), 'r') as zipObj:
            if fn in zipObj.namelist():
                zipObj.extract(fn)
                meteo = pd.read_csv(os.path.join(input_folder, fn), header=None, skiprows=21)
                meteo = meteo.astype(int)
                meteo = meteo[meteo[meteo.columns[2]] >= start_date]
                meteo = meteo[meteo[meteo.columns[2]] <= end_date]

                for index, row in meteo.iterrows():
                    obsv = {}
                    obsv['date'] = "{}-{}-{}T12:00:00".format(str(row[2])[0:4], str(row[2])[4:6], str(row[2])[6:])
                    obsv['rs'] = str(row[3]/10)
                    obsv['prop'] = obs[zipf[-6:-4]].get('observableProperty')
                    obsv['sensor'] = 'ECAD_' + str(station_id) + '_' + obs[zipf[-6:-4]].get('sensor')
                    URI = URIBase +  'WeatherObservation/' + "ECAD_" + str(station_id) + "_" + str(row[2]) + "_" + obsv['prop'] +  ">"
                    triplesRow = triplify(obsv, lsTriplesTemplate,
                                      URI, URI )            
                    triples = triples + triplesRow
                    if len(triples) > maxRecordsPerFile:
                        file = os.path.join(output_folder, 'Weather' + '_' + str(station_id) +'_' + str(start_date) + "_" 
                                            + str(end_date) + '_' + str(iFiles) + '.ttl')

                        writeToFile(lsNameSpaces, triples, file)
                        files.append(file)          
                        iFiles = iFiles + 1
                        iTriples = iTriples + len(triples)
                        triples = []

    file = os.path.join(output_folder, 'Weather' + '_' + str(station_id) +'_' + str(start_date) + "_" 
                                        + str(end_date) + '_' + str(iFiles) + '.ttl')
    files.append(file)    
    writeToFile(lsNameSpaces, triples, file)
    files.append(triplify_Station(os.path.join(input_folder, 'ECA_blend_station.txt'), station_id, output_folder))
        
    for upfile in files: 
        upload_webdav.upload_dataset(upfile, webdav_path, endpoint_URL, webdav_URL, endpoint_login, webdav_login, endpoint_pass, webdav_pass)
    
    return files    