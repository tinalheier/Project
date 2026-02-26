from roads import dele_veilinje
from terrain import horizon_mask_360
import rasterio
from pyproj import Transformer
import numpy as np
from geocentric_to_LG import azimuth_and_zenith 
from geocentric_to_LG import read_rinex_file
from rasterfiles import combine_tifs
import os
import pandas as pd 

from DOPcalculation import designMatrixA 
from emphererides_file import get_ephemerides, load_ephemerides

# horizon_mask_360(pointA, az_step, buffer, step) #Lat og long
# dele_veilinje(startpunkt, sluttpunkt, step): #UTM33


#Fra UTM zone 33N til WGS84 Earth-Centered Earth-Fixed (ECEF)
tf = Transformer.from_crs("EPSG:25833", "EPSG:4978", always_xy=True)

def find_available_sats(day, year, observation_time, maskElevation, max_elev_and_coord):
    day = str(day).zfill(3)
    base_path = os.path.join("data", "dataFrames", str(year), day)
    
        
    if not dataframeExists(day, year, base_path):
        get_ephemerides(day, year)
    
    GPS, Galileo, Beidou = load_ephemerides(day, year, base_path) 

    available_sats_point = {}

    for punkt, horizon in max_elev_and_coord.items():
        GPS_sats, Galileo_sats, Beidou_sats = azimuth_and_zenith(day, year, observation_time, punkt, maskElevation, GPS, Galileo, Beidou)
        
        GPS_updated = []
        Galileo_updated = []
        Beidou_updated= []

#print(punkt) (2815050.0861411192, 516548.4438278879, 5680854.373259013)   print(punkt[0])) 2815050.0861411192  print(punkt[1])) 516548.4438278879      print(punkt[2])) 5680854.373259013
#dette er horszon {0: -0.038151461429198966, 40: 4.011171678047463      print(horizon[40]) =  4.011171678047463), hente ut på nøkkel 40 grader
        
    
        for satname, x,y,z, az, zen in GPS_sats:

            sat_elev = 90 - zen
            nearest_az = min(horizon.keys(), key=lambda a: abs(a - az + 180) % 360 - 180)
            terrain_elev = horizon[nearest_az]
            if sat_elev > terrain_elev:
                GPS_updated.append((satname, x,y,z, az, sat_elev))

        for satname, x,y,z, az, zen in Galileo_sats:
            sat_elev = 90 - zen
            nearest_az = min(horizon.keys(), key=lambda a: abs(a - az))
            terrain_elev = horizon[nearest_az]
            if sat_elev > terrain_elev:
                Galileo_updated.append((satname, x,y,z, az, sat_elev))

        for satname, x,y,z, az, zen in Beidou_sats:
            sat_elev = 90 - zen
            nearest_az = min(horizon.keys(), key=lambda a: abs(a - az))
            terrain_elev = horizon[nearest_az]
            if sat_elev > terrain_elev:
                Beidou_updated.append((satname,x,y,z, az, sat_elev))
        
        available_sats_point[punkt] = {
        "GPS": GPS_updated,
        "Galileo": Galileo_updated,
        "Beidou": Beidou_updated
    }
        
    return available_sats_point

def dataframeExists(day, year, base_path):

    if not os.path.isdir(base_path):
        return False
    
    files = os.listdir(base_path)
    if len(files) == 0:
        return False
    
    return True

#finne max vinkel for alle azimuth på hele delstrekningen
#startpunkt og sluttpunkt er der man trykker i kartet, step_vei er veien stykket opp, step azimuth er step mellom 0-360
#buffer azimtuh er hvor langt den søker totalt, og step utover buffer er når den søker ut til buffer på en azimtuh
def find_max_elev_horizon_360(raster_path, startpunkt, sluttpunkt, step_vei, step_azimuth, buffer_azimuth, step_utover_buffer):
    
    with rasterio.open(raster_path) as src: 
        all_points_along_road = dele_veilinje(startpunkt, sluttpunkt, step_vei)
        elevation_along_road_360 = {}

        for point in all_points_along_road:

            point_ECEF = tf.transform(point[0], point[1], point[2])
            max_elevation = horizon_mask_360(src, point, step_azimuth, buffer_azimuth, step_utover_buffer)
            elevation_along_road_360[point_ECEF] = max_elevation

    return elevation_along_road_360

    src.close()



def last(startpunkt, sluttpunkt, day, year, obs_time):
    merged_tif = combine_tifs(
    startpunkt,
    sluttpunkt,
    folder_path="data/DTM_nasjonal/",
    buffer=10000
)
    try:
        sjekk = find_max_elev_horizon_360(
            merged_tif,
            startpunkt,
            sluttpunkt,
            50,
            40,
            10000,
            10
        )
        result = find_available_sats(day, year, obs_time, 45, sjekk)

        matrix = designMatrixA(result)

    finally:
        if os.path.exists(merged_tif):
            os.remove(merged_tif)
            print("Slettet midlertidig raster:", merged_tif)

    return matrix




# # #TRD
# startpunkt = 270353.68,7040091.61 
# sluttpunkt = 270386.58,7039786.7

#Lærdal
startpunkt = 49379.22356892761,6773638.5790781425
sluttpunkt = 87964.31359693682,6767233.745804535

Day = 35
year = 2025
OBS_TIME = "033000"


hey = last(startpunkt, sluttpunkt, Day, year, OBS_TIME)

print(hey)


