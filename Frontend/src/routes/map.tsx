
import { MapContainer, TileLayer, Marker, Popup} from "react-leaflet"
import "leaflet/dist/leaflet.css"


function MapPage() {
  return (
    <div style={{ height: "60%", width: "100%" }}>
      <MapContainer
        center={[63.4305, 10.3951]}
        zoom={13}
        style={{ height: "100%", width: "100%" }}
      >
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        <Marker
              position={[19.000855082428515, -98.19408389636365]}>
              <Popup>
                A pretty CSS3 popup. <br /> Easily customizable.
              </Popup>
        </Marker>
      </MapContainer>
    </div>
  )
}

export default MapPage