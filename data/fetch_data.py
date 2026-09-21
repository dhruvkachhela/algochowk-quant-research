"""
NIFTY 50 Historical Data Fetcher
Downloads daily OHLCV from 2007 to present from Yahoo Finance chart API.
"""

import os
import json
import urllib.request
import pandas as pd
from datetime import datetime

DATA_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_FILE = os.path.join(DATA_DIR, "nifty50_daily.csv")

def fetch_nifty_data(start_year: int = 2007) -> pd.DataFrame:
    """
    Fetches daily OHLCV data for NIFTY 50 (^NSEI) from start_year to current date.
    """
    start_ts = int(datetime(start_year, 1, 1).timestamp())
    end_ts = int(datetime(2026, 9, 21, 23, 59, 59).timestamp())
    
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/%5ENSEI?interval=1d&period1={start_ts}&period2={end_ts}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode())
    
    result = data["chart"]["result"][0]
    timestamps = result["timestamp"]
    quote = result["indicators"]["quote"][0]
    
    df = pd.DataFrame({
        "Date": [datetime.fromtimestamp(ts).strftime("%Y-%m-%d") for ts in timestamps],
        "Open": quote["open"],
        "High": quote["high"],
        "Low": quote["low"],
        "Close": quote["close"],
        "Volume": quote["volume"]
    })
    
    # Drop rows with null close values (market holidays with empty entries)
    df = df.dropna(subset=["Close", "Open", "High", "Low"]).reset_index(drop=True)
    
    # Save to CSV
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"[OK] Downloaded {len(df)} trading days of NIFTY data (from {df['Date'].iloc[0]} to {df['Date'].iloc[-1]})")
    print(f"[OK] Saved to: {OUTPUT_FILE}")
    return df

if __name__ == "__main__":
    fetch_nifty_data()
