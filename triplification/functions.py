import jsonpath
import json
import datetime
import subprocess
from urllib.parse import quote
import requests
from shapely.wkt import loads
from builtins import str
from os.path import isfile, isdir, join, abspath, splitext, getsize
from os import listdir
from requests.auth import HTTPBasicAuth
import urllib.parse
from dateutil.parser import parse


URIBase = '<http://melodi.irit.fr/resource/'
dictObsVar = {}
dictObsVar['pmer'] = {
    'units': 'qudt-unit-1-1:Pascal',
    'sensor': 'Barometer',
    'description': 'Pression au niveau mer',
    'observableProperty': 'l-mfo:AtmosphericPressure',
    'procedure': 'l-mfo:procedure_pmer'
}

dictObsVar['tend'] = {
    'units': 'qudt-unit-1-1:Pascal',  # 3
    'sensor': 'Barometer',
    'description': 'Variation de pression en 3 heures',
    'observableProperty': 'l-mfo:AtmosphericPressure',
    'procedure': 'l-mfo:procedure_tend'
}

dictObsVar['cod_tend'] = {
    'units': 'synopMeteoFranceCode:Code_0200',
    'sensor': 'Barometer',
    'description': 'Type de tendance barometrique, code (0200)',
    'observableProperty': 'l-mfo:AtmosphericPressure',
    'procedure': 'l-mfo:procedure_cod_tend'
}

dictObsVar['dd'] = {
    'units': 'qudt-unit-1-1:DegreeAngle',
    'timePhenomenonObservation':  0,  # 0.1666667,
    'sensor': 'Anemometer',
    'description': 'Direction du vent moyen 10mn',
    'observableProperty': 'l-mfo:WindSpeed',
    'procedure': 'l-mfo:procedure_dd'
}
dictObsVar['ff'] = {
    'units': 'qudt-unit-1-1:MeterPerSecond',
    'timePhenomenonObservation':  0,  # 0.1666667,
    'sensor': 'Anemometer',
    'description': 'Vitesse du vent moyen 10mn',
    'observableProperty': 'l-mfo:WindSpeed',
    'procedure': 'l-mfo:procedure_ff'
}
dictObsVar['t'] = {
    'units': 'qudt-unit-1-1:Kelvin',
    'sensor': 'Thermometer',
    'description': 'Temperature',
    'observableProperty': 'l-mfo:Temperature',
    'procedure': 'l-mfo:procedure_t'
}

dictObsVar['td'] = {
    'units': 'qudt-unit-1-1:Kelvin',
    'sensor': 'Thermometer',
    'description': 'Point de rosee',
    'observableProperty': 'l-mfo:Temperature',
    'procedure': 'l-mfo:procedure_td'
}
dictObsVar['u'] = {
    'units': 'qudt-unit-1-1:Percent',
    'sensor': 'Higrometer',
    'description': 'Humidite',
    'observableProperty': 'l-mfo:Humidity',
    'procedure': 'l-mfo:procedure_u'
}
dictObsVar['vv'] = {
    'units': 'qudt-unit-1-1:Meter',
    'sensor': 'VisibilitySensor',
    'description': 'Visibilite horizontale',
    'observableProperty': 'l-mfo:Visibility',
    'procedure': 'l-mfo:procedure_vv'
}

dictObsVar['ww'] = {
    'units': 'synopMeteoFranceCode:Code_4677',
    'sensor': 'xSensor',
    'description': 'Temps present (code 4677)',
    'procedure': 'l-mfo:procedure_ww',
    'observableProperty': 'l-mfo:WeatherConditions'
}
dictObsVar['w1'] = {
    'units': 'synopMeteoFranceCode:Code_4561',
    'sensor': 'xSensor',
    'description': 'Temps passe (code 4561)',
    'procedure': 'l-mfo:procedure_w1',
    'observableProperty': 'l-mfo:WeatherConditions'
}
dictObsVar['w2'] = {
    'units': 'synopMeteoFranceCode:Code_4661',
    'sensor': 'xSensor',
    'description': 'Temps pasee (code 4561)',
    'procedure': 'l-mfo:procedure_w2',
    'observableProperty': 'l-mfo:WeatherConditions'
}

