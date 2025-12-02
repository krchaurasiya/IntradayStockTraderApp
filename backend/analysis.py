import pandas as pd
import numpy as np
import datetime as dt

import yfinance as yf
import pandas as pd

def get_intraday_series(symbol, timeframe='5m'):
    period_map = {
        '1m': '1d',
        '5m': '5d',
        '15m': '5d',
        '30m': '1mo',
        '1h': '2mo'
    }

    interval = timeframe
    period = period_map.get(timeframe, '5d')

    data = yf.download(symbol, period=period, interval=interval, progress=False, auto_adjust=False)


    # ✅ FIX 1: Flatten MultiIndex columns if present
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = [col[0] for col in data.columns]

    # ✅ FIX 2: Move index into a real column
    data.reset_index(inplace=True)

    # ✅ FIX 3: Safely detect datetime column
    if 'Datetime' in data.columns:
        data['datetime'] = data['Datetime'].astype(str)
    elif 'Date' in data.columns:
        data['datetime'] = data['Date'].astype(str)
    else:
        raise Exception("No datetime column found in yfinance data")

    # ✅ FIX 4: Rename for frontend
    data.rename(columns={
        'Open': 'open',
        'High': 'high',
        'Low': 'low',
        'Close': 'close',
        'Volume': 'volume'
    }, inplace=True)

    # ✅ FIX 5: Select only clean JSON-safe columns
    data = data[['datetime', 'open', 'high', 'low', 'close', 'volume']]
    data = data.dropna()

    return data



def sma(series, period):
    return series.rolling(period).mean()

def ema(series, period):
    return series.ewm(span=period, adjust=False).mean()

def rsi(series, period=14):
    delta = series.diff()
    up = delta.clip(lower=0)
    down = -1*delta.clip(upper=0)
    ma_up = up.ewm(alpha=1/period, adjust=False).mean()
    ma_down = down.ewm(alpha=1/period, adjust=False).mean()
    rs = ma_up / ma_down.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))
    return rsi.fillna(50)

def macd(series, fast=12, slow=26, signal=9):
    ema_fast = series.ewm(span=fast, adjust=False).mean()
    ema_slow = series.ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    hist = macd_line - signal_line
    return macd_line, signal_line, hist

def detect_volume_spike(df, multiplier=2):
    avg_vol = df['volume'].rolling(window=20, min_periods=1).mean()
    spike = df['volume'] > (avg_vol * multiplier)
    return spike

def compute_indicators(df):
    df2 = df.copy()
    df2['close'] = pd.to_numeric(df2['close'])
    df2['ma5'] = ema(df2['close'], 5)
    df2['ma20'] = ema(df2['close'], 20)
    df2['rsi'] = rsi(df2['close'], 14)
    macd_line, signal_line, hist = macd(df2['close'])
    df2['macd'] = macd_line
    df2['macd_signal'] = signal_line
    df2['vol_spike'] = detect_volume_spike(df2).astype(int)
    latest = df2.tail(1).to_dict(orient='records')[0]
    return {
        'latest': latest,
        'summary': {
            'ma5_above_ma20': bool(df2['ma5'].iloc[-1] > df2['ma20'].iloc[-1]),
            'rsi': float(df2['rsi'].iloc[-1]),
            'vol_spike': bool(df2['vol_spike'].iloc[-1])
        }
    }

def fetch_fundamentals(symbol):
    # Placeholder: ideally use a fundamentals API. Return sample structure.
    return {
        'symbol': symbol,
        'pe_ratio': None,
        'eps': None,
        'revenue_growth': None,
        'last_earnings_date': None,
        'note': 'This is a placeholder. Replace with real API (eg. Alpha Vantage, FinancialModelingPrep).'
    }

def scan_universe(universe):
    results = []
    for s in universe:
        df = get_intraday_series(s, '5m')
        ind = compute_indicators(df)
        score = 0
        if ind['summary']['ma5_above_ma20']:
            score += 1
        if ind['summary']['rsi'] < 75 and ind['summary']['rsi'] > 30:
            score += 1
        if ind['summary']['vol_spike']:
            score += 1
        results.append({'symbol': s, 'score': score, 'indicators': ind['summary']})
    results = sorted(results, key=lambda x: x['score'], reverse=True)
    return results