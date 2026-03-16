from position_WGS84 import find_satellites, find_satellites_GLONASS
from emphererides_file import read_rinex_file
from pyproj import Transformer
import numpy as np
import os
import pandas as pd
from emphererides_file import get_ephemerides, load_ephemerides


a = 6378137 
b = 6356752.3141
e_2nd = (a**2-b**2)/a**2

ecef_to_llh = Transformer.from_crs("EPSG:4978", "EPSG:4326",always_xy=True)


def azimuth_and_zenith(day, year,  observation_time, receiverCartesianPos, maskElevation, empheridesfile_GPS, empheridesfile_Galileo,
    empheridesfile_Beidou, empheridesfile_Glonass):
    
    results_GPS = []
    results_Galileo = []
    results_Beidou = []
    results_Glonass = []

    maskElevationZenith = 90 - maskElevation

    satellites_GPS = find_satellites(empheridesfile_GPS, day, year, observation_time)
    satellites_Galileo = find_satellites(empheridesfile_Galileo, day, year, observation_time)
    satellites_Beidou = find_satellites(empheridesfile_Beidou, day, year, observation_time)
    satellites_Glonass = find_satellites_GLONASS(empheridesfile_Glonass, day, year, observation_time)


    lat,long,h = ecef_to_llh.transform(receiverCartesianPos[0], receiverCartesianPos[1], receiverCartesianPos[2])
    latlong_receiver = (lat,long,h)

    for index, row in satellites_GPS.iterrows():

        sat_pos = row["satellitePosition"]
        distance_sat_receiver = baseline(sat_pos, receiverCartesianPos)
        LG = local_coordinates(distance_sat_receiver, latlong_receiver)
        zenith = float(zentih_angle(LG)* 180/np.pi) #degree
            
        
        if zenith <= 90 and zenith <= maskElevationZenith:
            x,y,z  = sat_pos
            satname = row["sat"]
            bearing = float(bearing_LG(LG) * 180/np.pi)
            results_GPS.append((satname, x,y,z, bearing, zenith))

    
    for index, row in satellites_Galileo.iterrows():

        sat_pos = row["satellitePosition"]
        distance_sat_receiver = baseline(sat_pos, receiverCartesianPos)
        LG = local_coordinates(distance_sat_receiver, latlong_receiver)

            
        zenith = float(zentih_angle(LG)* 180/np.pi)

        if zenith <= 90 and zenith <= maskElevationZenith:
            x,y,z  = sat_pos
            satname = row["sat"]
            bearing = float(bearing_LG(LG)* 180/np.pi)
            results_Galileo.append((satname, x,y,z, bearing, zenith))    
        

    for index, row in satellites_Beidou.iterrows():

        sat_pos = row["satellitePosition"]


        distance_sat_receiver = baseline(sat_pos, receiverCartesianPos)
        LG = local_coordinates(distance_sat_receiver, latlong_receiver)

            
        zenith = float(zentih_angle(LG)* 180/np.pi)

        if zenith <= 90 and zenith <= maskElevationZenith:
            x,y,z  = sat_pos
            satname = row["sat"]
            bearing = float(bearing_LG(LG)* 180/np.pi) #rad
            results_Beidou.append((satname,x,y,z,  bearing, zenith))   


    for index, row in satellites_Glonass.iterrows():

        sat_pos = row["satellitePosition"]


        distance_sat_receiver = baseline(sat_pos, receiverCartesianPos)
        LG = local_coordinates(distance_sat_receiver, latlong_receiver)

            
        zenith = float(zentih_angle(LG)* 180/np.pi)

        if zenith <= 90 and zenith <= maskElevationZenith:
            x,y,z  = sat_pos
            satname = row["sat"]
            bearing = float(bearing_LG(LG)* 180/np.pi) #rad
            results_Glonass.append((satname,x,y,z,  bearing, zenith))   
    


    return results_GPS, results_Galileo, results_Beidou, results_Glonass



def baseline(satellite_coord, receiver_coord):
    baseline = satellite_coord - receiver_coord
    return baseline


def T_matrix(latitude, longitude):
    long = longitude 
    lat = latitude
    x = np.array([[-np.sin(lat)*np.cos(long),   -np.sin(lat)*np.sin(long),    np.cos(lat)],
                  [-np.sin(long),                np.cos(long),                0],
                  [np.cos(lat)*np.cos(long),     np.cos(lat)*np.sin(long),    np.sin(lat)]])
    return x

def local_coordinates(baseline, lat_long):
    latitude, longitude = lat_long[0], lat_long[1]
    matrix = T_matrix(latitude, longitude)
    return np.dot(matrix, baseline)

def bearing_LG(local_coordinates):
    N, E = local_coordinates[0], local_coordinates[1]  
                                
    bearing = np.arctan2(E, N)  

    if bearing < 0:
        bearing += (2*np.pi)

    return bearing 

def distance_LG(local_coordinates):
    N, E, Z = local_coordinates[0], local_coordinates[1], local_coordinates[2]
    distance = np.sqrt(N**2 + E**2 + Z**2)
    return distance

def zentih_angle(local_coordinates):
    N, E, Z = local_coordinates[0], local_coordinates[1], local_coordinates[2]
    slope_distance = np.sqrt(E**2 + N**2 + Z**2)
    return np.arccos(Z/slope_distance)  #in rad


def dataframeExists(day, year, base_path):

    if not os.path.isdir(base_path):
        return False
    
    files = os.listdir(base_path)
    if len(files) == 0:
        return False
    
    return True


# DAY = 35
# yEAR = 2025

# OBS_TIME = "033000"
# RECEIVER_COORD = np.array([3146294.9, 595984.2, 5491077.6])

# MASK_ELEVATION = 45

# print(azimuth_and_zenith(DAY, yEAR, OBS_TIME, RECEIVER_COORD, MASK_ELEVATION))
