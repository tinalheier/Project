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
  lat: number
  lon: number
}

type Props = {
  data: ChartPoint[]
  handlePointClick: (lon:number, lat:number) => void
}

function pdopColor(pdop:number){
  if (pdop == 0) return "black"
  if (pdop < 1) return "green"
  if (pdop < 2) return "yellow"
  if (pdop < 5) return "orange"

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
        backgroundColor: data.map(p => pdopColor(p.pdop)), 
        tension: 0.2, 
        pointRadius: 3
      }
    ]
  }
    const options = {
    responsive: true,
    onClick: (event:any, elements:any) => {
      if (!elements.length) return

      const index = elements[0].index
      const point = data[index]
      
      handlePointClick(point.lon, point.lat)

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
          text: "PDOP"
        },
        beginAtZero: true
      }
    }
  }

  return (
    <div style={{height: "300px"}}>
      <Line data={chartData} options={options} />
    </div>
  )
}