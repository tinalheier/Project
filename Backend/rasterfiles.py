import os
import rasterio
from rasterio.merge import merge
from shapely.geometry import LineString, box


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)

DTM_FOLDER = os.path.join(PROJECT_ROOT, "data", "DTM_nasjonal")


def combine_tifs(startPoint, endPoint, folder_path=DTM_FOLDER, buffer=10000):

    tif_files = [
        os.path.join(folder_path, f)
        for f in os.listdir(folder_path)
        if f.endswith(".tif")
    ]

    line = LineString([startPoint, endPoint])
    buffer_geo = line.buffer(buffer)

    rasters = []

    for raster in tif_files:
        src = rasterio.open(raster)
        boundingbox = box(*src.bounds)

        if boundingbox.intersects(buffer_geo):
            rasters.append(src)
        else:
            src.close()

    if not rasters:
        raise ValueError("No overlap")

    mosaic, transform = merge(rasters)

    meta = rasters[0].meta.copy()
    meta.update({
        "height": mosaic.shape[1],
        "width": mosaic.shape[2],
        "transform": transform
    })

    out_path = os.path.join(PROJECT_ROOT, "data", "merged", "merged_raster.tif")

    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    with rasterio.open(out_path, "w", **meta) as dst:
        dst.write(mosaic)

    for r in rasters:
        r.close()

    print("Ny raster lagret:", out_path)

    return out_path