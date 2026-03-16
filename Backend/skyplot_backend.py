import numpy as np
from geocentric_to_LG import azimuth_and_zenith
from sat_with_terrain import find_max_elev_horizon_360, dataframeExists
from emphererides_file import get_ephemerides, load_ephemerides
import os

def unpack_results(results):
    satellites = [r[0] for r in results]
    azimuth = [r[4] for r in results]
    zenith = [r[5] for r in results]
    return satellites, azimuth, zenith


def compute_skyplot_data(day, year, observation_time, receiverCartesianPos,maskElevation):
    day = str(day).zfill(3)
    base_path = os.path.join("data", "dataFrames", str(year), day)

    if not dataframeExists(day, year, base_path):
        get_ephemerides(day, year)
    

    GPS, Galileo, Beidou, Glonass = load_ephemerides(day, year, base_path) 

    results_GPS, results_Galileo, results_Beidou, results_Glonass = azimuth_and_zenith(day, year,  observation_time, receiverCartesianPos, maskElevation, GPS, Galileo,
    Beidou, Glonass
    )


    sat_GPS, az_GPS_deg, zenith_GPS = unpack_results(results_GPS)
    sat_Galileo, az_Galileo_deg, zenith_Galileo = unpack_results(results_Galileo)
    sat_Beidou, az_Beidou_deg, zenith_Beidou = unpack_results(results_Beidou)
    sat_Glonass, az_Glonass_deg, zenith_Glonass = unpack_results(results_Glonass)


    zen_GPS = zenith_GPS
    zen_Galileo = zenith_Galileo
    zen_Beidou = zenith_Beidou
    zen_Glonass = zenith_Glonass

    dateString = day + year
    clockString = observation_time[0:2] + ":" + observation_time[2:4] + ":" + observation_time[4:6]

    data = {
        "date": dateString,
        "time": clockString,
        "maskElevation": maskElevation,
        "GPS": {
            "sat": sat_GPS,
            "az_deg": az_GPS_deg,
            "elev": zen_GPS,
        },
        "Galileo": {
            "sat": sat_Galileo,
            "az_deg": az_Galileo_deg,
            "elev": zen_Galileo,
        },
        "Beidou": {
            "sat": sat_Beidou,
            "az_deg": az_Beidou_deg,
            "elev": zen_Beidou,
        },
         "Glonass": {
            "sat": sat_Glonass,
            "az_deg": az_Glonass_deg,
            "elev": zen_Glonass,
        },
    }

    return data
