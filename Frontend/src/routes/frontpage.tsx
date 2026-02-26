import MapPage from "./map"
import { useEffect, useMemo, useState } from "react"
import proj4 from "proj4"

proj4.defs("EPSG:25833", "+proj=utm +zone=33 +ellps=GRS80 +towgs84=0, 0, 0, 0, 0, 0, 0 +units=m +no_defs")

type UTM = {east: number; north: number } | null
type LatLng = [number, number] | null 

function getUTMNumbers(text: string): UTM {
    const cleaned = text.trim().replace(/\s+/g, " ")
    const parts = cleaned.includes(",") ? cleaned.split(",") : cleaned.split(" ")
    if (parts.length !== 2) return null

    const east = Number(String(parts[0]).trim())
    const north = Number(String(parts[1]).trim())

    if (!Number.isFinite(east)|| !Number.isFinite(north)) return null

    return {east, north}
}

function UTM33ToLatLng(utm: UTM): LatLng{
    if (!utm) return null

    const[lon, lat] = proj4("EPSG:25833", "EPSG:4326", [utm.east, utm.north]) as [number, number]
    return [lat, lon]
}
 
function Frontpage() {

    const [startText, setStartText] = useState("")
    const [endText, setEndText] = useState("")
    const [route, setRoute] = useState<[number, number][]>([])
    const [date, setDate] = useState("")

    const startUtm = useMemo(() => getUTMNumbers(startText), [startText])
    const endUtm = useMemo(() => getUTMNumbers(endText), [endText])

    const startLatLng =  useMemo(() => UTM33ToLatLng(startUtm), [startUtm])
    const endLatLng =  useMemo(() => UTM33ToLatLng(endUtm), [endUtm])

   

    useEffect(() =>{
        if (!startUtm || !endUtm){
            setRoute([])
            return
        }

        fetch(`http://127.0.0.1:5000/api/route?start_e=${startUtm.east}&start_n=${startUtm.north}&end_e=${endUtm.east}&end_n=${endUtm.north}&date=${date}`)
        .then(r => r.json())
        .then(geo =>{
            const coords = geo.geometry.coordinates
            const latlngs = coords.map(([lon, lat]: [number, number]) => [lat,lon])
            setRoute(latlngs)
        })
        .catch(console.error)
    }, [startUtm, endUtm])





    return (
      <div className="frontpage">
        <div className="left">
            <div className="points"> 
                <p>
                    Start Point (UTM33)
                </p>
                <input className="coordInput"  placeholder="E, N (f.eks. 270239.58,7040945.2)" value={startText} 
                onChange={(e) => setStartText(e.target.value)}/>
            </div>
            <div className="points"> 
                <p>
                    End Point (UTM33)
                </p>
                <input className="coordInput" placeholder="E, N (f.eks. 270239.58,7040945.2)" value={endText} 
                onChange={(e) => setEndText(e.target.value)}/>
            </div>
            <div className="points">
                <p>
                    Observation time (UTC)
                </p>
                <input type="datetime-local" value = {date} 
                onChange={(e) => setDate(e.target.value)}/>
            </div>
            <div id ="gnss-systems">
                <h2>GNSS Systems</h2>
                <div id ="checkbox-row">
                    <div className ="checkbox-id">
                        <p> GPS </p>
                        <input type ="checkbox" id="GPS-button" className="gnss-checkbox"/>
                    </div>
                    <div className ="checkbox-id">
                        <p> Galileo </p>
                        <input type ="checkbox" id="Galileo-button" className="gnss-checkbox"/>
                    </div>
                    <div className ="checkbox-id">
                        <p> BeiDou </p>
                        <input type ="checkbox" id="BeiDou-button" className="gnss-checkbox"/>
                    </div>
                    <div className ="checkbox-id">
                        <p> GLONASS </p>
                        <input type ="checkbox" id="GLONASS-button" className="gnss-checkbox"/>
                    </div>
                </div>
            </div>
            <div id="maskanglebox">
                <p> Mask angle</p>
                <input type = "range" min="1" max ="90" className="slider" id ="mySlider"/>
            </div>
            <div id = "findroad">
                <button className = "roadbutton"> Find road </button>
            </div>
        </div>
        <div className="right">
            <MapPage start={startLatLng}  end={endLatLng} route={route} setStartUtmText={(utmText: string) => setStartText(utmText)}
          setEndUtmText={(utmText: string) => setEndText(utmText)}/>

            <div className="boks">

            </div>
        
        </div>
      </div>
    )
  }
  
  export default Frontpage