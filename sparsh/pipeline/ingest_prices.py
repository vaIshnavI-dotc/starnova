"""Download and cache daily prices. Run: python -m pipeline.ingest_prices [--force]"""
import sys
import time

import pandas as pd
import yfinance as yf

from pipeline.config import BENCHMARK, END_DATE, RAW_PRICES, START_DATE, TICKERS

COLS = ["date", "open", "high", "low", "close", "adj_close", "volume", "source"]


def fetch_yf(symbol: str) -> pd.DataFrame | None:
    df = yf.download(symbol, start=START_DATE.isoformat(), end=END_DATE.isoformat(),
                     auto_adjust=False, progress=False)
    if df is None or df.empty:
        return None
    if isinstance(df.columns, pd.MultiIndex):      # newer yfinance versions
        df.columns = df.columns.get_level_values(0)
    df = df.reset_index().rename(columns={
        "Date": "date", "Open": "open", "High": "high", "Low": "low",
        "Close": "close", "Adj Close": "adj_close", "Volume": "volume"})
    df["source"] = "yfinance"
    return df[COLS]


def fetch_jugaad(symbol: str) -> pd.DataFrame | None:
    """Fallback. NOTE: unadjusted prices, so splits and bonuses are NOT handled."""
    from jugaad_data.nse import stock_df
    df = stock_df(symbol=symbol, from_date=START_DATE, to_date=END_DATE, series="EQ")
    if df is None or df.empty:
        return None
    df = df.rename(columns={"DATE": "date", "OPEN": "open", "HIGH": "high",
                            "LOW": "low", "CLOSE": "close", "VOLUME": "volume"})
    df["adj_close"] = df["close"]
    df["source"] = "jugaad_unadjusted"
    return df[COLS].sort_values("date")


def fetch(symbol: str, yahoo_symbol: str) -> pd.DataFrame | None:
    try:
        df = fetch_yf(yahoo_symbol)
        if df is not None:
            return df
    except Exception as e:
        print(f"  yfinance failed for {symbol}: {e}")
    if yahoo_symbol.startswith("^"):               # index: no fallback
        return None
    try:
        return fetch_jugaad(symbol)
    except Exception as e:
        print(f"  jugaad failed for {symbol}: {e}")
        return None


def main(force: bool = False) -> None:
    RAW_PRICES.mkdir(parents=True, exist_ok=True)
    jobs = [("NIFTY", BENCHMARK)] + [(t, f"{t}.NS") for t in TICKERS]
    failed = []
    for name, ysym in jobs:
        out = RAW_PRICES / f"{name}.parquet"
        if out.exists() and not force:
            print(f"skip {name} (cached)")
            continue
        print(f"fetching {name} ...")
        df = fetch(name, ysym)
        if df is None or df.empty:
            failed.append(name)
            continue
        df["date"] = pd.to_datetime(df["date"]).dt.tz_localize(None)
        df.to_parquet(out, index=False)
        print(f"  saved {len(df)} rows ({df['source'].iloc[0]})")
        time.sleep(0.5)                            # be gentle with rate limits
    print("\nDone.")
    if failed:
        print("FAILED (check symbol or retry):", ", ".join(failed))
        (RAW_PRICES / "_failed.txt").write_text("\n".join(failed))


if __name__ == "__main__":
    main(force="--force" in sys.argv)