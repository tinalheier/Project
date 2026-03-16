type SkyplotProps = {
  data: any
}

function Skyplot({ data }: SkyplotProps) {
  return (
    <div style={{ padding: "10px", background: "white" }}>
      <h3>Skyplot</h3>

      <p>Date: {data.date}</p>
      <p>Time: {data.time}</p>

      <h4>GPS satellites</h4>
      <pre>{JSON.stringify(data.GPS, null, 2)}</pre>

      <h4>Galileo satellites</h4>
      <pre>{JSON.stringify(data.Galileo, null, 2)}</pre>

      <h4>Beidou satellites</h4>
      <pre>{JSON.stringify(data.Beidou, null, 2)}</pre>

      <h4>Glonass satellites</h4>
      <pre>{JSON.stringify(data.Glonass, null, 2)}</pre>
    </div>
  )
}

export default Skyplot