dictObsVar['n'] = {
    'units': 'qudt-unit-1-1:Percent',
    'sensor': 'Ceilometer',
    'description': 'Nebulosite totale',
    'observableProperty': 'l-mfo:CloudCover',
    'procedure': 'l-mfo:procedure_n'
}
dictObsVar['nbas'] = {
    'units': 'synopMeteoFranceCode:octa',
    'sensor': 'Ceilometer',
    'description': 'Nebulosite des nuages de l\'etage inferieur',
    'observableProperty': 'l-mfo:CloudCover',
    'procedure': 'l-mfo:procedure_nbas'
}
dictObsVar['hbas'] = {
    'units': 'qudt-unit-1-1:Meter',
    'sensor': 'Ceilometer',
    'description': 'Hauteur de la base des nuages de l\'etage inferieur',
    'observableProperty': 'l-mfo:CloudCover',
    'procedure': 'l-mfo:procedure_hbas'
}

dictObsVar['cl'] = {
    'units': 'synopMeteoFranceCode:Code_0513',
    'sensor': 'Ceilometer',
    'description': 'Type des nuages de l\'etage inferieur',
    'procedure': 'l-mfo:procedure_cl',
    'observableProperty': 'l-mfo:CloudCover',
}
dictObsVar['cm'] = {
    'units': 'synopMeteoFranceCode:Code_0515',
    'sensor': 'Ceilometer',
    'description': 'Type des nuages de l\'etage moyen',
    'procedure': 'l-mfo:procedure_cm',
    'observableProperty': 'l-mfo:CloudCover',
}
dictObsVar['ch'] = {
    'units': 'synopMeteoFranceCode:Code_0509',
    'sensor': 'Ceilometer',
    'description': 'Types des nuages de l\'etage superieur',
    'procedure': 'l-mfo:procedure_ch',
    'observableProperty': 'l-mfo:CloudCover',
}

dictObsVar['pres'] = {
    'units': 'qudt-unit-1-1:Pascal',
    'sensor': 'Barometer',
    'description': 'Pression station',
    'observableProperty': 'l-mfo:AtmosphericPressure',
    'procedure': 'l-mfo:procedure_pres'
}

dictObsVar['niv_bar'] = {
    'units': 'qudt-unit-1-1:Pascal',
    'sensor': 'Barometer',
    'description': 'Niveau barometrique',
    'observableProperty': 'l-mfo:AtmosphericPressure',
    'procedure': 'l-mfo:procedure_niv_bar'
}
dictObsVar['geop'] = {
    'units': 'synopMeteoFranceCode:squareMeterPerSquareSecond',
    'sensor': 'Geopotential',
    'description': 'Geopotential',
    'procedure': 'l-mfo:procedure_geop',
    'observableProperty': 'l-mfo:Geopotential',
}

dictObsVar['tend24'] = {
    'units': 'qudt-unit-1-1:Pascal',
    'sensor': 'Barometer',
    'description': 'Variation de pression en 24 heures',
    'observableProperty': 'l-mfo:AtmosphericPressure',
    'procedure': 'l-mfo:procedure_tend24'
}
dictObsVar['tn12'] = {
    'units': 'qudt-unit-1-1:Kelvin',
    'sensor': 'Thermometer',
    'description': 'Temperature minimale sur 12 heures',
    'observableProperty': 'l-mfo:Temperature',
    'procedure': 'l-mfo:procedure_tn12'
}
dictObsVar['tn24'] = {
    'units': 'qudt-unit-1-1:Kelvin',
    'sensor': 'Thermometer',
    'description': 'Temperature minimale sur 24 heures',
    'observableProperty': 'l-mfo:Temperature',
    'procedure': 'l-mfo:procedure_tn24'
}

