from flask import Flask, request, jsonify
from analysis import get_intraday_series, compute_indicators, fetch_fundamentals, scan_universe
import os

app = Flask(__name__)

@app.route('/api/quote')
def quote():
    symbol = request.args.get('symbol')
    timeframe = request.args.get('timeframe', '5m')
    if not symbol:
        return jsonify({"error":"symbol required"}),400
    df = get_intraday_series(symbol, timeframe)
    return jsonify(df.to_dict(orient='records'))

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