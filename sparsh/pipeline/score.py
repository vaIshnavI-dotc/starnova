"""Score tips against real prices. Reads data/clean/tips.parquet + prices.parquet, writes scored.parquet."""
import re

import numpy as np
import pandas as pd

from pipeline.config import CLEAN, COST_PCT

DEFAULT_HORIZON = 10  # trading days when the tip gives none
NUM = r"(\d+(?:\.\d+)?)"


# ---------- parsing ----------
def parse_tip(text):
    t = str(text).lower()
    d = {"direction": "buy", "target": None, "stop": None, "horizon": DEFAULT_HORIZON}

    if re.search(r"\b(avoid|watch only|wait for|no fresh buy|no buy)\b", t):
        d["direction"] = "neutral"
    elif re.search(r"\b(sell|short)\b", t):
        d["direction"] = "sell"

    m = re.search(r"target\s*" + NUM, t)                       # target 480
    if not m:
        m = re.search(NUM + r"\s*target\b(?!\s*in\b)", t)      # 800 target buy (not "3400 target in 10 days")
    if not m:
        m = re.search(NUM + r"\s*(?:paar|tak|tk|jayega|upar)", t)  # 25 paar jayega
    if m:
        d["target"] = float(m.group(1))

    m = re.search(r"(?:stop\s*loss|stoploss|sl|stop)\s*" + NUM, t)
    if m:
        d["stop"] = float(m.group(1))

    m = re.search(r"(\d+)(?:\s*-\s*(\d+))?\s*(week|hafte|day|month|mahine)", t)
    if m:
        n = int(m.group(2) or m.group(1))
        d["horizon"] = n * {"week": 5, "hafte": 5, "day": 1, "month": 21, "mahine": 21}[m.group(3)]
    elif re.search(r"this week|is hafte|this month|is mahine", t):
        d["horizon"] = 5 if re.search(r"week|hafte", t) else 21
    elif "positional" in t:
        d["horizon"] = 20
    return d


# ---------- prices ----------
def load_prices():
    p = pd.read_parquet(CLEAN / "prices.parquet")
    if not isinstance(p.index, pd.RangeIndex):
        p = p.reset_index()
    p.columns = [str(c).lower() for c in p.columns]
    need = {"ticker", "date", "open", "high", "low", "close"}
    if not need.issubset(p.columns):
        raise SystemExit(f"prices.parquet columns are {list(p.columns)}; need {sorted(need)}. Paste this line to Claude.")
    p["date"] = pd.to_datetime(p["date"]).dt.date
    return {k: g.sort_values("date").reset_index(drop=True) for k, g in p.groupby("ticker")}


# ---------- scoring ----------
def score_one(tip, d, px):
    sign = 1 if d["direction"] == "buy" else -1
    if px is None:
        return dict(outcome="unscorable", reason="no price data")
    win = px[px["date"] >= tip.entry_date].head(d["horizon"])
    if win.empty:
        return dict(outcome="unscorable", reason="no prices after entry")
    entry = float(win.iloc[0]["open"])
    tgt, stp = d["target"], d["stop"]
    if (tgt - entry) * sign <= 0:
        return dict(outcome="unscorable", reason="target on wrong side of entry price", entry_price=entry)
    if stp is not None and (entry - stp) * sign <= 0:
        stp = None  # stop on wrong side of entry: ignore it

    exit_price, outcome, exit_date = None, "expired", None
    for _, r in win.iterrows():
        o, h, l = r["open"], r["high"], r["low"]
        hit_t = (h >= tgt) if sign == 1 else (l <= tgt)
        hit_s = stp is not None and ((l <= stp) if sign == 1 else (h >= stp))
        if hit_s:                       # stop checked first: conservative when both hit same day
            exit_price = min(o, stp) if sign == 1 else max(o, stp)
            outcome, exit_date = "stopped", r["date"]; break
        if hit_t:
            exit_price = max(o, tgt) if sign == 1 else min(o, tgt)
            outcome, exit_date = "hit", r["date"]; break
    if exit_price is None:
        exit_price, exit_date = float(win.iloc[-1]["close"]), win.iloc[-1]["date"]
    ret = sign * (exit_price - entry) / entry * 100 - COST_PCT
    return dict(outcome=outcome, entry_price=entry, exit_price=float(exit_price),
                exit_date=exit_date, net_return_pct=round(ret, 2), reason="")


def main():
    tips = pd.read_parquet(CLEAN / "tips.parquet")
    prices = load_prices()
    rows = []
    for tip in tips.itertuples():
        d = parse_tip(tip.tip_text)
        base = dict(tip_id=tip.tip_id, ticker=tip.ticker, source_id=tip.source_id,
                    direction=d["direction"], target=d["target"], stop=d["stop"], horizon_days=d["horizon"],
                    is_synthetic=tip.is_synthetic)
        if d["direction"] == "neutral":
            res = dict(outcome="unscorable", reason="neutral call")
        elif d["target"] is None:
            res = dict(outcome="unscorable", reason="no target found")
        else:
            res = score_one(tip, d, prices.get(tip.ticker))
        rows.append({**base, **res})
    out = pd.DataFrame(rows)
    out.to_parquet(CLEAN / "scored.parquet", index=False)

    sc = out[out.outcome != "unscorable"]
    print(f"tips: {len(out)} | scored: {len(sc)} | unscorable: {len(out) - len(sc)}")
    print(out[out.outcome == "unscorable"].reason.value_counts().to_string(), "\n")
    print(sc.outcome.value_counts().to_string(), "\n")
    g = sc.groupby("source_id").agg(n=("tip_id", "count"),
                                    hit_rate=("outcome", lambda s: round((s == "hit").mean(), 2)),
                                    avg_net_ret_pct=("net_return_pct", "mean")).round(2)
    print(g.to_string())


if __name__ == "__main__":
    main()

