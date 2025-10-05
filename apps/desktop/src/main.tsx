import React from 'react'
import { createRoot } from 'react-dom/client'

function App() {
  return (
    <div style={{ padding: 16 }}>
      <h1>Local TA</h1>
      <p>Your local teaching assistant, running fully on-device.</p>
    </div>
  )
}

const container = document.getElementById('root')!
const root = createRoot(container)
root.render(<App />)


