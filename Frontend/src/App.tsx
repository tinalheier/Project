import { useEffect, useState } from "react"
import Frontpage from "./routes/frontpage"
import MapPage from "./routes/map"

function App() {
  const [msg, setMsg] = useState<string>("Backend")

  useEffect(() => {
    fetch("http://127.0.0.1:5000/api/GNSS-test")
      .then(res => res.json())
      .then(data => setMsg(data.msg))
      .catch(err => console.error(err))
  }, [])

  return (
    <div className="app-root">
      <header className="header">
       <h1 id = "headerH1">
            GNSS Tool
       </h1>
      </header>

      <main className="main">
        <Frontpage />
      </main>
      <footer className="footer"> 
      </footer>
    </div>
  )
}

export default App