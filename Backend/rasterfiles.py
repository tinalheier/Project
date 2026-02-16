
import os
import rasterio
from rasterio.merge import merge
from shapely.geometry import LineString, box



def combine_tifs(startPoint, endPoint, folder_path = "/Backend/data/DTM_nasjonal/", buffer = 10000):

    #finner alle .tif filer i mappen
    tif_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith(".tif")]


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
 

    BASE_DIR = os.path.dirname(__file__)
    out_path = os.path.join(BASE_DIR, "data", "merged_raster.tif")

    os.makedirs(os.path.dirname(out_path), exist_ok=True)   

    with rasterio.open(out_path, "w", **meta) as dst:
        dst.write(mosaic)

    for r in rasters:
        r.close()

    print("Ny raster lagret:", out_path)

    return out_path

