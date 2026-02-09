from roads import dele_veilinje
from terrain import horizon_mask_360
import rasterio

# horizon_mask_360(pointA, az_step, buffer, step) #Lat og long
# dele_veilinje(startpunkt, sluttpunkt, step): #UTM33

DTM_trd = rasterio.open('Backend/data/DTM_trd.tif')
#DSM_trd= rasterio.open('Backend/data/DSM_trd.tif')



#finne max vinkel for alle azimuth på hele delstrekningen
#startpunkt og sluttpunkt er der man trykker i kartet, step_vei er veien stykket opp, step azimuth er step mellom 0-360
#buffer azimtuh er hvor langt den søker totalt, og step utover buffer er når den søker ut til buffer på en azimtuh
def midlertidig_navn(startpunkt, sluttpunkt, step_vei, step_azimuth, buffer_azimuth, step_utover_buffer):
    
    all_points_along_road = dele_veilinje(startpunkt, sluttpunkt, step_vei)

    print(len(all_points_along_road))
    for point in all_points_along_road:

        max_elevation = horizon_mask_360(point, step_azimuth, buffer_azimuth, step_utover_buffer)
  



DTM_trd.close()

# startpunkt = 270239.58,7040945.2 #samf
# sluttpunkt = 270226.82,7041348.34


startpunkt = 270353.68,7040091.61 
sluttpunkt = 270386.58,7039786.7

sjekk = midlertidig_navn(startpunkt, sluttpunkt, 10, 6, 10000, 10)