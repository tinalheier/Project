from Backend.position_WGS84 import find_satellites
from Backend.emphererides_file import read_rinex_file

import numpy as np

a = 6378137 
b = 6356752.3141
e_2nd = (a**2-b**2)/a**2



def azimuth_and_zenith(textfile, date, observation_time, receiverCartesianPos, maskElevation):
    
    results_GPS = []
    results_Galileo = []
    results_Beidou = []

    maskElevationZenith = 90 - maskElevation


    empherids = read_rinex_file(textfile)
    empheridesfile_GPS,  empheridesfile_Galileo, empheridesfile_Beidou = empherids[0], empherids[1], empherids[2]
    

    satellites_GPS = find_satellites(empheridesfile_GPS, date, observation_time)
    satellites_Galileo = find_satellites(empheridesfile_Galileo, date, observation_time)
    satellites_Beidou = find_satellites(empheridesfile_Beidou, date, observation_time)

    for index, row in satellites_GPS.iterrows():

        sat_pos = row["satellitePosition"]
        distance_sat_receiver = baseline(sat_pos, receiverCartesianPos)
        latlong_receiver = xyz_to_latlong_receiver(receiverCartesianPos)
        LG = local_coordinates(distance_sat_receiver, latlong_receiver)
        zenith = float(zentih_angle(LG)* 180/np.pi) #degree
        
    
        if zenith <= 90 and zenith <= maskElevationZenith:
            satname = row["sat"]
            bearing = float(bearing_LG(LG))
            results_GPS.append((satname, bearing, zenith))

   
    for index, row in satellites_Galileo.iterrows():

        sat_pos = row["satellitePosition"]


        distance_sat_receiver = baseline(sat_pos, receiverCartesianPos)

        latlong_receiver = xyz_to_latlong_receiver(receiverCartesianPos)

        LG = local_coordinates(distance_sat_receiver, latlong_receiver)

        
        zenith = float(zentih_angle(LG)* 180/np.pi)

        if zenith <= 90 and zenith <= maskElevationZenith:
            satname = row["sat"]
            bearing = float(bearing_LG(LG))
            results_Galileo.append((satname, bearing, zenith))    
    

    for index, row in satellites_Beidou.iterrows():

        sat_pos = row["satellitePosition"]


        distance_sat_receiver = baseline(sat_pos, receiverCartesianPos)

        latlong_receiver = xyz_to_latlong_receiver(receiverCartesianPos)

        LG = local_coordinates(distance_sat_receiver, latlong_receiver)

        
        zenith = float(zentih_angle(LG)* 180/np.pi)

        if zenith <= 90 and zenith <= maskElevationZenith:
            satname = row["sat"]
            bearing = float(bearing_LG(LG)) #rad
            results_Beidou.append((satname, bearing, zenith))   

    return results_GPS, results_Galileo, results_Beidou



def baseline(satellite_coord, receiver_coord):
    baseline = satellite_coord - receiver_coord
    return baseline


def xyz_to_latlong_receiver(receiver_coord):
    p = np.sqrt(receiver_coord[0]**2 + receiver_coord[1]**2)

    phi_0 = np.arctan(receiver_coord[2]/(p*(1-e_2nd)))

    N_0 = a**2/np.sqrt(a**2*np.cos(phi_0)**2 + (b**2*np.sin(phi_0)**2))

    h = (p / np.cos(phi_0)) - N_0

    phi_improved = np.arctan(receiver_coord[2] / (p *(1-(e_2nd*(N_0/(N_0+h)))))) 

    longitude = np.arctan(receiver_coord[1]/receiver_coord[0])

    if phi_0 == phi_improved:
        return float(phi_improved), float(longitude)
    
    else: return inverse_transformation_step(phi_improved, p, receiver_coord)


#Helper function to xyz_to_latlong_receiver, iteration
def inverse_transformation_step(phi_improved, p, receiver_coord):
    ReceiverX, ReceiverY, ReceiverZ = receiver_coord
    phi_0 = phi_improved
    N_0 = a**2/np.sqrt(a**2*np.cos(phi_0)**2 + (b**2*np.sin(phi_0)**2))
    h = (p/np.cos(phi_0)) - N_0

    phi_improved = np.arctan(ReceiverZ / (p *(1-(e_2nd*(N_0/(N_0+h))))))
    
    longitude = np.arctan(ReceiverY/ReceiverX)
    if phi_0 == phi_improved:
        
        return float(phi_improved), float(longitude)
    
    else: return inverse_transformation_step(phi_improved, p, receiver_coord)
    

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




