import requests
from shapely import wkt
from shapely.ops import linemerge
from shapely.geometry import MultiLineString
import numpy as np


# Finner veglenkesekvenser mellom start og sluttpunkt


def hent_veglenkesekvenser_rute(startpunkt, sluttpunkt): #utm33 koord

    BASE = "https://nvdbapiles.atlas.vegvesen.no/vegnett/api/v4"

    HEADERS = {
        "X-Client": "tina-heier-ntnu-gnss"
    }
    url = f"{BASE}/beta/vegnett/rute"

    start = f"{startpunkt[0]},{startpunkt[1]}"
    slutt = f"{sluttpunkt[0]},{sluttpunkt[1]}"

    params = {
     "start": start,
     "slutt": slutt,
     "maks_avstand": 10,
     "omkrets": 100,
     "konnekteringslenker": "true"
    }

    r = requests.get(url, headers=HEADERS, params=params)

    print("STATUS:", r.status_code)

    r.raise_for_status()

    data = r.json()

    #Hente pos til alle segmenter og gjør de til shapely LineStrings
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


#Dele veilinjen i masse ulike deler, med 10m avstand og får koord i x,yz 
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

        points.append((x, y,z))

    
    return points


startpunkt = 270239.58,7040945.2 #samf
sluttpunkt = 270356.96,7039392.78

rute = hent_veglenkesekvenser_rute(startpunkt, sluttpunkt)

dele_veilinje(startpunkt, sluttpunkt, 10)