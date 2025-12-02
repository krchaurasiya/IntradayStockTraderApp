export default function Gauges({ signals = [] }) {

  const buys = signals.filter(s => s.signal === 'BUY').length
  const sells = signals.filter(s => s.signal === 'SELL').length
  const total = buys + sells || 1

  const buyStrength = Math.round((buys / total) * 100)
  const sellStrength = 100 - buyStrength

  return (
    <div>
      <h3 style={{ color: 'lightgreen' }}>BUY: {buyStrength}%</h3>
      <h3 style={{ color: 'red' }}>SELL: {sellStrength}%</h3>
    </div>
  )
}
