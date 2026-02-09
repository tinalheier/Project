import rasterio
import rasterio.plot 
import numpy as np
from pyproj import Transformer
from rasterio.windows import from_bounds
import math
from rasterio.transform import rowcol

DTM_trd = rasterio.open('Backend/data/DTM_trd.tif')
#DSM_trd= rasterio.open('Backend/data/DSM_trd.tif')

#Se om punktet er innenfor rasteren
def point_inside_raster(src, x, y) -> bool:
    bb = src.bounds #bounding box
    return (bb.left <= x <= bb.right) and (bb.bottom <= y <= bb.top)

#hente høydeverdien i raster til koordinat x,y og returnerer høyde om det er noe, none om det er utenfor/i nonData
def get_Height_In_Raster(src, x, y):
    if not point_inside_raster(src, x, y):
        return None
    
    z = next(src.sample([(x,y)]))[0]

    if (src.nodata is not None and z == src.nodata) or np.isnan(z):
        return None

    return float(z)


#Her ser vi får oss at vi er i et punkt, Vi snurrer rundt og "skyter" ut en stråle fra der vi er rotert.
#Deretter finner vi max azimuth der vi treffer

def max_azimuth(distances, data, transform, Ax, Ay, zA, azimuth):

    az_rad = math.radians(azimuth)

    xs = Ax + distances * math.sin(az_rad)
    ys = Ay + distances * math.cos(az_rad)

    rows, cols = rowcol(transform, xs, ys)

    rows = np.clip(rows, 0, data.shape[0]-1)
    cols = np.clip(cols, 0, data.shape[1]-1)

    zs = data[rows, cols]

    angles = np.degrees(np.arctan2(zs - zA, distances))

    return np.nanmax(angles)



def horizon_mask_360(pointA, az_step, buffer, step):

    results = []
    distances = np.arange(step, buffer + step, step)

    src = DTM_trd
    Ax, Ay, zA = pointA

    window = from_bounds(
        Ax-buffer,
        Ay-buffer,
        Ax+buffer,
        Ay+buffer,
        src.transform
    )

    data = src.read(1, window=window)
    transform = src.window_transform(window)

    for az in np.arange(0, 360, az_step):

        res = max_azimuth(distances, data, transform, Ax, Ay, zA, az)
        results.append(res)

    return results




#testing
# point_testA= [10.3817288, 63.4144650] #longitude, latitude
# point_testB= [10.3707799, 63.4176188] #longitude, latitude, nb, dette funker ikke, pga utm

# print(select_raster_in_buffer(100, point_testA,point_testB, 2))

# print(horizon_mask_360(point_testA, 4, 5000, 10))