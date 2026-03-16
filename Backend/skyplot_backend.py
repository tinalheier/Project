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


def compute_skyplot_terrain(data_dict, observation_time, day, year, maskElevation):
    day = str(day).zfill(3)

    def unpack(system_list):

        sat = []
        az = []
        elev = []

        for satname, x, y, z, bearing, zenith in system_list:
            sat.append(satname)
            az.append(bearing)
            elev.append(zenith)

        return sat, az, elev


    GPS = data_dict.get("GPS", [])
    Galileo = data_dict.get("Galileo", [])
    Beidou = data_dict.get("Beidou", [])
    Glonass = data_dict.get("Glonass", [])

    sat_GPS, az_GPS, elev_GPS = unpack(GPS)
    sat_Gal, az_Gal, elev_Gal = unpack(Galileo)
    sat_Bei, az_Bei, elev_Bei = unpack(Beidou)
    sat_Glo, az_Glo, elev_Glo = unpack(Glonass)

   
    dateString = day + str(year)
    clockString = observation_time[0:2] + ":" + observation_time[2:4] + ":" + observation_time[4:6]


    skyplot_data = {
        "date": dateString,
        "time": clockString,
        "maskElevation": maskElevation,
    

        "GPS": {
            "sat": sat_GPS,
            "az_deg": az_GPS,
            "elev": elev_GPS,
        },

        "Galileo": {
            "sat": sat_Gal,
            "az_deg": az_Gal,
            "elev": elev_Gal,
        },

        "Beidou": {
            "sat": sat_Bei,
            "az_deg": az_Bei,
            "elev": elev_Bei,
        },

        "Glonass": {
            "sat": sat_Glo,
            "az_deg": az_Glo,
            "elev": elev_Glo,
        },
         "source": "terrain_skyplot"
    }

    return skyplot_data



def compute_skyplot_data(day, year, observation_time, receiverCartesianPos,maskElevation):
    day = str(day).zfill(3)
    base_path = os.path.join("data", "dataFrames", str(year), day)

    if not dataframeExists(day, year, base_path):
        get_ephemerides(day, year)
    

    GPS, Galileo, Beidou, Glonass = load_ephemerides(day, year, base_path) 

    results_GPS, results_Galileo, results_Beidou, results_Glonass = azimuth_and_zenith(day, year,  observation_time, receiverCartesianPos, maskElevation, GPS, Galileo,
    Beidou, Glonass
    )

    #results_GPS = [('G01', -16349750.919138134, -14537816.186284404, -15115440.857930157, 192.94154267394674, 15.467724024968293), ('G02', -6040540.482308791, -14865435.387159284, -20862670.00185245, 283.19057400181447, 14.717951932523235), ('G03', -12328197.618357176, -22988278.61345311, 5116923.910616838, 208.20112128019198, 57.7461746838801), ('G07', -25670098.37193479, -6741161.574092577, 4164892.1233742917, 156.15937011548252, 54.96346529299631), ('G08', 1604924.6644637925, -21464950.928336617, -15428100.962973272, 273.31514156748324, 35.37693696845735), ('G10', 13749557.261711435, -4320897.554473264, -22046549.217947725, 334.288432081216, 50.34352200147774), ('G13', -10710952.173712404, 21143174.356385306, -11982423.590317009, 67.7226304937739, 61.472861034681294), ('G14', -15933594.474456945, 1354560.6270362756, -21155096.730127145, 76.62127430059829, 20.36306201389666), ('G15', 1464009.9290616405, 21555477.422627885, -15956827.319429504, 41.14224972681057, 66.75359162075857), ('G17', -20933061.203149866, 10292345.842834631, -12571655.684650129, 94.17127567179895, 42.66552279428768), ('G19', -20360425.270067886, 15832057.72715272, -5117766.106513303, 96.31135479334658, 59.753728342863454), ('G20', -7616650.942768391, 22904782.328234434, -11084684.319547359, 62.833231168154235, 66.83401065202388), ('G22', -13080050.785949197, 8438870.91600292, -21224861.537641864, 62.909774798449234, 32.45409706485432), ('G23', 16988156.806558605, 9917654.06780416, -17899261.119627133, 359.9434660165201, 70.14552563156617), ('G24', 11098930.857393935, 14896601.563561732, -19642409.95160059, 15.530848870263455, 65.56744916305327), ('G27', 10919392.818811495, -22906489.66140759, -7384305.232621892, 275.3012222545154, 59.303551190411305), ('G30', -25729217.86047373, 1514169.3822243593, -6773252.675983159, 126.09610647837742, 41.38854088631797), ('G32', 19856033.851195462, -13792232.36489638, -10507633.80390061, 303.8094742089951, 69.0568916533493)]


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
