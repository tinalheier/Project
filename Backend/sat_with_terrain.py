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

def main(startpunkt, sluttpunkt, day, year, obs_time, maskangle, active_GNSS):
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
            10,
            19000, #10-15k ble for kort
            10
        )

        result = find_available_sats(day, year, obs_time, maskangle, sjekk)
        dict_w_DOP = designMatrixA(result, active_GNSS)

    finally:
        if os.path.exists(merged_tif):
            os.remove(merged_tif)
            print("Slettet midlertidig raster:", merged_tif)

    return dict_w_DOP



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
            nearest_az = min(horizon.keys(), key=lambda a: abs((a - az + 180) % 360 - 180))
            terrain_elev = horizon[nearest_az]
            if sat_elev > terrain_elev:
                GPS_updated.append((satname, x,y,z, az, sat_elev))

        for satname, x,y,z, az, zen in Galileo_sats:
            sat_elev = 90 - zen
            nearest_az = min(horizon.keys(), key=lambda a: abs((a - az + 180) % 360 - 180))
            terrain_elev = horizon[nearest_az]
            if sat_elev > terrain_elev:
                Galileo_updated.append((satname, x,y,z, az, sat_elev))

        for satname, x,y,z, az, zen in Beidou_sats:
            sat_elev = 90 - zen
            nearest_az = min(horizon.keys(), key=lambda a: abs((a - az + 180) % 360 - 180))
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




#Returnerer dict på formen:
#(3093078.660852142, 365968.15045084106, 5547352.932991824): {'GPS': 
#[('G05', -1342355.9322939492, -20603433.52312917, 16497819.82694112, 1.482270586177253, 79.69943589468461), ('G20', 8790390.114376752, -12830156.931231089, 21628893.11728327, 
# 0.810439663935219, 47.87219019399329), ('G25', -17474521.44288167, -19658330.772733476, 4241569.639101882, 3.8361402083027025, 53.707918647436664), 
# ('G29', -9988455.682830317, -12053183.764650533, 21394018.337013517, 5.474416719139785, 66.05376600799552)], 'Galileo': [('E02', -17928611.558935527, -22372409.353924595, 
# 7394548.1003797855, 3.870521527091352, 60.352616872536956), ('E18', 6355363.64036415, -21676521.661827706, 6267762.404535926, 2.1577484476224287, 50.63060165560439), 
# ('E34', -21566772.192889698, -11304319.532022033, 16836384.261079147, 4.762111289237629, 52.46014800851812), ('E36', -911439.4920821647, -16012088.834107947, 24887956.73709774, 
# 0.28204130985981135, 66.45385327442628)], 'Beidou': [('C11', -7638866.7454947205, -13570670.079798257, 23229005.71544989, 5.7993445972320306, 68.29717420478599), 
# ('C12', 11704015.76304312, -20036516.415461298, 15551411.763391864, 1.4407272082607645, 48.30469982292896), ('C21', 8257932.972055634, -22228366.57812545, 14706661.785025703, 
# 1.583510838733823, 56.53917084690851), ('C34', 905851.9187320314, -18847057.221110407, 20555343.10500046, 0.833416865669841, 71.83376298689822), 
# ('C42', -3143596.5973125645, -27668165.233277563, -1485954.350407377, 2.8611719786683367, 48.2442890383957), ('C43', -15399747.247792661, -8051532.527943917, 21820406.652323417, 
# 5.232188818642709, 52.96643609059336), ('C50', 3034829.1704819365, -26718935.43273646, 7462821.069521663, 2.291342198268592, 58.2447479187001)], 'PDOP': 3.7251651434231348}, 




# # #TRD
# startpunkt = 270353.68,7040091.61 
# sluttpunkt = 270386.58,7039786.7

# #Lærdal
# startpunkt = 49379.22356892761,6773638.5790781425
# sluttpunkt = 87964.31359693682,6767233.745804535

# Day = 22
# year = 2025
# OBS_TIME = "033000"


# active_GNSS = {
#     "GPS": False,
#     "Galileo": True,
#     "Beidou": True
# }

# hey = main(startpunkt, sluttpunkt, Day, year, OBS_TIME, 10, active_GNSS )


