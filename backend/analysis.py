import pandas as pd
import numpy as np
import datetime as dt

# NOTE: This module expects a data provider. For the MVP we show how to use yfinance (commented).
# If you want real-time intraday data use a paid API & replace get_intraday_series implementation below.

def get_intraday_series(symbol, timeframe='5m'):
    # \"\"\"Return a pandas DataFrame with columns: datetime, open, high, low, close, volume\"\"\"
    # Example using yfinance (uncomment if yfinance installed and internet available)
    import yfinance as yf
    period = '5d'
    interval = timeframe
    data = yf.download(symbol, period=period, interval=interval, progress=False)
    data = data.reset_index().rename(columns={'Datetime':'datetime'})
    data['datetime'] = data['Datetime'].astype(str)
    df = data[['Datetime','Open','High','Low','Close','Volume']]
    df.columns = ['datetime','open','high','low','close','volume']
    return df
    # For offline/demo: generate synthetic data for last 120 intervals
    now = dt.datetime.utcnow()
    periods = 120
    rng = pd.date_range(end=now, periods=periods, freq=timeframe.upper())
    close = (100 + np.cumsum(np.random.randn(periods))).round(2)
    open_ = close + np.random.randn(periods).round(2)
    high = np.maximum(open_, close) + np.abs(np.random.rand(periods)).round(2)
    low = np.minimum(open_, close) - np.abs(np.random.rand(periods)).round(2)
    volume = (np.random.randint(1000, 10000, size=periods)).astype(int)
    df = pd.DataFrame({
        'datetime': rng.astype(str),
        'open': open_,
        'high': high,
        'low': low,
        'close': close,
        'volume': volume
    })
    return df

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