dictObsVar['tx12'] = {
    'units': 'qudt-unit-1-1:Kelvin',
    'sensor': 'Thermometer',
    'description': 'Temperature maximale sur 12 heures',
    'observableProperty': 'l-mfo:Temperature',
    'procedure': 'l-mfo:procedure_tx12'
}
dictObsVar['tx24'] = {
    'units': 'qudt-unit-1-1:Kelvin',
    'sensor': 'Thermometer',
    'description': 'Temperature maximale sur 24 heures',
    'observableProperty': 'l-mfo:Temperature',
    'procedure': 'l-mfo:procedure_tx24'
}
dictObsVar['tminsol'] = {
    'units': 'qudt-unit-1-1:Kelvin',
    'sensor': 'Thermometer',
    'description': 'Temperature minimale du sol sur 12 heures',
    'observableProperty': 'l-mfo:Temperature',
    'procedure': 'l-mfo:procedure_tminsol'
}

dictObsVar['tw'] = {
    'units': 'qudt-unit-1-1:Kelvin',
    'sensor': 'Thermometer',
    'description': 'Temperature du thermometre mouille',
    'observableProperty': 'l-mfo:Temperature',
    'procedure': 'l-mfo:procedure_tw'
}
dictObsVar['raf10'] = {
    'units': 'qudt-unit-1-1:MeterPerSecond',
    'sensor': 'Anemometer',
    'description': 'Rafales sur les 10 dernieres minutes',
    'observableProperty': 'l-mfo:WindSpeed',
    'procedure': 'l-mfo:procedure_raf10'
}

dictObsVar['rafper'] = {
    'units': 'qudt-unit-1-1:MeterPerSecond',
    'sensor': 'Anemometer',
    'description': 'Rafales sur une periode',
    'observableProperty': 'l-mfo:WindSpeed',
    'procedure': 'l-mfo:procedure_rafper'
}
dictObsVar['per'] = {
    'units': 'qudt-unit-1-1:MinuteTime',
    'sensor': 'Timer',
    'description': 'Periode de mesure de la rafale',
    'procedure': 'l-mfo:procedure_per',
    'observableProperty': 'l-mfo:WindSpeed'
}
dictObsVar['etat_sol'] = {
    'units': 'synopMeteoFranceCode:Code_0901',
    'sensor': 'xSensor',
    'description': 'Etat du sol',
    'procedure': 'l-mfo:procedure_etat_sol',
    'observableProperty': 'l-mfo:SoilCondition'
}

dictObsVar['ht_neige'] = {
    'units': 'qudt-unit-1-1:Meter',
    'sensor': 'SnowGauge',
    'description': 'Hauteur totale de la couche de neige, glace, autre au sol',
    'observableProperty': 'l-mfo:SnowFall',
    'procedure': 'l-mfo:procedure_ht_neige'
}
dictObsVar['ssfrai'] = {
    'units': 'qudt-unit-1-1:Meter',
    'sensor': 'SnowGauge',
    'description': 'Hauteur de la neige fraiche',
    'observableProperty': 'l-mfo:SnowFall',
    'procedure': 'l-mfo:procedure_ssfrai'
}
dictObsVar['perssfrai'] = {
    'units': 'synopMeteoFranceCode:TenthOfHour',
    'sensor': 'Timer',
    'description': 'Periode de mesure de la neige fraiche',
    'observableProperty': 'l-mfo:SnowFall',
    'procedure': 'l-mfo:procedure_perssfrai'
}

dictObsVar['rr1'] = {
    'units': 'qudt-unit-1-1:Millimeter',
    'sensor': 'Pluviometer',
    'description': 'Precipitations dans 1 derniere heure',
    'observableProperty': 'l-mfo:Rain',
    'procedure': 'l-mfo:procedure_rr1'

}
dictObsVar['rr3'] = {
    'units': 'qudt-unit-1-1:Millimeter',
    'sensor': 'Pluviometer',
    'description': 'Precipitations dans les 3 derniere heures',
    'observableProperty': 'l-mfo:Rain',
    'procedure': 'l-mfo:procedure_rr3'
}
dictObsVar['rr6'] = {
    'units': 'qudt-unit-1-1:Millimeter',
    'sensor': 'Pluviometer',
    'description': 'Precipitations dans les 6 derniere heures',
    'observableProperty': 'l-mfo:Rain',
    'procedure': 'l-mfo:procedure_rr6'
}
dictObsVar['rr12'] = {
    'units': 'qudt-unit-1-1:Millimeter',
    'sensor': 'Pluviometer',
    'description': 'Precipitations dans les 12 derniere heures',
    'observableProperty': 'l-mfo:Rain',
    'procedure': 'l-mfo:procedure_rr12'
}
dictObsVar['rr24'] = {
    'units': 'qudt-unit-1-1:Millimeter',
    'sensor': 'Pluviometer',
    'description': 'Precipitations dans les 24 derniere heures',
    'observableProperty': 'l-mfo:Rain',
    'procedure': 'l-mfo:procedure_rr24'
}

