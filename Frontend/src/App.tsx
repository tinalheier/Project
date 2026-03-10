import Frontpage from "./routes/frontpage"

function App() {

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