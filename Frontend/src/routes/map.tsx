import { MapContainer, TileLayer, Marker, useMapEvents, useMap, Polyline } from "react-leaflet"
import "leaflet/dist/leaflet.css"
import L from "leaflet"
import proj4 from "proj4"


import markerIcon from "leaflet/dist/images/marker-icon.png"
import { useEffect } from "react"

const defaultIconStart = L.icon({ iconUrl: markerIcon, iconSize: [25, 41] })
const defaultIconEnd = L.icon({ iconUrl: markerIcon, iconSize: [25, 41] })

type LatLng = [number, number] | null



function latLngToUtm33Text(point: [number, number]): string {
  const [lat, lon] = point
  // proj4 forventer [lon, lat]
  const [e, n] = proj4("EPSG:4326", "EPSG:25833", [lon, lat]) as [number, number]
  return `${e.toFixed(2)},${n.toFixed(2)}`
}


function ClickHandler({
  start,
  end,
  setStartUtmText,
  setEndUtmText,
}: {
  start: LatLng
  end: LatLng
  setStartUtmText?: (v: string) => void
  setEndUtmText?: (v: string) => void
}) {
  useMapEvents({
    click(e) {
      const point: [number, number] = [e.latlng.lat, e.latlng.lng]

      if (!start) {
        setStartUtmText?.(latLngToUtm33Text(point))
        return
      }
      if (!end) {
        setEndUtmText?.(latLngToUtm33Text(point))
      }
    },
  })
  return null
}

function MapPage({
  start,
  end,
  route, 
  setStartUtmText,
  setEndUtmText,

}: {
  start: LatLng
  end: LatLng
  route: [number, number][]
  setStartUtmText?: (v: string) => void
  setEndUtmText?: (v: string) => void
}) 


{
  function resetButton() {
    setStartUtmText?.("")
    setEndUtmText?.("")
  }

  function UpdateCenterMap({center}: {center:[number, number] | null}) {
    const map = useMap()

    useEffect(() => {
      if (center) {
        map.setView(center, map.getZoom())
      }
    }, [center])

    return null
  }

  return (
    <div style={{ height: "75%", width: "100%" }}>
      <MapContainer center={[63.4305, 10.3951]} zoom={13} style={{ height: "100%", width: "100%" }}>
        <UpdateCenterMap center = {start} />
        

        <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />

        <ClickHandler
          start={start}
          end={end}
          setStartUtmText={setStartUtmText}
          setEndUtmText={setEndUtmText}
        />

        {start && <Marker position={start} icon={defaultIconStart} />}
        {end && <Marker position={end} icon={defaultIconEnd} />}
        {route.length > 1 && <Polyline positions={route}/>}
      </MapContainer>

      <div id="resetButtonMap">
        <button className="roadbutton" onClick={resetButton} disabled={!start && !end}>
          Nullstill
        </button>
      </div>
    </div>
  )
}

export default MapPage