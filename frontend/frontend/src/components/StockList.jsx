export default function StockList({ onSelect }) {
  const stocks = ['RELIANCE.NS', 'TCS.NS', 'INFY.NS', 'HDFCBANK.NS', 'ICICIBANK.NS']

  return (
    <table className="stock-table">
      <thead>
        <tr><th>#</th><th>Name</th></tr>
      </thead>
      <tbody>
        {stocks.map((s, i) => (
          <tr key={s} onClick={() => onSelect(s)}>
            <td>{i + 1}</td>
            <td>{s}</td>
          </tr>
        ))}
      </tbody>
    </table>
  )
}
