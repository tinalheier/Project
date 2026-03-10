from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import numpy as np
from pyproj import Transformer
from skyplot_backend import compute_skyplot_data
from roads import hent_veglenkesekvenser_rute, dele_veilinje
from datetime import datetime
from sat_with_terrain import main
from DOPcalculation import DOPChart

app = Flask(__name__)


#fra UTM33 til Lat/lon
tf = Transformer.from_crs("EPSG:25833", "EPSG:4326", always_xy=True)
ecef_to_latlon = Transformer.from_crs("EPSG:4978", "EPSG:4326", always_xy=True)
CORS(app)


# TEXTFILE = "BRDC00IGS_R_20251260000_01D_MN.rnx" #Endre denne hvis filvei endres
# DATE = "20250506"
# OBS_TIME = "033000"
# RECEIVER_COORD = np.array([3146294.9, 595984.2, 5491077.6])
# MASK_ELEVATION = 45

@app.get("/api/route")
def route():
    try:
        start_e = float(request.args["start_e"])
        start_n = float(request.args["start_n"])
        end_e = float(request.args["end_e"])
        end_n = float(request.args["end_n"])

        merged_road = hent_veglenkesekvenser_rute(
            (start_e, start_n),
            (end_e, end_n)
        )

        if merged_road is None:
            return jsonify({"error": "No route found"}), 400

        coords = []

        # håndter MultiLineString og LineString
        if merged_road.geom_type == "MultiLineString":
            lines = merged_road.geoms
        else:
            lines = [merged_road]

        for line in lines:
            for pt in line.coords:
                x = pt[0]
                y = pt[1]

                lon, lat = tf.transform(x, y)
                coords.append([lon, lat])

        if not coords:
            return jsonify({"error": "Empty geometry"}), 400

        return jsonify({
            "type": "Feature",
            "geometry": {
                "type": "LineString",
                "coordinates": coords
            }
        })
    
    

    except Exception as e:
        print("ROUTE ERROR:", e)
        return jsonify({"error": str(e)}), 500
    

@app.get("/api/dop")
def dop():
    try:
        start_e = float(request.args["start_e"])
        start_n = float(request.args["start_n"])
        end_e = float(request.args["end_e"])
        end_n = float(request.args["end_n"])

        date = request.args.get("date")
        gps = request.args.get("gps") == "true"
        galileo = request.args.get("galileo") == "true"
        beidou = request.args.get("beidou") == "true"
        mask = float(request.args.get("mask", 10))

        active_GNSS = {
            "GPS": gps,
            "Galileo": galileo,
            "Beidou": beidou
        }


        if date:
            dt = datetime.fromisoformat(date)
            DATE = dt.strftime("%Y%m%d")
            OBS_TIME = dt.strftime("%H%M%S")

            d = datetime.strptime(DATE, "%Y%m%d")
            year = DATE[0:4]
            julian = d.timetuple().tm_yday

            print(year)
            print("Julian:", julian)
            print("OBS_TIME:", OBS_TIME)
    

    
        dop_dict = main((start_e, start_n), (end_e, end_n), julian, year, OBS_TIME, mask, active_GNSS)
        chart = DOPChart(dop_dict)
        features = []

        for coord, data in dop_dict.items():

            if "PDOP" not in data:
                pdop = 0
            
            else:
                pdop = data["PDOP"]

            x, y, z = coord
            lon, lat, _ = ecef_to_latlon.transform(x, y, z)

            features.append({
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [lon, lat]
                },
                "properties": {
                    "pdop": float(pdop)
                }
            })

        print("ferdig")
        return jsonify({
            "type": "FeatureCollection",
            "features": features,
            "chart": chart})

            
    except Exception as e:
        print("DOP ERROR:", e)
        return jsonify({"error": str(e)}), 500

@app.get("/api/skyplot")
def skyplot():

    lon = float(request.args["lon"])
    lat = float(request.args["lat"])
    date = request.args["date"]
    mask = float(request.args.get("mask", 10))

    dt = datetime.fromisoformat(date)

    DATE = dt.strftime("%Y%m%d")
    OBS_TIME = dt.strftime("%H%M%S")

    d = datetime.strptime(DATE, "%Y%m%d")
    year = DATE[0:4]
    julian = d.timetuple().tm_yday


    transformer = Transformer.from_crs("EPSG:4326","EPSG:4978", always_xy=True)

    x,y,z = transformer.transform(lon, lat, 0)

    data = compute_skyplot_data(
        julian, year, OBS_TIME, np.array([x,y,z]),mask
    )

    return jsonify(data)

if __name__ == "__main__":
    app.run(debug=True)