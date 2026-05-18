from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import numpy as np
from pyproj import Transformer
from skyplot_backend import compute_skyplot_terrain
from roads import hent_veglenkesekvenser_rute, dele_veilinje
from datetime import datetime
from sat_with_terrain import main
from DOPcalculation import DOPChart

app = Flask(__name__)


#fra UTM33 til Lat/lon
tf = Transformer.from_crs("EPSG:25833", "EPSG:4326", always_xy=True)
ecef_to_latlon = Transformer.from_crs("EPSG:4978", "EPSG:4326", always_xy=True)
CORS(app)
@app.route("/")
def home():
    return "Backend is running"



dictionary_dop_terrain = None


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
            return jsonify({"error": "Could not find route. Try to select a new start and end point"}), 400

        coords = []


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
        glonass = request.args.get("glonass") == "true"
        mask = float(request.args.get("mask", 10))

        active_GNSS = {
            "GPS": gps,
            "Galileo": galileo,
            "Beidou": beidou,
            "Glonass": glonass
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
        global dictionary_dop_terrain

        dictionary_dop_terrain = dop_dict
        chart = DOPChart(dop_dict)
        features = []

        for i, (coord, data) in enumerate(dop_dict.items()):

            if "PDOP" not in data:
                pdop = 0

            
            else:
                pdop = data["PDOP"]

            
            if "GDOP" not in data:
                gdop = 0
            
            else:
                gdop = data["GDOP"]

            x, y, z = coord
            lon, lat, _ = ecef_to_latlon.transform(x, y, z)

            features.append({
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [lon, lat]
                },
                "properties": {
                    "pdop": float(pdop),
                    "gdop": float(gdop),
                    "index": i
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


@app.get("/api/skyplot_terrain")
def skyplot_terrain():

    index = int(request.args["index"])
    date = request.args["date"]
    mask = float(request.args.get("mask",10))
    gps = request.args.get("gps") == "true"
    galileo = request.args.get("galileo") == "true"
    beidou = request.args.get("beidou") == "true"
    glonass = request.args.get("glonass") == "true"

    active_GNSS = {
            "GPS": gps,
            "Galileo": galileo,
            "Beidou": beidou,
            "Glonass": glonass
        }

    dt = datetime.fromisoformat(date)

    DATE = dt.strftime("%Y%m%d")
    OBS_TIME = dt.strftime("%H%M%S")

    d = datetime.strptime(DATE, "%Y%m%d")
    year = DATE[0:4]
    julian = d.timetuple().tm_yday


    global dictionary_dop_terrain

    if dictionary_dop_terrain is None:
        return jsonify({"error":"Run /api/dop first"}),400

    data_dict = list(dictionary_dop_terrain.values())[index]
    
    data = compute_skyplot_terrain(
        data_dict,
        OBS_TIME,
        julian,
        year,
        mask,
        active_GNSS,
    )

    return jsonify(data)


if __name__ == "__main__": 
    import os 
    port = int(os.environ.get("PORT", 5000)) 
    app.run( host="0.0.0.0", port=port, debug=True )