dictObsVar['phenspe1'] = {
    'units': 'synopMeteoFranceCode:Code_3778',
    'sensor': 'xSensor', 'description': 'Phenomene special code(3778)',
    'observableProperty': 'l-mfo:SpecialPhenomene',
    'procedure': 'l-mfo:procedure_phenspe1'
}
dictObsVar['phenspe2'] = {
    'units': 'synopMeteoFranceCode:Code_3778',
    'sensor': 'xSensor', 'description': 'Phenomene special code(3778)',
    'observableProperty': 'l-mfo:SpecialPhenomene',
    'procedure': 'l-mfo:procedure_phenspe2'
}
dictObsVar['phenspe3'] = {
    'units': 'synopMeteoFranceCode:Code_3778',
    'sensor': 'xSensor',
    'description': 'Phenomene special code(3778)',
    'observableProperty': 'l-mfo:SpecialPhenomene',
    'procedure': 'l-mfo:procedure_phenspe3'
}
dictObsVar['phenspe4'] = {
    'units': 'synopMeteoFranceCode:Code_3778',
    'sensor': 'xSensor',
    'description': 'Phenomene special code(3778)',
    'observableProperty': 'l-mfo:SpecialPhenomene',
    'procedure': 'l-mfo:procedure_phenspe4'
}

dictObsVar['nnuage1'] = {
    'units': 'synopMeteoFranceCode:Octa',
    'sensor': 'Ceilometer',
    'description': 'Nebulosite cche nuageuse',
    'procedure': 'l-mfo:procedure_nnuage1',
    'observableProperty': 'l-mfo:CloudCover',
}
dictObsVar['ctype1'] = {
    'units': 'synopMeteoFranceCode:Code_0500',
    'sensor': 'Ceilometer',
    'description': 'Type Nuage',
    'observableProperty': 'l-mfo:CloudCover',
    'procedure': 'l-mfo:procedure_ctype1'
}
dictObsVar['hnuage1'] = {
    'units': 'qudt-unit-1-1:Meter',
    'sensor': 'Ceilometer',
    'description': 'Hauteur de base',
    'observableProperty': 'l-mfo:CloudCover',
    'procedure': 'l-mfo:procedure_hnuage1'
}

dictObsVar['nnuage2'] = {
    'units': 'synopMeteoFranceCode:Octa',
    'sensor': 'Ceilometer',
    'description': 'Nebulosite cche nuageuse',
    'observableProperty': 'l-mfo:CloudCover',
    'procedure': 'l-mfo:procedure_nnuage2'

}
dictObsVar['ctype2'] = {
    'units': 'synopMeteoFranceCode:Code_0500',
    'description': 'Type Nuage',
    'observableProperty': 'l-mfo:CloudCover',
    'procedure': 'l-mfo:procedure_ctype2',
    'sensor': 'Ceilometer',
}
dictObsVar['hnuage2'] = {
    'units': 'qudt-unit-1-1:Meter',
    'sensor': 'Ceilometer',
    'description': 'Hauteur de base',
    'observableProperty': 'l-mfo:CloudCover',
    'procedure': 'l-mfo:procedure_hnuage2',
}

