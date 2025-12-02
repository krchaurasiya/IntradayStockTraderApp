import { useEffect, useState } from 'react'
import axios from 'axios'

import StockList from './components/StockList'
import CandlestickChart from './components/CandlestickChart'
import Gauges from './components/Gauges'
import OrderPanel from './components/OrderPanel'

import './App.css'

export default function App() {
  const [prices, setPrices] = useState([])
  const [signals, setSignals] = useState([])
  const [selected, setSelected] = useState('RELIANCE.NS')
  const [status, setStatus] = useState('loading')

  useEffect(() => {
    let intervalId

    async function loadAll() {
      try {
        setStatus('loading')

        // ✅ Load live price candles
        const quoteRes = await axios.get(
          `http://localhost:5000/api/quote?symbol=${selected}`
        )
        setPrices(quoteRes.data)

        // ✅ Load AI indicators
        const indicatorRes = await axios.post(
          `http://localhost:5000/api/indicators`,
          { data: quoteRes.data }
        )

        setSignals(indicatorRes.data)
        setStatus('ready')
      } catch (err) {
        console.error('UI LOAD ERROR:', err)
        setStatus('error')
      }
    }

    loadAll()

    // ✅ Auto refresh every 15 seconds
    intervalId = setInterval(loadAll, 15000)

    return () => clearInterval(intervalId)
  }, [selected])

  return (
    <div className="dashboard-root">
      <header className="header">
        <div className="brand">AI - Trading App</div>
        <div className="header-right">
          <div>
            Stock: <b>{selected}</b>
          </div>
          <div>Status: {status}</div>
        </div>
      </header>

      <div className="layout">
        {/* LEFT PANEL */}
        <aside className="left-panel card">
          <h3>List of Stocks</h3>
          <StockList onSelect={setSelected} />
        </aside>

        {/* CENTER PANEL */}
        <main className="center-panel card">
          <h3>Candlestick Charts Here</h3>
          <CandlestickChart data={prices} />

          {status === 'loading' && (
            <div style={{ marginTop: 10, color: '#aaa' }}>
              Loading market data...
            </div>
          )}

          {status === 'error' && (
            <div style={{ marginTop: 10, color: 'red' }}>
              Error loading data from server
            </div>
          )}
        </main>

        {/* RIGHT PANEL */}
        <aside className="right-panel">
          <div className="card">
            <Gauges signals={signals} />
          </div>

          <div className="card">
            <OrderPanel symbol={selected} />
          </div>
        </aside>
      </div>
    </div>
  )
}
