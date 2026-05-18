import { useState } from "react";
import {
  Chart as ChartJS,
  LineElement,
  PointElement,
  LinearScale,
  CategoryScale,
  Tooltip,
  Legend,
} from "chart.js";
import { Line } from "react-chartjs-2";

ChartJS.register(LineElement, PointElement, LinearScale, CategoryScale, Tooltip, Legend);

type ChartPoint = {
  distance: number;
  pdop: number;
  gdop: number;
  lat: number;
  lon: number;
};

type Props = {
  data: ChartPoint[];
  handlePointClick: (index: number) => void;
};

function dopColor(dop: number) {
  if (dop === 0) return "black";
  if (dop < 1) return "green";
  if (dop < 2) return "#43c150";
  if (dop < 5) return "yellow";
  if (dop < 10) return "#fbbf24";
  if (dop < 20) return "#fb8824";
  return "red";
}

export default function LineChart({ data, handlePointClick }: Props) {
  const [viewMode, setViewMode] = useState<"chart" | "tabell" | "heatmap">("chart");

  const isTable = viewMode === "tabell";
  const isHeatmap = viewMode === "heatmap";

  const segmentColor = (ctx: any) => {
    const value = ctx.p0?.parsed?.y ?? ctx.p1?.parsed?.y ?? 0;
    return dopColor(value);
  };


const chartData = {
  labels: data.map((p) => p.distance),

  datasets: [
    {
      label: "PDOP",

      data: data.map((p) => p.pdop),

      borderColor: isHeatmap ? segmentColor : "pink",

      backgroundColor: "pink",

      pointBackgroundColor: isHeatmap
        ? "transparent"
        : data.map((p) => dopColor(p.pdop)),

      pointBorderColor: isHeatmap ? "transparent" : "transparent",

      pointRadius: isHeatmap ? 0 : 5,

      pointHoverRadius: isHeatmap ? 0 : 5,

      tension: isHeatmap ? 0.45 : 0,

      cubicInterpolationMode: "monotone" as const,

      borderWidth: isHeatmap ? 2 : 2,

      segment: isHeatmap
        ? {
            borderColor: segmentColor,
          }
        : undefined,
    },

    {
      label: "GDOP",

      data: data.map((p) => p.gdop),

      borderColor: isHeatmap ? segmentColor : "blue",

      backgroundColor: "blue",

      pointBackgroundColor: isHeatmap
        ? "transparent"
        : data.map((p) => dopColor(p.gdop)),

      pointBorderColor: isHeatmap ? "transparent" : "transparent",

      pointRadius: isHeatmap ? 0 : 5,

      pointHoverRadius: isHeatmap ? 0 : 5,

      tension: isHeatmap ? 0.45 : 0,

      cubicInterpolationMode: "monotone" as const,

      borderWidth: isHeatmap ? 2 : 2,

      segment: isHeatmap
        ? {
            borderColor: segmentColor,
          }
        : undefined,
    },
  ],
};



  const options = {
    responsive: true,
    maintainAspectRatio: false,
    onClick: (_event: any, elements: any) => {
      if (!elements.length) return;
      const index = elements[0].index;
      handlePointClick(index);
    },
    scales: {
      x: {
        title: {
          display: true,
          text: "Distance along road (m)",
        },
      },
      y: {
        title: {
          display: true,
          text: "DOP value",
        },
        beginAtZero: true,
      },
    },
  };

  return (
    <div style={{ maxWidth: 980, width: "100%", margin: "0 auto" }}>
      <div style={{ display: "flex", flexWrap: "wrap", gap: "0.75rem", alignItems: "center", marginBottom: "1rem" }}>
        <button onClick={() => setViewMode("chart")}>Show DOP-chart</button>
        <button onClick={() => setViewMode("tabell")}>Show table</button>
        <button onClick={() => setViewMode("heatmap")}>Show heatmap</button>

        <span>
          Current display: <strong>{viewMode}</strong>
        </span>
      </div>

      <div style={{
        display: "flex",
        flexWrap: "nowrap",
        gap: "0.75rem",
        alignItems: "center",
        marginBottom: "1.5rem",
        padding: "0.75rem 0.85rem",
        backgroundColor: "#f9f9f9",
        borderRadius: "0.5rem",
        border: "1px solid #e0e0e0",
        overflowX: "auto"
      }}>
        <div style={{ display: "inline-flex", alignItems: "center", gap: "0.35rem", fontSize: "0.85rem" }}>
          <div style={{ width: "10px", height: "14px", backgroundColor: "black", borderRadius: "2px" }}></div>
          <span>DOP = 0</span>
        </div>
        <div style={{ display: "inline-flex", alignItems: "center", gap: "0.35rem", fontSize: "0.85rem" }}>
          <div style={{ width: "10px", height: "14px", backgroundColor: "green", borderRadius: "2px" }}></div>
          <span>{"DOP < 1"}</span>
        </div>
        <div style={{ display: "inline-flex", alignItems: "center", gap: "0.35rem", fontSize: "0.85rem" }}>
          <div style={{ width: "10px", height: "14px", backgroundColor: "#43c150", borderRadius: "2px" }}></div>
          <span>{"DOP < 2"}</span>
        </div>
        <div style={{ display: "inline-flex", alignItems: "center", gap: "0.35rem", fontSize: "0.85rem" }}>
          <div style={{ width: "10px", height: "14px", backgroundColor: "yellow", borderRadius: "2px", border: "1px solid #ccc" }}></div>
          <span>{"DOP < 5"}</span>
        </div>
        <div style={{ display: "inline-flex", alignItems: "center", gap: "0.35rem", fontSize: "0.85rem" }}>
          <div style={{ width: "10px", height: "14px", backgroundColor: "#fbbf24", borderRadius: "2px" }}></div>
          <span>{"DOP < 10"}</span>
        </div>
        <div style={{ display: "inline-flex", alignItems: "center", gap: "0.35rem", fontSize: "0.85rem" }}>
          <div style={{ width: "10px", height: "14px", backgroundColor: "#fb8824", borderRadius: "2px" }}></div>
          <span>{"DOP < 20"}</span>
        </div>
        <div style={{ display: "inline-flex", alignItems: "center", gap: "0.35rem", fontSize: "0.85rem" }}>
          <div style={{ width: "10px", height: "14px", backgroundColor: "red", borderRadius: "2px" }}></div>
          <span>DOP ≥ 20</span>
        </div>
      </div>

      {isTable ? (
        <div
          style={{
            overflowX: "auto",
            overflowY: "auto",
            maxWidth: 980,
            width: "100%",
            maxHeight: "500px",
            border: "1px solid #ddd",
            borderRadius: "0.5rem",
            margin: "0 auto",
          }}
        >
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "1.5fr 1fr 1fr",
              gap: "0.5rem",
              padding: "0.75rem",
              background: "#f7f7f7",
              fontWeight: 600,
              position: "sticky",
              top: 0,
              zIndex: 1,
            }}
          >
            <div>Distance (m)</div>
            <div>PDOP</div>
            <div>GDOP</div>
          </div>

          {data.map((p, index) => (
            <div
              key={index}
              style={{
                display: "grid",
                gridTemplateColumns: "1.5fr 1fr 1fr",
                gap: "0.5rem",
                padding: "0.75rem",
                borderTop: "1px solid #ececec",
                alignItems: "center",
              }}
            >
              <div>{p.distance}</div>

              <div
                style={{
                  background: dopColor(p.pdop),
                  color: "black",
                  padding: "0.5rem",
                  borderRadius: "0.25rem",
                  textAlign: "center",
                  cursor: "pointer",
                }}
                onClick={() => handlePointClick(index)}
              >
                {p.pdop.toFixed(2)}
              </div>

              <div
                style={{
                  background: dopColor(p.gdop),
                  color: "black",
                  padding: "0.5rem",
                  borderRadius: "0.25rem",
                  textAlign: "center",
                  cursor: "pointer",
                }}
                onClick={() => handlePointClick(index)}
              >
                {p.gdop.toFixed(2)}
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div style={{ height: "500px", maxWidth: 980, width: "100%", margin: "0 auto" }}>
          <p>
            Click on a point in the map or in the DOP chart to display Skyplot
            (Scroll down)
          </p>
          <Line key={viewMode} data={chartData} options={options} />
        </div>
      )}
    </div>
  );
}