dictObsVar['nnuage3'] = {
    'units': 'synopMeteoFranceCode:Octa',
    'sensor': 'Ceilometer',
    'description': 'Nebulosite cche nuageuse',
    'observableProperty': 'l-mfo:CloudCover',
    'procedure': 'l-mfo:procedure_nnuage3'
}
dictObsVar['ctype3'] = {
    'units': 'synopMeteoFranceCode:Code_0500',
    'sensor': 'Ceilometer',
    'description': 'Type Nuage',
    'observableProperty': 'l-mfo:CloudCover',
    'procedure': 'l-mfo:procedure_ctype3'

}
dictObsVar['hnuage3'] = {
    'units': 'qudt-unit-1-1:Meter',
    'sensor': 'Ceilometer',
    'description': 'Hauteur de base',
    'observableProperty': 'l-mfo:CloudCover',
    'procedure': 'l-mfo:procedure_hnuage3'
}

dictObsVar['nnuage4'] = {
    'units': 'synopMeteoFranceCode:Octa',
    'sensor': 'Ceilometer',
    'description': 'Nebulosite cche nuageuse',
    'observableProperty': 'l-mfo:CloudCover',
    'procedure': 'l-mfo:procedure_nnuage4'

}
dictObsVar['ctype4'] = {
    'units': 'synopMeteoFranceCode:Code_0500',
    'sensor': 'Ceilometer',
    'description': 'Type Nuage',
    'observableProperty': 'l-mfo:CloudCover',
    'procedure': 'l-mfo:procedure_ctype4'
}
dictObsVar['hnuage4'] = {
    'units': 'qudt-unit-1-1:Meter',
    'sensor': 'Ceilometer',
    'description': 'Hauteur de base',
    'observableProperty': 'l-mfo:CloudCover',
    'procedure': 'l-mfo:procedure_hnuage4'
}

lsTimeInstants = []
lsTimeIntervals = []

# Generic Functions


def valueToLiteral(value, parameter, triple):
    
    if not isinstance(value, str):
        value = str(value)
    if parameter == "wktLiteral":
        triple[2] = '"' + value + '"' + '^^geo:' + parameter
    else:
        triple[2] = '"' + value + '"' + '^^xsd:' + parameter
    return [triple]

# The value is composed of two date (Start and End). There are a space between them.
def valueToInstant(value, triple):
    instant = parse(value,  ignoretz=True)
 
    

def valueToInterval(value, triple):
    
    dStart = datetime.datetime.strptime(
        value.split()[0], '%Y-%m-%d')
    dEnd = datetime.datetime.strptime(value.split()[1], '%Y-%m-%d')
    stIntervalUri = URIBase + "Interval/" + \
        str(int(dStart.timestamp())) + '_' + \
        str(int(dEnd.timestamp())) + ">"
    if value in lsTimeIntervals:
        triple[2] = stIntervalUri
        triples = [triple]
    else:
        triple[2] = stIntervalUri
        lsTimeIntervals.append(value)
        triples = [triple]
        triples = triples + \
            createInterval(dStart.timestamp(), dEnd.timestamp())
    return triples

def valueToInstant(dEpoch, triple):
    triple[2] = URIBase + "Instant/" + str(int(dEpoch)) + ">"
    triples = [triple] + createInstant(dEpoch)

    return triples


def createInstant(dEpoch):
    stEpoch = str(int(dEpoch))
    triples = []
    stInstantUri = URIBase + "Instant/" + stEpoch + ">"
    lsTimeInstants.append(stEpoch)
    timeAsXSD = '"' + \
        datetime.datetime.fromtimestamp(dEpoch).isoformat(
            'T') + '"' + '^^xsd:dateTime'
    # xTriple_01 = [lsTimeInstants[stEpoch], 'a', 'time:Instant']
    xTriple_02 = [stInstantUri,
                  'time:inXSDDateTime', timeAsXSD]
    # xTriple_03 = [dictTimeInstants[stEpoch], 'time:inXSDDateTimeStamp', timeAsXSDStamp]
    triples = [xTriple_02]  # , xTriple_03]

    return triples


