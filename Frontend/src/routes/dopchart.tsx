import React from "react";
import { Chart as ChartJS, LineElement, PointElement, LinearScale, CategoryScale, Tooltip, Legend } from "chart.js";
import { Line } from "react-chartjs-2";


ChartJS.register(
  LineElement,
  PointElement,
  LinearScale,
  CategoryScale,
  Tooltip,
  Legend
)


type ChartPoint = {
  distance: number
  pdop: number
  gdop: number
  lat: number
  lon: number
}

type Props = {
  data: ChartPoint[]
  handlePointClick: (index: number) => void
  
}

function dopColor(dop: number){
  if (dop == 0) return "black"
  if (dop < 1) return "green"
  if (dop < 2) return "#43c150"
  if (dop < 5) return "yellow" 
  if (dop < 10) return  "#fbbf24"
  if (dop < 20) return  "#fb8824"
  return "red"
}


export default function LineChart({ data, handlePointClick }: Props){
  const chartData = {
    labels: data.map( p => p.distance),
    datasets: [
      {
        label: "PDOP",
        data: data.map(p => p.pdop),
        borderColor: "pink",
        backgroundColor:"pink",

        pointBackgroundColor: data.map(p => dopColor(p.pdop)), 
        pointBorderColor: "pink",
        tension: 0.2, 
        pointRadius: 5
      },
       {
        label: "GDOP",
        data: data.map(p => p.gdop),
        borderColor: "green",
        backgroundColor:"green",

        pointBackgroundColor: data.map(p => dopColor(p.pdop)), 
        pointBorderColor: "green",
        tension: 0.2, 
        pointRadius: 5
      }
    ]
  }

    const options = {
    responsive: true,
    onClick: (event:any, elements:any) => {
      if (!elements.length) return

      const index = elements[0].index
      
      handlePointClick(index)

    },

    maintainAspectRatio: false,
    scales: {
      x: {
        title: {
          display: true,
          text: "Distance along road (m)"
        }
      },
      y: {
        title: {
          display: true,
          text: "DOP value"
        },
        beginAtZero: true
      }
    }
  }

  return (
    <div style={{height: "500px"}}>
       <p>Click on a point in the map or in the DOP chart to display Skyplot (Scroll down)</p>
      <Line data={chartData} options={options} />
    </div>
  )
}