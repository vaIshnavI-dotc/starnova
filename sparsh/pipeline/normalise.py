"""Normalise raw tips: UTC times, ticker check, entry session. Writes data/clean/tips.parquet."""
import re
from datetime import date, timedelta

import pandas as pd

from pipeline.config import RAW, CLEAN, TICKERS, EARLIEST_TIP_DATE
from pipeline.clean_prices import entry_session

MIN_AGE_DAYS = 14  # tips newer than this can't be scored yet


def _load_calendar():
    cal = pd.read_parquet(CLEAN / "trading_calendar.parquet")
    if cal.index.name or not isinstance(cal.index, pd.RangeIndex):
        cal = cal.reset_index()
    col = next((c for c in cal.columns if "date" in str(c).lower()), cal.columns[0])
    return sorted(pd.to_datetime(cal[col]).dt.date.unique())


def _load_tips():
    df = pd.read_csv(RAW / "raw_tips.csv")
    df = df.rename(columns={"posted_at": "tip_time", "raw_text": "tip_text"})  # accept old headers
    if "tip_id" not in df:
        df.insert(0, "tip_id", [f"t{i:03d}" for i in range(1, len(df) + 1)])
    if "is_synthetic" not in df:
        df["is_synthetic"] = df.get("data_origin", "") == "synthetic"
    if "ticker" not in df:
        known = set(TICKERS)
        def find(txt):
            hits = [w for w in re.findall(r"[A-Z]+", str(txt)) if w in known]
            return hits[0] if hits else None
        df["ticker"] = df["tip_text"].map(find)
    return df


def main():
    days = _load_calendar()
    df = _load_tips()
    n_in = len(df)

    df["tip_time_utc"] = pd.to_datetime(df["tip_time"], utc=True)
    reasons = pd.Series("", index=df.index)

    reasons[~df["ticker"].isin(TICKERS)] = "ticker not in TICKERS"
    reasons[(reasons == "") & (df["tip_time_utc"].dt.date < EARLIEST_TIP_DATE)] = "before price window"
    cutoff = date.today() - timedelta(days=MIN_AGE_DAYS)
    reasons[(reasons == "") & (df["tip_time_utc"].dt.date > cutoff)] = "too recent to score"

    entries = []
    for t, r in zip(df["tip_time_utc"], reasons):
        if r:
            entries.append(None)
            continue
        entries.append(entry_session(t.tz_convert("UTC").tz_localize(None).to_pydatetime(), days))
    df["entry_date"] = entries
    reasons[(reasons == "") & df["entry_date"].isna()] = "no entry session found"

    df["reject_reason"] = reasons
    ok = df[df["reject_reason"] == ""].copy()
    bad = df[df["reject_reason"] != ""]

    CLEAN.mkdir(parents=True, exist_ok=True)
    cols = ["tip_id", "ticker", "source_id", "tip_text", "tip_time_utc", "entry_date", "is_synthetic"]
    ok[cols].to_parquet(CLEAN / "tips.parquet", index=False)

    print(f"tips in: {n_in} | accepted: {len(ok)} | rejected: {len(bad)}")
    for _, r in bad.iterrows():
        print(f"  REJECT {r['tip_id']} {r['ticker']}: {r['reject_reason']}")
    print("\nSample (tip time -> entry date):")
    show = ok.assign(dow=ok["tip_time_utc"].dt.day_name().str[:3])
    print(show[["tip_id", "ticker", "tip_time_utc", "dow", "entry_date"]].head(12).to_string(index=False))
    print("\nWeekend tips:")
    print(show[show["dow"].isin(["Sat", "Sun"])][["tip_id", "ticker", "tip_time_utc", "entry_date"]].to_string(index=False))


if __name__ == "__main__":
    main()

