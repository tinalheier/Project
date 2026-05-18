import { MapContainer, TileLayer, Marker, useMapEvents, useMap, Polyline, CircleMarker, Tooltip } from "react-leaflet"
import "leaflet/dist/leaflet.css"
import L from "leaflet"
import proj4 from "proj4"
import start from '../assets/start.png'
import end from '../assets/end.png'
import { useEffect, useState, useRef} from "react"

const defaultIconStart = L.icon({ iconUrl: start, iconSize: [30, 47] })

const defaultIconEnd = L.icon({ iconUrl: end, iconSize: [30, 47] })
const norwayBounds = L.latLngBounds([[57.9, 4.5], [71.5, 31.5]])

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
    click(e: L.LeafletMouseEvent) {
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
  if (pdop < 1) return "green"
  if (pdop < 2) return "#43c150"
  if (pdop < 5) return "yellow" 
  if (pdop < 10) return  "#fbbf24"
  if (pdop < 20) return  "#fb8824"
  return "red"
}

function SearchControl() {
  const map = useMap()
  const controlRef = useRef<HTMLDivElement | null>(null)
  const [query, setQuery] = useState("")
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (controlRef.current) {
      L.DomEvent.disableClickPropagation(controlRef.current)
      L.DomEvent.disableScrollPropagation(controlRef.current)
    }
  }, [])

  const search = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()

    if (!query.trim()) {
      setError("Enter a city or place name")
      return
    }

    const url = `https://nominatim.openstreetmap.org/search?format=json&countrycodes=no&limit=5&q=${encodeURIComponent(query)}&viewbox=4.5,71.5,31.5,57.9&bounded=1`

    try {
      const response = await fetch(url, {
        headers: { Accept: "application/json" },
      })

      const results = await response.json()

      if (!Array.isArray(results) || results.length === 0) {
        setError("No result found in Norway")
        return
      }

      const place = results[0]
      const lat = Number(place.lat)
      const lon = Number(place.lon)

      if (place.boundingbox) {
        const bbox = [
          [Number(place.boundingbox[0]), Number(place.boundingbox[2])],
          [Number(place.boundingbox[1]), Number(place.boundingbox[3])],
        ]

        map.fitBounds(bbox as any, {
          padding: [40, 40],
          maxZoom: 13,
        })
      } else {
        map.setView([lat, lon], 13)
      }

      setError(null)
    } catch (err) {
      console.error(err)
      setError("Search failed, try another place")
    }
  }

  return (
    <div
      ref={controlRef}
      className="leaflet-control"
      style={{
        position: "absolute",
        top: 14,
        left: "50%",
        transform: "translateX(-50%)",
        zIndex: 1000,
        background: "rgba(255,255,255,0.88)",
        backdropFilter: "blur(10px)",
        borderRadius: 14,
        padding: 10,
        boxShadow: "0 4px 18px hsla(0, 52%, 55%, 0.08)",
        border: "1px solid rgba(255,255,255,0.35)",
      }}
    >
      <form onSubmit={search} style={{ display: "flex", alignItems: "center", gap: 8 }}>
        <input
          value={query}
          placeholder="Search place..."
          onChange={(e) => setQuery(e.target.value)}
          style={{
            width: 190,
            height: 30,
            padding: "0 14px",
            borderRadius: 10,
            border: "1px solid rgba(0,0,0,0.08)",
            outline: "none",
            fontSize: 14,
            background: "white",
          }}
        />

        <button
          type="submit"
          style={{
            height: 30,
            padding: "0 16px",
            borderRadius: 10,
            border: "none",
            background: "#5c763d",
            color: "white",
            fontWeight: 500,
            fontSize: 14,
            cursor: "pointer",
          }}
        >
          Search
        </button>
      </form>

      {error && (
        <div style={{ color: "#dc2626", fontSize: 12, marginTop: 6, paddingLeft: 4 }}>
          {error}
        </div>
      )}
    </div>
  )
}

function MapPage({
  start,
  end,
  route, 
  dopPoints,
  setStartUtmText,
  setEndUtmText,
  onPointClick,
  onResetClick

}: {
  start: LatLng
  end: LatLng
  route: [number, number][]
  dopPoints: any[]
  setStartUtmText?: (v: string) => void
  setEndUtmText?: (v: string) => void
  onPointClick: (index: number) => void
  onResetClick: ()=> void 
}) 

{
  function resetButton() {
    setStartUtmText?.("")
    setEndUtmText?.("")
    onResetClick()
  }

  function UpdateCenterMap({ start, end }: { start: [number, number] | null; end: [number, number] | null }) {
    const map = useMap()

    useEffect(() => {
      if (start && end) {
        const bounds = L.latLngBounds([start, end]).pad(0.2)
        map.fitBounds(bounds, {
          padding: [50, 50],
          maxZoom: 14,
        })
      } else if (start) {
        map.setView(start, map.getZoom())
      }
    }, [start, end, map])

    return null
  }

  

return (
    <div style={{ height: "75%", width: "100%" }}>
      <MapContainer
        center={[63.4305, 10.3951]}
        zoom={13}
        minZoom={3}
        maxBounds={norwayBounds.pad(0.2)}
        maxBoundsViscosity={0.8}
        style={{ height: "100%", width: "100%", position: "relative" }}
      >
        <SearchControl />

        <UpdateCenterMap start={start} end={end} />
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
            const gdop = Number(f.properties?.gdop)
            

    return (
      <CircleMarker
        key={idx}
        center={[lat, lon]}
        radius={3}
        pathOptions={{
          color: dopColor(pdop),
          fillColor: dopColor(pdop),
          fillOpacity: 0.9,
        }}
        eventHandlers={{
          click: () => onPointClick(idx)
        }}
      > 
 
      <Tooltip direction="top" offset={[0, -5]}>
        <b>Point: {idx}</b>
        <br />
        <br />
        <b> PDOP: </b><b>{pdop === 0 ? "X" : pdop.toFixed(3)}</b>
        <br />
        {pdop === 0 ? (
          <>
            Less than 4 available satellites<br/>
            UTM33: {latLngToUtm33Text([lat, lon])}
          </>
        ) : (
          <>
        <b>GDOP: {gdop === 0 ? "X" : gdop.toFixed(3)}</b>
        <br />
        UTM33: {latLngToUtm33Text([lat, lon])}
</>
        )}
      </Tooltip>
      </CircleMarker>
  )
  })}
      </MapContainer>

      <div id="resetButtonMap">
        <button className="roadbutton" onClick={resetButton} disabled={!start && !end}>
          Reset
        </button>
      </div>
    </div>
  )
}

export default MapPage
