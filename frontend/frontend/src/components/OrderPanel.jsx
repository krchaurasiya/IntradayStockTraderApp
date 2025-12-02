import { useState } from 'react'
import axios from 'axios'

export default function OrderPanel({ symbol }) {
  const [side, setSide] = useState('BUY')
  const [qty, setQty] = useState(1)
  const [sl, setSl] = useState('')
  const [tp, setTp] = useState('')
  const [msg, setMsg] = useState(null)
  const [loading, setLoading] = useState(false)

  async function placeOrder() {
    if (!symbol) {
      setMsg('❌ No stock selected')
      return
    }

    if (!qty || qty <= 0) {
      setMsg('❌ Quantity must be greater than 0')
      return
    }

    try {
      setLoading(true)
      setMsg(null)

      const res = await axios.post('http://localhost:5000/api/trade', {
        symbol,
        side,
        qty: Number(qty),   // ✅ ensure number
        sl: sl ? Number(sl) : null,
        tp: tp ? Number(tp) : null
      })

      setMsg(`✅ Order Placed Successfully:\n${JSON.stringify(res.data, null, 2)}`)
    } catch (e) {
      console.error(e)
      setMsg('❌ Order Failed: Backend error')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="order-panel">
      <div style={{ display: 'flex', gap: '10px' }}>
        <button
          onClick={() => setSide('BUY')}
          className={side === 'BUY' ? 'active-buy' : ''}
        >
          Buy
        </button>

        <button
          onClick={() => setSide('SELL')}
          className={side === 'SELL' ? 'active-sell' : ''}
        >
          Sell
        </button>
      </div>

      <input
        type="number"
        placeholder="Qty"
        value={qty}
        onChange={e => setQty(e.target.value)}
        min="1"
      />

      <input
        type="number"
        placeholder="SL"
        value={sl}
        onChange={e => setSl(e.target.value)}
      />

      <input
        type="number"
        placeholder="TP"
        value={tp}
        onChange={e => setTp(e.target.value)}
      />

      <button onClick={placeOrder} disabled={loading}>
        {loading ? 'Placing...' : side}
      </button>

      {msg && <pre style={{ marginTop: '10px', color: '#ddd' }}>{msg}</pre>}
    </div>
  )
}
