from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
RAW_PRICES = RAW / "prices_raw"
FROZEN = ROOT / "data" / "frozen" / "v1"
CLEAN = ROOT / "data" / "clean"
DB_PATH = ROOT / "data" / "db" / "app.sqlite"

BENCHMARK = "^NSEI"          # Nifty 50 on Yahoo
COST_PCT = 0.2               # ASSUMPTION: brokerage + STT per round trip, shown in /meta
ENTRY_RULE = "next_session_open"   # see docs/entry_rule.md

# Price window: start 60 days before the earliest tip so volume baselines work
EARLIEST_TIP_DATE = date(2025, 6, 1)      # CHANGE to your earliest tip
START_DATE = EARLIEST_TIP_DATE - timedelta(days=60)
END_DATE = date.today()

# Starter universe. Add tickers that appear in your tips later.
TICKERS = [
    "RELIANCE", "TCS", "HDFCBANK", "INFY", "ICICIBANK", "SBIN", "ITC", "LT",
    "AXISBANK", "KOTAKBANK", "BHARTIARTL", "HINDUNILVR", "MARUTI", "SUNPHARMA",
    "TATAMOTORS", "TATASTEEL", "WIPRO", "ADANIENT", "ADANIPORTS", "ONGC",
    "NTPC", "POWERGRID", "COALINDIA", "BAJFINANCE", "ASIANPAINT", "TITAN",
    "ZOMATO", "PAYTM", "IRFC", "YESBANK", "SUZLON", "IDEA", "RPOWER",
    "JPPOWER", "HFCL", "NHPC", "SAIL", "PNB", "IDFCFIRSTB", "TRIDENT",
]