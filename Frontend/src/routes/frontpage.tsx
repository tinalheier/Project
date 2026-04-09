import MapPage from "./map"
import { useEffect, useMemo, useState } from "react"
import proj4 from "proj4"
import Skyplot from "./skyplot"
import LineChart from "./dopchart"


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
    const [mask, setMask] = useState<number>(10)
    const [selectedSystems, setSelectedSystems] = useState({
        GPS: true, 
        Galileo: true,
        Beidou: true,
        Glonass: true,
    });
    const [errorMessage, setErrorMessage] = useState<string | null>(null)
    const [buttonClick, setButtonClick] = useState(false)
    const [skyplotData, setSkyplotData] = useState<any | null>(null)

    const startUtm = useMemo(() => getUTMNumbers(startText), [startText])
    const endUtm = useMemo(() => getUTMNumbers(endText), [endText])

    const startLatLng =  useMemo(() => UTM33ToLatLng(startUtm), [startUtm])
    const endLatLng =  useMemo(() => UTM33ToLatLng(endUtm), [endUtm])

    const [dopPoints, setDopPoints] = useState<any[]>([])


    const [dopChartData, setDopChartData] = useState<{ distance: number; pdop: number; gdop: number; lat: number; lon: number}[]>([])

    const [pageLoad, setPageLoad] = useState(false)

    function roadAnalysis(){

        if (!startUtm || !endUtm){
            setErrorMessage("Choose start and end point")
            return
        }

        if (!date){
            setErrorMessage("Choose obs time")
            return
        }

        setErrorMessage(null)
    
        setButtonClick(true)
        
        setPageLoad(true)
        fetch(
          `http://127.0.0.1:5000/api/dop?` +
          `start_e=${startUtm.east}` +
          `&start_n=${startUtm.north}` +
          `&end_e=${endUtm.east}` +
          `&end_n=${endUtm.north}` +
          `&date=${date}` +
          `&gps=${selectedSystems.GPS}` +
          `&galileo=${selectedSystems.Galileo}` +
          `&beidou=${selectedSystems.Beidou}` +
          `&glonass=${selectedSystems.Glonass}` +
          `&mask=${mask}`
        )
        .then(r => r.json())
        .then(data => {
          if (!data?.features) {
            console.error("No features in response:", data)
            setDopPoints([])
            setDopChartData([])
            return
          }
          setDopPoints(data.features)
          setDopChartData(data.chart)
          setRoute([])
        })
        .catch(console.error)
        .finally(() => {
            setPageLoad(false)
         })

      }
 
           

       useEffect(() =>{
        if (!startUtm || !endUtm){
            setRoute([])
 
            return
        }

        fetch(`http://127.0.0.1:5000/api/route?start_e=${startUtm.east}&start_n=${startUtm.north}&end_e=${endUtm.east}&end_n=${endUtm.north}`)
        
        .then(r => r.json())
        .then(geo =>{
            const coords = geo.geometry.coordinates
            const latlngs = coords.map(([lon, lat]: [number, number]) => [lat,lon])
            setRoute(latlngs)
        })
        .catch(console.error)
    }, [startUtm, endUtm])

    function handlePointClick(index:number){
    
    fetch(
    `http://127.0.0.1:5000/api/skyplot_terrain?` +
    `index=${index}` +
    `&date=${date}` +
    `&mask=${mask}` +
     `&gps=${selectedSystems.GPS}` +
    `&galileo=${selectedSystems.Galileo}` +
    `&beidou=${selectedSystems.Beidou}` +
    `&glonass=${selectedSystems.Glonass}`
)

  .then(r => r.json())
  .then(data => {
    setSkyplotData(data)
  })
    }


    function handleResetClick(){
        if (pageLoad){
            setPageLoad(false)
        }
        
        setSkyplotData(null)
        setDopChartData([])
        setDopPoints([])
        
    }


    function getDateYesterday(){
        const today = new Date()

        today.setDate(today.getDate() - 1)
        today.setHours(23, 59, 0, 0)

        return today.toISOString().slice(0,16)
    }


    return (
      <div className="frontpage">
        <div className="left">
            <div className="points"> 
                <p>
                    Start Point (UTM33)
                </p>
                <input className="coordInput"  placeholder="E, N (f.eks. 270239.58,7040945.2 or Click on map)" value={startText} 
                onChange={(e) => setStartText(e.target.value)}/>
            </div>
            <div className="points"> 
                <p>
                    End Point (UTM33)
                </p>
                <input className="coordInput" placeholder="E, N (f.eks. 270239.58,7040945.2  or Click on map)" value={endText} 
                onChange={(e) => setEndText(e.target.value)}/>
            </div>
            <div className="points">
                <p>
                    Observation time (UTC)
                </p>
                <input type="datetime-local" min='2013-01-01 00:00:00' max = {getDateYesterday()} value = {date} 
                onChange={(e) => setDate(e.target.value)}/>
            </div>
            <div id ="gnss-systems">
                <h2>GNSS Systems</h2>
                <div id ="checkbox-row">
                    <div className ="checkbox-id">
                        <p> GPS </p>
                        <input type ="checkbox" id="GPS-button" className="gnss-checkbox" 
                        checked = {selectedSystems.GPS} onChange={(e) =>
                        setSelectedSystems(prev => ({ ...prev, GPS:e.target.checked})) }/>
                    </div>
                    <div className ="checkbox-id">
                        <p> Galileo </p>
                        <input type ="checkbox" id="Galileo-button" className="gnss-checkbox"
                        checked = {selectedSystems.Galileo} onChange={(e) =>
                            setSelectedSystems(prev => ({ ...prev, Galileo:e.target.checked})) }/>
                    </div>
                    <div className ="checkbox-id">
                        <p> BeiDou </p>
                        <input type ="checkbox" id="BeiDou-button" className="gnss-checkbox"
                        checked = {selectedSystems.Beidou} onChange={(e) =>
                            setSelectedSystems(prev => ({ ...prev, Beidou:e.target.checked})) }/>
                    </div>
                    <div className ="checkbox-id">
                        <p> GLONASS </p>
                        <input type ="checkbox" id="GLONASS-button" className="gnss-checkbox"
                        checked = {selectedSystems.Glonass} onChange={(e) =>
                            setSelectedSystems(prev => ({ ...prev, Glonass:e.target.checked})) }/>
                    </div>
                </div>
            </div>
            <div id="maskanglebox">
                <p> Mask angle: {mask}°</p>
                <input type = "range" min="1" max ="90" className="slider" id ="mySlider" value = {mask} 
                onChange={(e) => setMask(Number(e.target.value))}/>
            </div>
            {errorMessage && (
            <div style={{ color: "red", marginBottom: "10px" }}>
                {errorMessage}
            </div>
            )}
            <div id = "findroad">
                <button className = "roadbutton" onClick ={roadAnalysis}> DOP analysis </button>
            </div>
        </div>
        <div className="right">
            <MapPage start={startLatLng}  end={endLatLng} route={route} dopPoints={dopPoints} onPointClick={handlePointClick} onResetClick={handleResetClick} setStartUtmText={(utmText: string) => setStartText(utmText)}
          setEndUtmText={(utmText: string) => setEndText(utmText)}/>
            
                {pageLoad && (
                    <div className="loader"></div>
                )}
            <div className="boks">
                {dopChartData.length > 0 && (
                    <LineChart data = {dopChartData} handlePointClick = {handlePointClick}/>
                )}

                 {skyplotData && (
                    <Skyplot data ={skyplotData} />
                )}

            </div>
        </div>
      </div>
    )
    
  }
  
  export default Frontpage