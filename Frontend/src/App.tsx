import { useEffect, useState } from "react"

function App() {
  const [msg, setMsg] = useState("")

  useEffect(() => {
    fetch("http://127.0.0.1:5000/api/GNSS-test")
      .then(res => res.json())
      .then(data => setMsg(data.msg))
      .catch(err => console.error(err))
  }, [])

  return (
    <div style={{ padding: 40 }}>
      <h1>test</h1>
      <p>{msg}</p>
    </div>
  )
}

export default App