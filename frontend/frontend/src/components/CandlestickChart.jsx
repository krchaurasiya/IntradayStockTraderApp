import ReactApexChart from 'react-apexcharts'

export default function CandlestickChart({ data = [] }) {
  const series = [{
    data: data.map(d => ({
      x: d.datetime,          // ✅ FIXED KEY
      y: [
        Number(d.open),
        Number(d.high),
        Number(d.low),
        Number(d.close)
      ]
    }))
  }]

  const options = {
    chart: {
      type: 'candlestick',
      height: 500,
      toolbar: { show: true }
    },
    theme: { mode: 'dark' },
    xaxis: { type: 'category' },
    yaxis: { tooltip: { enabled: true } },
    plotOptions: {
      candlestick: {
        colors: {
          upward: '#16a34a',
          downward: '#dc2626'
        }
      }
    }
  }

  return <ReactApexChart options={options} series={series} type="candlestick" height={500} />
}
