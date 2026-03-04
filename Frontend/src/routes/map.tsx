import { MapContainer, TileLayer, Marker, useMapEvents, useMap, Polyline,CircleMarker, Tooltip } from "react-leaflet"
import "leaflet/dist/leaflet.css"
import L from "leaflet"
import proj4 from "proj4"
import start from '../assets/start.png'
import end from '../assets/end.png'
import markerIcon from "leaflet/dist/images/marker-icon.png"
import { useEffect } from "react"

const defaultIconStart = L.icon({ iconUrl: start, iconSize: [30, 47] })

const defaultIconEnd = L.icon({ iconUrl: end, iconSize: [30, 47] })

type LatLng = [number, number] | null



function latLngToUtm33Text(point: [number, number]): string {
  const [lat, lon] = point
  const [e, n] = proj4("EPSG:4326", "EPSG:25833", [lon, lat]) as [number, number]
  return `${e.toFixed(5)},${n.toFixed(5)}`
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
function dopColor(pdop: number) {
  if (pdop == 0) return "black"
  if (pdop < 2) return "green"
  if (pdop < 4) return "yellow"
  if (pdop < 6) return "orange"
  return "red"
}

function MapPage({
  start,
  end,
  route, 
  dopPoints,
  setStartUtmText,
  setEndUtmText,

}: {
  start: LatLng
  end: LatLng
  route: [number, number][]
  dopPoints: any[]
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
        {Array.isArray(dopPoints) &&
          dopPoints.map((f: any, idx: number) => {
            const [lon, lat] = f.geometry.coordinates
            const pdop = Number(f.properties?.pdop)
            

    return (
      <CircleMarker
        key={idx}
        center={[lat, lon]}
        radius={6}
        pathOptions={{
          color: dopColor(pdop),
          fillColor: dopColor(pdop),
          fillOpacity: 0.9,
        }}
      > 
        <Tooltip
          permanent
          direction="center"
          className="dop-label"
        >
          {pdop === 0 ? "X" : pdop.toFixed(1)}
          be

        </Tooltip>

        <Tooltip direction="top" offset={[0, -5]} opacity={1}>
          {pdop === 0 ? (
        <>
          Less than 4 available satellites. <br />
          Position (UTM33): {latLngToUtm33Text([lat, lon])}
        </>
      ) : (
        <>
          PDOP: {pdop.toFixed(2)} <br />
          Position (UTM33): {latLngToUtm33Text([lat, lon])}
        </>
      )}
        </Tooltip>
      </CircleMarker>
  )
  })}
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