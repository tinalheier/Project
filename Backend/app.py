from flask import Flask, render_template, jsonify
from flask_cors import CORS
import numpy as np

from skyplot_backend import compute_skyplot_data

app = Flask(__name__)
CORS(app)

TEXTFILE = "BRDC00IGS_R_20251260000_01D_MN.rnx" #Endre denne hvis filvei endres
DATE = "20250506"
OBS_TIME = "033000"
RECEIVER_COORD = np.array([3146294.9, 595984.2, 5491077.6])
MASK_ELEVATION = 45

#Inputs for the different observation locations in Specialization thesis
#np.array([2816111.074, 515693.221, 5680574.092]) TRD
#np.array([3146294.9, 595984.2, 5491077.6]) Oslo

@app.route("/api/GNSS-test")
def test():
    return jsonify({"msg": "He hei"})

app.run(debug=True)
@app.route("/skyplot-data")
def skyplot_data():
    data = compute_skyplot_data(TEXTFILE, DATE, OBS_TIME, RECEIVER_COORD, MASK_ELEVATION)
    return jsonify(data)

if __name__ == "__main__":
    app.run(debug=True)