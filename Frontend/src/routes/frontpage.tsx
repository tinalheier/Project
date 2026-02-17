import MapPage from "./map"

function Frontpage() {
    return (
      <div className="frontpage">
        <div className="left">
            <div className="points"> 
                <p>
                    Start Point (E,N)
                </p>
                <input className="coordInput" />
            </div>
            <div className="points"> 
                <p>
                    End Point (E,N)
                </p>
                <input className="coordInput" />
            </div>
            <div className="points">
                <p>
                    Observation time (UTC)
                </p>
                <input type="datetime-local" />
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
                <button id = "roadbutton"> Find road </button>
            </div>
        </div>
        <div className="right">
            <MapPage />

            <div className="boks">

            </div>
        
        </div>
      </div>
    )
  }
  
  export default Frontpage