def createInterval(dBegin, dEnd):
    stIntervalUri = URIBase + "Interval/" + \
        str(int(dBegin)) + '_' + str(int(dEnd)) + ">"
    triples = []
    beginURI = URIBase + "Instant/" + \
        str(int(dBegin)) + ">"
    endURI = URIBase + "Instant/" + \
        str(int(dEnd)) + ">"
    # xTriple_01 = [stIntervalUri, 'a', 'time:Interval']
    xTriple_02 = [stIntervalUri, 'time:hasBeginning', beginURI]
    xTriple_03 = [stIntervalUri, 'time:hasEnd', endURI]
    triples = [xTriple_02, xTriple_03]

    if str(int(dBegin)) not in lsTimeInstants:
        triples = triples + \
            createInstant(dBegin)
    if str(int(dEnd)) not in lsTimeInstants:
        triples = triples + \
            createInstant(dEnd)
    return triples

# parameters define the beginning and the end (optional, use '-' to bypass) of the URI


def valueToURI(value, parameters, triple):
    
    URI = ''
    params = parameters.split(' ')
    if len(params) != 2:
        triple[2] = "<" + value + ">"
    else:
        if params[0].strip() != "-":
            URI = URI + params[0].strip()
        URI = URI + value
        if params[1].strip() != "-":
            URI = URI + params[1].strip()
        triple[2] = "<" + URI + ">"

    return [triple]

def valueToClass(value, triple):

    if isinstance(value, list):
        rs = []
        for val in value:
            triple[2] = URI + val + ">"
         
            rs.append([triple[0], triple[1], val])
        return rs
    else:
        triple[2] = value
        return [triple]

# parameters define the class of the instance
def valueToInstance(value, parameter, triple):
    
    if "/" in parameter.strip():
        URI = URIBase + parameter
    else:
        URI = URIBase + parameter + "/"
    if isinstance(value, list):
        rs = []
        for val in value:
            triple[2] = URI + val + ">"
         
            rs.append([triple[0], triple[1], URI + val + ">" ])
        return rs
    else:
        triple[2] = URI + value + ">"
        return [triple]


# Functions for AU
def getInseeURI(insee, triple):
    
    URI = 'http://id.insee.fr/geo/'
    if len(insee) == 2:
        URI = URI + 'region/' + insee
    elif len(insee) == 3:
        URI = URI + 'departement/' + insee
    else:
        URI = URI + 'commune/' + insee
    URI = '<' + URI + '>'
    triple[2] = URI
    return [triple]

# Functions for EO


def getAdminType(adminType, triple):
    
    URI = 'admin:Other'
    if 'region' in adminType:
        URI = 'admin:Region'
    elif 'departement' in adminType:
        URI = 'admin:Departement'
    elif 'commune' in adminType:
        URI = 'admin:Commune'
    elif 'canton' in adminType:
        URI = 'admin:Canton'
    elif 'Arrondissement' in adminType:
        URI = 'admin:Arrondissement'
    triple[2] = URI
    return [triple]

# Ba Huy: It would be faster to use
# from shapely.geometry import shape
# geom = shape(geojson)
# geom.wkt


def getMFO_Result(jsonObs, triple):
    #    {'rr3': 1.6, 'temporalInfo': {'year': '2018', 'month': '01', 'day': '18', 'timeStamp': 1516309200.0, 'hour': '21'}, 'numer_sta': '07037'}
    setKeys = jsonObs.keys()
    lsKeys = list(setKeys)
    lsNotKeys = ['date', 'numer_sta', 'id']
    lsOneKey = [item for item in lsKeys if item not in lsNotKeys]
    stKey = lsOneKey[0]
    if str(jsonObs[stKey]) == 'nan':
        return []
    stNumericValue = '"' + str(jsonObs[stKey]) + '"' + '^^xsd:double'
    newTimeSubject = URIBase + "Result/" + jsonObs['id'] + "_" + stKey + ">"
    xTriple_00 = [triple[0], triple[1], newTimeSubject]
   # xTriple_01 = [newTimeSubject, 'a', 'o-mfo:Result']
   # xTriple_02 = [newTimeSubject, 'a', 'qudt-1-1:QuantitativeValue']
    xTriple_03 = [newTimeSubject, 'qudt-1-1:unit', dictObsVar[stKey]['units']]
    xTriple_04 = [newTimeSubject, 'qudt-1-1:numericValue', stNumericValue]
    triples = [xTriple_00, xTriple_03, xTriple_04]
    return triples


