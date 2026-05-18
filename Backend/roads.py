import requests
from shapely import wkt, union_all
from shapely.ops import linemerge
from shapely.geometry import MultiLineString
import numpy as np
from shapely.geometry import Point


# Finner veglenkesekvenser mellom gitt start og sluttpunkt

def hent_veglenkesekvenser_rute(startpunkt, sluttpunkt): #utm33 koord

    BASE = "https://nvdbapiles.atlas.vegvesen.no/vegnett/api/v4"

    HEADERS = {
        "X-Client": "tina-heier-ntnu-gnss"
    }
    url = f"{BASE}/beta/vegnett/rute"

    start = f"{startpunkt[0]},{startpunkt[1]}"
    slutt = f"{sluttpunkt[0]},{sluttpunkt[1]}"

    omkrets_verdier = [100, 500, 1000, 5000, 10000, 15000]
    
    def fetch(omkrets):
        params = {
        "start": start,
        "slutt": slutt,
        "maks_avstand": 700,
        "omkrets": omkrets,
        "konnekteringslenker": "true"
        }

        r = requests.get(url, headers=HEADERS, params=params)

        print("STATUS:", r.status_code)

        return r

    r = None

    for omkrets in omkrets_verdier:
        r = fetch(omkrets)


        status = r.json().get("metadata", {}).get("status_tekst")

        if status != "IKKE_FUNNET_RUTE":
            break
        
    print(r.url)

    data = r.json()

    #Hente posisjoner til alle segmenter og gjør de til shapely LineStrings
    lines = []

    segments = data["vegnettsrutesegmenter"]


    for seg in segments: 
        wkt_line = seg["geometri"]["wkt"]
        line = wkt.loads(wkt_line)
        lines.append(line)




    if len(lines) != 1:
        merged_road = linemerge(MultiLineString(lines))

    else:
        merged_road = lines[0]


    return merged_road


#Dele veilinjen i masse ulike deler, med step som avstand og får koord i x,y z UTM33
def dele_veilinje(startpunkt, sluttpunkt, step):
    
    veglinje = hent_veglenkesekvenser_rute(startpunkt, sluttpunkt)

    length = veglinje.length
    distances = np.arange(0, length + step, step)
    
    points = []
    for i in distances:
        p = veglinje.interpolate(i)

        try:
            x,y,z = p.coords[0]
        except ValueError:
            x, y = p.coords[0]
            z = None
    
       
        points.append((x, y, z))

    
    return points



# # # startpunkt = 270239.58,7040945.2 #samf
# # # sluttpunkt = 270356.96,7039392.78

# startpunkt = 268275.10701,7042069.63928 #tunell
# sluttpunkt = 268728.84744,7041977.67557

# # startpunkt = 237101.15574,6984448.33133 #5000 omkrets blir for lite
# # sluttpunkt = 251626.79789,6983869.25654

# rute = hent_veglenkesekvenser_rute(startpunkt, sluttpunkt)

# # print(dele_veilinje(startpunkt, sluttpunkt, 10))
