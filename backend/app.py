from flask import Flask, request, jsonify
from analysis import get_intraday_series, compute_indicators, fetch_fundamentals, scan_universe
import os

app = Flask(__name__)

@app.route('/api/quote')
def quote():
    symbol = request.args.get('symbol', 'RELIANCE.NS')
    timeframe = request.args.get('timeframe', '5m')

    df = get_intraday_series(symbol, timeframe)

    # ✅ Force native Python types (JSON-safe)
    records = []
    for _, row in df.iterrows():
        records.append({
            "datetime": str(row["datetime"]),
            "open": float(row["open"]),
            "high": float(row["high"]),
            "low": float(row["low"]),
            "close": float(row["close"]),
            "volume": int(row["volume"])
        })

    return jsonify(records)


@app.route('/api/fundamentals')
def fundamentals():
    symbol = request.args.get('symbol')
    if not symbol:
        return jsonify({"error":"symbol required"}),400
    data = fetch_fundamentals(symbol)
    return jsonify(data)

@app.route('/api/indicators', methods=['POST'])
def indicators():
    body = request.json or {}
    symbol = body.get('symbol')
    timeframe = body.get('timeframe','5m')
    if not symbol:
        return jsonify({"error":"symbol required"}),400
    df = get_intraday_series(symbol, timeframe)
    indicators = compute_indicators(df)
    return jsonify(indicators)

@app.route('/api/scan', methods=['POST'])
def scan():
    body = request.json or {}
    universe = body.get('universe', ['RELIANCE.NS','ICICIBANK.NS','TATAMOTORS.NS'])
    results = scan_universe(universe)
    return jsonify(results)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
    
from datetime import datetime

trade_log = []

@app.route('/api/trade', methods=['POST'])
def trade():
    data = request.json

    trade = {
        "id": len(trade_log) + 1,
        "symbol": data.get("symbol"),
        "side": data.get("side"),
        "qty": data.get("qty"),
        "sl": data.get("sl"),
        "tp": data.get("tp"),
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    trade_log.append(trade)

    return jsonify({
        "status": "success",
        "trade": trade
    })
@app.route('/api/trades', methods=['GET'])
def trades():
    return jsonify(trade_log)