def getMFO_Sensors(numer_sta, triple):
    sensor_triples = []
    sensors = []
    props = []
    for obs in dictObsVar:
        # print(dictObsVar[obs])
        if dictObsVar[obs]['sensor'] not in sensors:
            sensors.append(dictObsVar[obs]['sensor'])
            t = triple.copy()
            t[2] = URIBase + 'Sensor/' + \
                numer_sta + "_" + dictObsVar[obs]['sensor'].lower() + ">"

           # t1 = [URIBase + 'Sensor/' + dictObsVar[obs] + ['sensor'].lower() + "-" + numer_sta + ">", 'a', 'sosa:Sensor']
            t1 = [URIBase + 'Sensor/' +
                  dictObsVar[obs]['sensor'].lower() + "-" +
                  numer_sta + ">", 'sosa:observes',
                  URIBase + 'ObservableProperty/' + dictObsVar[obs]['observableProperty'].lower()[6:] + ">"]
           # if dictObsVar[obs]['observableProperty'].lower()[6:] not in props:
           #     sensor_triples.append(['<http://melodi.irit.fr/ressource/ObservableProperty/' + dictObsVar[obs]['observableProperty'].lower()[6:], 'a', 'sosa:ObservableProperty'])
           #    props.append(dictObsVar[obs]['observableProperty'].lower()[6:])
            sensor_triples.append(t)
            sensor_triples.append(t1)
            # sensor_triples.append(t2)

    return sensor_triples


def getMFO_ObservedProperty(jsonObs, triple):
    #    {'rr3': 1.6, 'temporalInfo': {'year': '2018', 'month': '01', 'day': '18', 'timeStamp': 1516309200.0, 'hour': '21'}, 'numer_sta': '07037'}
    # print(jsonObs)
    setKeys = jsonObs.keys()
    lsKeys = list(setKeys)
    lsNotKeys = ['date', 'numer_sta', 'id']
    lsOneKey = [item for item in lsKeys if item not in lsNotKeys]
    stKey = lsOneKey[0]
    triple[2] = URIBase + 'ObservableProperty/' + \
        dictObsVar[stKey]['observableProperty'].lower()[6:] + ">"
    triples = [triple]
    return triples


def getMFO_URI_Sensor(jsonObs, triple):
    #    {'rr3': 1.6, 'temporalInfo': {'year': '2018', 'month': '01', 'day': '18', 'timeStamp': 1516309200.0, 'hour': '21'}, 'numer_sta': '07037'}
    setKeys = jsonObs.keys()
    lsKeys = list(setKeys)
    lsNotKeys = ['date', 'numer_sta', 'id']
    lsOneKey = [item for item in lsKeys if item not in lsNotKeys]
    stKey = lsOneKey[0]
    uriSensor = URIBase + 'Sensor/' + \
        jsonObs['numer_sta'] + "_" + dictObsVar[stKey]['sensor'].lower() + ">"
    triple[2] = uriSensor
    triples = [triple]
    return triples


def getMFO_UsedProcedure(jsonObs, triple):
    setKeys = jsonObs.keys()
    lsKeys = list(setKeys)
    lsNotKeys = ['date', 'numer_sta', 'id']
    lsOneKey = [item for item in lsKeys if item not in lsNotKeys]
    stKey = lsOneKey[0]
    uriProcedure = dictObsVar[stKey]['procedure']
    triple[2] = URIBase + "Procedure/" + stKey + ">"
    triples = [triple]
    return triples


