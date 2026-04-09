import Plot from "react-plotly.js";

type SkyplotProps = {
  data: any;
};

function julianToDate(year: number, julianDay: number){
  const date = new Date(year, 0)
  date.setDate(julianDay)
  return date;
  };



function Skyplot({ data }: SkyplotProps) {

  const createTrace = (gnssData: any, name: string, color: string) => {
    if (!gnssData || gnssData.az_deg.length === 0) return null;

    return {
      type: "scatterpolar",
      mode: "markers+text",
      r: gnssData.elev.map((e: number) => 90 - e),
      theta: gnssData.az_deg,
      text: gnssData.sat,
      textposition: "top center",
      name: name,
      marker: {
        size: 10,
        color: color,
      },
      customdata: gnssData.elev,
      hovertemplate:
        "<b>%{text}</b><br>" +
        "Azimuth: %{theta:.1f}°<br>" +
        "Elevation: %{customdata:.1f}°<extra></extra>",
    };
  };

  const traces = [
  createTrace(data.GPS, "GPS", "#3d8bc3"),
  createTrace(data.Galileo, "Galileo", "#325b3b"),
  createTrace(data.Beidou, "BeiDou", "#d62728"),
  createTrace(data.Glonass, "GLONASS", "#b2b722"),
].filter((t): t is any => t !== null);
  

const createTraceElevation = (maxelev: any) =>{
  const az = Object.keys(maxelev).map(Number);
  const elev =  Object.values(maxelev).map(Number);

  // lukke polygonet
  const azClosed = [...az, az[0]];
  const elevClosed = [...elev.map((e:number) => 90-e), 90-elev[0]]
  return{
    type: "scatterpolar", 
    mode: "lines",
    theta: azClosed,
    r: elevClosed,
    name: "Terrain mask",
    customdata: [...elev, elev[0]],
    hovertemplate:
      "Max elevation in horizon: %{customdata:.1f}°<br>" +
      "Azimuth: %{theta}°<extra></extra>",
    line: {
      color:"red",
      width: 2,
    },

  };
};

  const createMaskangleTrace = (maskangle: number) =>{
    const az = Array.from({length: 361}, (_, i) => i);
    return{ 
    type: "scatterpolar", 
    mode: "lines",
    theta: az,
    r: az.map(()=>90-maskangle),
    name: "Mask angle",
    hoverinfo: "skip",
    line: {
      color:"rgba(255,0,0,0.5)",
      width: 1,
      dash: "dash",
    },
    };
  };

  const maxElevTrace = createTraceElevation(data.max_elevation);

  const Maskangle = createMaskangleTrace(data.maskElevation)

  const dateSkyplot = julianToDate(data.date.slice(3,8), data.date.slice(0,3));
  
  const allSatellites = [
  ...(data.GPS?.sat || []),
  ...(data.Galileo?.sat || []),
  ...(data.Beidou?.sat || []),
  ...(data.Glonass?.sat || []),
];
  return (
    <div style={{ padding: "5px", background: "white" }}>
      <h3>Skyplot</h3>
        <div style={{background: "white"}}>
          <p>Date: {dateSkyplot.toLocaleDateString("no-NO")}  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Observation Time: {data.time}</p>
          <p>Available satellites: {data.GPS?.sat?.length || 0} &nbsp;GPS,  &nbsp;&nbsp;&nbsp;{data.Galileo?.sat?.length || 0}&nbsp; Galileo,  &nbsp;&nbsp;&nbsp; {data.Beidou?.sat?.length || 0}&nbsp; Beidou,  &nbsp;&nbsp;&nbsp; {data.Glonass?.sat?.length || 0} &nbsp;Glonass
          </p>
          <div style={{background: "white"}}>
          <p>
            <b>GPS: </b> {data.GPS?.sat?.join(", ") || "-"}
          </p>

          <p>
            <b> Galileo: </b> {data.Galileo?.sat?.join(", ") || "-"}
          
          </p>

          <p>
            <b> BeiDou: </b> {data.Beidou?.sat?.join(", ") || "-"}
          </p>

          <p>
            <b> GLONASS: </b> {data.Glonass?.sat?.join(", ") || "-"}
          </p>
          </div>
      </div>
      <div style={{ width: "100%", height: "600px" }}>
        <Plot
          data={[...traces, maxElevTrace,Maskangle]}
          layout={{
            polar: {
              radialaxis: {
                range: [0, 90],
                tickvals: [0, 30, 60, 90],
                ticktext: ["90°", "60°", "30°", "0°"],
                angle: 90,
              },
              angularaxis: {
                direction: "clockwise",
                rotation: 90,
              },
            },
            showlegend: true,
          }}
          style={{ width: "100%", height: "100%" }}
          useResizeHandler={true}
        />
      </div>
    </div>
  );
}

export default Skyplot;