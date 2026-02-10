from roads import dele_veilinje
from terrain import horizon_mask_360
import rasterio
from pyproj import Transformer
import numpy as np
from geocentric_to_LG import azimuth_and_zenith 
from geocentric_to_LG import read_rinex_file

# horizon_mask_360(pointA, az_step, buffer, step) #Lat og long
# dele_veilinje(startpunkt, sluttpunkt, step): #UTM33

src = rasterio.open('Backend/data/DTM_trd.tif')

tf = Transformer.from_crs("EPSG:25833", "EPSG:4978", always_xy=True)

def find_available_sats(textfile, date, observation_time, maskElevation, max_elev_and_coord):
    empherids = read_rinex_file(textfile)
    
    available_sats_point = {}

    for punkt, horizon in max_elev_and_coord.items():
        GPS_updated = []
        Galileo_updated = []
        Beidou_updated= []
#print(punkt) (2815050.0861411192, 516548.4438278879, 5680854.373259013)   print(punkt[0])) 2815050.0861411192  print(punkt[1])) 516548.4438278879      print(punkt[2])) 5680854.373259013
#dette er horszon {0: -0.038151461429198966, 40: 4.011171678047463      print(horizon[40]) =  4.011171678047463), hente ut på nøkkel 40 grader

        GPS, Galileo, Beidou = azimuth_and_zenith(empherids, date, observation_time, punkt, maskElevation)
        
        for satname, az, zen in GPS:
            sat_elev = 90 - zen
            nearest_az = min(horizon.keys(), key=lambda a: abs(a - az + 180) % 360 - 180)
            terrain_elev = horizon[nearest_az]
            if sat_elev > terrain_elev:
                GPS_updated.append((satname, az, sat_elev))

        for satname, az, zen in Galileo:
            sat_elev = 90 - zen
            nearest_az = min(horizon.keys(), key=lambda a: abs(a - az))
            terrain_elev = horizon[nearest_az]
            if sat_elev > terrain_elev:
                Galileo_updated.append((satname, az, sat_elev))

        for satname, az, zen in Beidou:
            sat_elev = 90 - zen
            nearest_az = min(horizon.keys(), key=lambda a: abs(a - az))
            terrain_elev = horizon[nearest_az]
            if sat_elev > terrain_elev:
                Beidou_updated.append((satname, az, sat_elev))
        
        available_sats_point[punkt] = {
        "GPS": GPS_updated,
        "Galileo": Galileo_updated,
        "Beidou": Beidou_updated
    }
        
    return available_sats_point


        #([('G12', 3.9511136762660115, 35.392171240412786), ('G19', 1.349619531086164, 44.93939691124398), ('G24', 2.7734455113102525, 22.531116155567737)], 
        #[('E06', 3.713740151577025, 40.06245818595466), ('E09', 4.453883494827758, 34.0692673612388), ('E23', 1.5622957176424461, 23.168650391117858), 
        #('E31', 3.92835963031295, 37.07222947465102)], [('C24', 1.733236444993666, 44.342020469368585), ('C25', 4.326904477875038, 17.61584152392023)])
            

#finne max vinkel for alle azimuth på hele delstrekningen
#startpunkt og sluttpunkt er der man trykker i kartet, step_vei er veien stykket opp, step azimuth er step mellom 0-360
#buffer azimtuh er hvor langt den søker totalt, og step utover buffer er når den søker ut til buffer på en azimtuh
def find_max_elev_horizon_360(startpunkt, sluttpunkt, step_vei, step_azimuth, buffer_azimuth, step_utover_buffer):
    
    all_points_along_road = dele_veilinje(startpunkt, sluttpunkt, step_vei)
    elevation_along_road_360 = {}

    for point in all_points_along_road:

        point_ECEF = tf.transform(point[0], point[1], point[2])
        max_elevation = horizon_mask_360(src, point, step_azimuth, buffer_azimuth, step_utover_buffer)
        elevation_along_road_360[point_ECEF] = max_elevation

    return elevation_along_road_360

    src.close()

#TRD
startpunkt = 270353.68,7040091.61 
sluttpunkt = 270386.58,7039786.7
    


sjekk = find_max_elev_horizon_360(startpunkt, sluttpunkt, 10, 40, 10000, 10)
TEXTFILE = "BRDC00IGS_R_20251260000_01D_MN.rnx" #Endre denne hvis filvei endres
DATE = "20250506"
OBS_TIME = "033000"
RECEIVER_COORD = np.array([3146294.9, 595984.2, 5491077.6])

print(find_available_sats(TEXTFILE, DATE, OBS_TIME, 45, sjekk))

