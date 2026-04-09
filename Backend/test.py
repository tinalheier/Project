import numpy as np
import matplotlib.pyplot as plt
from pyproj import Transformer

from skyplot_backend import compute_skyplot_data, compute_skyplot_terrain
from sat_with_terrain import find_available_sats
from rasterfiles import combine_tifs
from terrain import max_azimuth

# UTM33 -> ECEF
utm_to_ecef = Transformer.from_crs("EPSG:25833", "EPSG:4978", always_xy=True)

def plot_two_skyplots(normal_data, terrain_data):
    fig = plt.figure(figsize=(12, 6))

    def setup_ax(ax, title):
        ax.set_theta_zero_location("N")
        ax.set_theta_direction(-1)
        ax.set_ylim(0, 90)
        ax.set_yticks([0, 30, 60, 90])
        ax.set_yticklabels(["90°", "60°", "30°", "0°"])
        ax.set_title(title)

    def plot_system(ax, system_data, label, color):
        if not system_data or len(system_data["az_deg"]) == 0:
            return
        az = np.radians(system_data["az_deg"])
        elev = np.array(system_data["elev"])
        r = elev
        ax.scatter(az, r, label=label, color=color)
        for i, sat in enumerate(system_data["sat"]):
            ax.text(az[i], r[i], sat, fontsize=7)

    # Vanlig skyplot
    ax1 = plt.subplot(121, polar=True)
    setup_ax(ax1, "Skyplot uten terrain")
    plot_system(ax1, normal_data["GPS"], "GPS", "blue")
    plot_system(ax1, normal_data["Galileo"], "Galileo", "green")
    plot_system(ax1, normal_data["Beidou"], "BeiDou", "orange")
    plot_system(ax1, normal_data["Glonass"], "GLONASS", "red")
    ax1.legend(loc="upper right")

    # Skyplot med terrain
    ax2 = plt.subplot(122, polar=True)
    setup_ax(ax2, "Skyplot med terrain")
    plot_system(ax2, terrain_data["GPS"], "GPS", "blue")
    plot_system(ax2, terrain_data["Galileo"], "Galileo", "green")
    plot_system(ax2, terrain_data["Beidou"], "BeiDou", "orange")
    plot_system(ax2, terrain_data["Glonass"], "GLONASS", "red")

    # terrain-mask
    max_elev = terrain_data.get("max_elevation", {})
    if max_elev:
        az = np.array(list(max_elev.keys()))
        elev = np.array(list(max_elev.values()))
        az_closed = np.radians(np.append(az, az[0]))
        elev_closed = np.append(elev, elev[0])
        ax2.plot(az_closed, elev_closed, color="red", linewidth=2, label="Terrain mask")

    ax2.legend(loc="upper right")
    plt.tight_layout()
    plt.show()


# -------- TEST FOR SAMME STED --------

# Samme sted i UTM33
east = 142384.43704
north = 6928715.24470
height = 308
day = "115"
year = "2025"
obs_time = "100000"
mask = 0

# 1) Konverter til ECEF for vanlig skyplot
x_ecef, y_ecef, z_ecef = utm_to_ecef.transform(east, north, height)
receiver_ecef = [x_ecef, y_ecef, z_ecef]

normal_data = compute_skyplot_data(day, year, obs_time, receiver_ecef, mask)

# 2) Lag terrain-data for akkurat samme punkt
# Her bruker vi samme punkt som start og slutt for å tvinge ett sted
merged_tif = combine_tifs((east, north), (east, north), folder_path="data/DTM_nasjonal/", buffer=10000)

max_elev_dict = find_max_elev_horizon_360(
    merged_tif,
    (east, north),
    (east, north),
    1,       # ett punkt
    1,       # azimuth step
    10000,   # buffer
    5        # sampling step
)

available = find_available_sats(day, year, obs_time, mask, max_elev_dict)

# Hent første/ eneste punkt
point_key = next(iter(available))
terrain_data = compute_skyplot_terrain(
    available[point_key],
    obs_time,
    day,
    year,
    mask,
    {"GPS": True, "Galileo": True, "Beidou": True, "Glonass": True}
)

plot_two_skyplots(normal_data, terrain_data)

print(plot_two_skyplots)