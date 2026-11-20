"""Clean raw prices and define the entry rule.
Run: python -m pipeline.clean_prices
"""
from bisect import bisect_right
from datetime import date, datetime, time, timedelta, timezone

import numpy as np
import pandas as pd

from pipeline.config import CLEAN, RAW_PRICES

IST_OFFSET = timedelta(hours=5, minutes=30)
MARKET_OPEN = time(9, 15)       # NSE regular session opens 09:15 IST


def entry_session(posted_at: datetime, trading_days: list[date]) -> date | None:
    """ENTRY RULE (no look-ahead): the tip is acted on at the OPEN of
    - the same day, if posted on a trading day BEFORE 09:15 IST
    - otherwise the next trading day.
    Tips posted during market hours also use the next open (conservative).
    Returns None if no later trading day exists in the data.
    """
    if posted_at.tzinfo is not None:
        posted_at = posted_at.astimezone(timezone.utc).replace(tzinfo=None)
    ist = posted_at + IST_OFFSET
    d = ist.date()
    if d in set(trading_days) and ist.time() < MARKET_OPEN:
        return d
    i = bisect_right(trading_days, d)          # first trading day strictly after d
    return trading_days[i] if i < len(trading_days) else None


def load_raw() -> pd.DataFrame:
    frames = []
    for p in sorted(RAW_PRICES.glob("*.parquet")):
        if p.stem == "NIFTY":
            continue
        df = pd.read_parquet(p)
        df["ticker"] = p.stem
        frames.append(df)
    return pd.concat(frames, ignore_index=True)


def clean(df: pd.DataFrame) -> pd.DataFrame:
    df = df.drop_duplicates(["ticker", "date"]).sort_values(["ticker", "date"]).copy()
    df["date"] = pd.to_datetime(df["date"]).dt.normalize()
    # a row is usable only if prices are present and positive
    df["valid"] = df[["open", "close", "adj_close"]].notna().all(axis=1) & (df["close"] > 0)
    # adjust OHLC by the same factor as adj_close so splits/bonuses don't fake moves
    factor = (df["adj_close"] / df["close"]).where(df["valid"])
    for c in ["open", "high", "low", "close"]:
        df[f"adj_{c}"] = df[c] * factor
    # volume baseline uses PREVIOUS days only (shift 1), so today's spike isn't in its own baseline
    g = df.groupby("ticker")["volume"]
    df["vol_mean_30"] = g.transform(lambda s: s.shift(1).rolling(30, min_periods=20).mean())
    df["vol_std_30"] = g.transform(lambda s: s.shift(1).rolling(30, min_periods=20).std())
    df["volume_z"] = (df["volume"] - df["vol_mean_30"]) / df["vol_std_30"].replace(0, np.nan)
    return df


def main() -> None:
    CLEAN.mkdir(parents=True, exist_ok=True)

    nifty = pd.read_parquet(RAW_PRICES / "NIFTY.parquet")
    nifty["date"] = pd.to_datetime(nifty["date"]).dt.normalize()
    nifty = nifty.drop_duplicates("date").sort_values("date")
    nifty.to_parquet(CLEAN / "nifty.parquet", index=False)

    # exchange calendar = days the Nifty traded
    cal = pd.DataFrame({"date": nifty["date"].dt.date.unique()})
    cal.to_parquet(CLEAN / "trading_calendar.parquet", index=False)

    prices = clean(load_raw())
    prices.to_parquet(CLEAN / "prices.parquet", index=False)

    print(f"tickers: {prices['ticker'].nunique()}  rows: {len(prices)}")
    print(f"date range: {prices['date'].min().date()} to {prices['date'].max().date()}")
    print(f"invalid rows: {(~prices['valid']).sum()}")
    print(f"trading days in calendar: {len(cal)}")
    unadj = prices.loc[prices["source"] != "yfinance", "ticker"].unique()
    if len(unadj):
        print("WARNING unadjusted source (splits not handled):", list(unadj))


if __name__ == "__main__":
    main()