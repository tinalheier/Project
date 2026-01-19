import numpy as np
from Backend.geocentric_to_LG import azimuth_and_zenith

def unpack_results(results):
    satellites = [r[0] for r in results]
    azimuth = [r[1] for r in results]
    zenith = [r[2] for r in results]
    return satellites, azimuth, zenith

def compute_skyplot_data(textfile, date, observation_time, receiverCartesianPos,maskElevation):

    results_GPS, results_Galileo, results_Beidou = azimuth_and_zenith(
        textfile, date, observation_time, receiverCartesianPos, maskElevation
    )

    sat_GPS, azimuth_GPS, zenith_GPS = unpack_results(results_GPS)
    sat_Galileo, azimuth_Galileo, zenith_Galileo = unpack_results(results_Galileo)
    sat_Beidou, azimuth_Beidou, zenith_Beidou = unpack_results(results_Beidou)

    az_GPS_deg = np.degrees(azimuth_GPS).tolist()
    az_Galileo_deg = np.degrees(azimuth_Galileo).tolist()
    az_Beidou_deg = np.degrees(azimuth_Beidou).tolist()

    zen_GPS = zenith_GPS
    zen_Galileo = zenith_Galileo
    zen_Beidou = zenith_Beidou

    dateString = date[0:4] + "-" + date[4:6] + "-" + date[6:8]
    clockString = observation_time[0:2] + ":" + observation_time[2:4] + ":" + observation_time[4:6]

    data = {
        "date": dateString,
        "time": clockString,
        "maskElevation": maskElevation,
        "GPS": {
            "sat": sat_GPS,
            "az_deg": az_GPS_deg,
            "zenith": zen_GPS,
        },
        "Galileo": {
            "sat": sat_Galileo,
            "az_deg": az_Galileo_deg,
            "zenith": zen_Galileo,
        },
        "Beidou": {
            "sat": sat_Beidou,
            "az_deg": az_Beidou_deg,
            "zenith": zen_Beidou,
        },
    }

    return data
