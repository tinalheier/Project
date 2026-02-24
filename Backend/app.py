from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import numpy as np
from pyproj import Transformer
from skyplot_backend import compute_skyplot_data
from roads import hent_veglenkesekvenser_rute

app = Flask(__name__)

#fra UTM33 til Lat/lon
tf = Transformer.from_crs("EPSG:25833", "EPSG:4326", always_xy=True)
CORS(app)


TEXTFILE = "BRDC00IGS_R_20251260000_01D_MN.rnx" #Endre denne hvis filvei endres
DATE = "20250506"
OBS_TIME = "033000"
RECEIVER_COORD = np.array([3146294.9, 595984.2, 5491077.6])
MASK_ELEVATION = 45

#Inputs for the different observation locations in Specialization thesis
#np.array([2816111.074, 515693.221, 5680574.092]) TRD
#np.array([3146294.9, 595984.2, 5491077.6]) Oslo

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
    
    
@app.route("/api/GNSS-test")
def test():
    return jsonify({"msg": "He hei"})

if __name__ == "__main__":
    app.run(debug=True)