def triplify(jsonDoc, lsTriplesTemplate, uriDummy, URI='', URI2=''):
    triples = []
    for t in lsTriplesTemplate:
        if len(t) < 3:
            continue
        # print(t)
        tripleSubject = t[0].strip()
        triplePredicate = t[1].strip()
        tripleObject = t[2].strip()
        if tripleObject[-1] == '.':
            tripleObject = tripleObject[:-1]
        functionName = ''
        if 'dummy' in tripleSubject:
            if len(tripleSubject) == 5:
                tripleSubject = tripleSubject.replace('dummy', uriDummy)
            elif '__' in tripleSubject:  # Transform URI based on the Object Class
                tripleSubject = tripleSubject.replace(
                    'dummy__', URIBase)
                tripleSubject = tripleSubject + "/" + URI2 + ">"
            elif '_' in tripleSubject:  # Transform URI based on the Object Class
                tripleSubject = tripleSubject.replace(
                    'dummy_', URIBase)
                tripleSubject = tripleSubject + "/" + URI + ">"

        if 'dummy' in tripleObject:
            tripleObject = tripleObject.replace(
                'dummy_', URIBase)
            tripleObject = tripleObject + "/" + URI + ">"

        if '(' in tripleObject and ')' in tripleObject:
            functionName = tripleObject[0:tripleObject.index('(')]
            if ',' in tripleObject:
                parameters = tripleObject[tripleObject.index(
                    ',') + 1:tripleObject.index(')')]
                parameterJsonPath = tripleObject[tripleObject.index(
                    '(') + 1:tripleObject.index(',')]
            else:
                parameters = ''
                parameterJsonPath = tripleObject[tripleObject.index(
                    '(') + 1:tripleObject.index(')')]

            if parameterJsonPath == 'doc':
                parameterJsonValue = jsonDoc
            else:
                if jsonpath.jsonpath(jsonDoc, parameterJsonPath) != False:
                    parameterJsonValue = jsonpath.jsonpath(
                        jsonDoc, parameterJsonPath)[0]

        tripleToProcess = [tripleSubject, triplePredicate, tripleObject]
        if functionName:
            lsProcessedTriple = processFunction(
                functionName.strip(), parameterJsonValue, parameters.strip(), tripleToProcess)
        else:
            lsProcessedTriple = [tripleToProcess]
        if (lsProcessedTriple is not None):
            triples = triples + lsProcessedTriple
    return triples


def readTemplate(stTemplateFile):
    file2Open = open(stTemplateFile, "r")
    lsLines = file2Open.readlines()
    lsTriples = []
    lsNameSpaces = []
    for l in lsLines:
        if len(l) > 0:
            if l[0] == '@':
                lsNameSpaces.append(l)
            elif l[0] == '#':
                pass
            else:
                lsElements = l.split(' ')
                if len(lsElements) > 3:
                    lsTriples.append(
                        [lsElements[0], lsElements[1], ' '.join(lsElements[2:])])
                else:
                    lsTriples.append(lsElements[0:3])
    return lsNameSpaces, lsTriples


def writeToFile(lsNameSpaces, lsTriples, stFileName):
    print('Writing triples to file: ', stFileName)
    file2Open = open(stFileName, "w", encoding='utf-8')
    #g = Graph()
    triples = []

    triples.extend(lsNameSpaces)
    for n in lsNameSpaces:
        file2Open.write(n)
    for l in lsTriples:
        # print(l)
        try:
            if l[0] is not None and l[1] is not None and l[2] is not None:

                file2Open.write(l[0] + ' ' + l[1] + ' ' + l[2] + '.' + '\n')
                #triples.append(l[0] + ' ' + l[1] + ' ' + l[2] + '.')
        except:
            # print(l)
            try:
                for ls in l:
                    if ls[0] is not None and ls[1] is not None and ls[2] is not None:
                        file2Open.write(ls[0] + ' ' + ls[1] + ' ' + ls[2] + '.\n')
                        #triples.append(ls[0] + ' ' + ls[1] + ' ' + ls[2] + '.')
            except:
                print('problems: ', l)
                pass
    file2Open.flush()
    file2Open.close()
    #g.parse(data="\n".join(triples), format='turtle')
    #g.serialize(destination=stFileName, format='turtle', encoding='utf-8')


def processFunction(functionName, variables, parameters, triple):
    func = globals()[functionName]
    if variables is None or variables == "":
        return None
    if parameters == '':
        result = func(variables, triple)
    else:
        result = func(variables, parameters, triple)
    return result