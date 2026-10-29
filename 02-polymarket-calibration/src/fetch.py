"""Builds the calibration dataset from Polymarket's public APIs. No API key needed.

For each tag I take the biggest closed Yes/No markets by money traded, then:
  1. read who won from the market's final prices (1 and 0),
  2. download the YES price history once,
  3. look up the YES price 30, 7 and 1 day before the market ended.

Usage (from the project folder):
    python src/fetch.py --per-tag 500
Writes data/markets.csv (one row per market and horizon). Every API response is
cached in data/cache/, so running it again doesn't hit the API.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path

import pandas as pd
import requests

GAMMA = "https://gamma-api.polymarket.com"
DATA = "https://data-api.polymarket.com"
HORIZONS_DAYS = [30, 7, 1]
# most specific first, so a Fed market lands in economy rather than politics
TAG_SLUGS = ["economy", "crypto", "sports", "politics"]

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "data" / "cache"
CACHE.mkdir(parents=True, exist_ok=True)
session = requests.Session()


def get(url: str, params: dict | None = None, retries: int = 5):
    key = hashlib.sha1((url + json.dumps(params or {}, sort_keys=True)).encode()).hexdigest()
    path = CACHE / f"{key}.json"
    if path.exists():
        return json.loads(path.read_text())
    for attempt in range(retries):
        try:
            r = session.get(url, params=params, timeout=30)
        except requests.RequestException:
            time.sleep(2 ** attempt)
            continue
        if r.status_code == 429 or r.status_code >= 500:
            time.sleep(2 ** attempt)
            continue
        r.raise_for_status()
        body = r.json()
        path.write_text(json.dumps(body))
        time.sleep(0.1)  # be polite
        return body
    raise RuntimeError(f"gave up on {url} {params}")


def as_list(v):
    return json.loads(v) if isinstance(v, str) else (v or [])


def biggest_closed_markets(tag_id: str, wanted: int) -> list[dict]:
    """Closed Yes/No markets for one tag, biggest first, that resolved cleanly to 1 and 0."""
    out, offset = [], 0
    while len(out) < wanted:
        page = get(f"{GAMMA}/markets", {"closed": "true", "tag_id": tag_id, "limit": 100, "offset": offset,
                                         "order": "volumeNum", "ascending": "false"})
        if not page:
            break
        for m in page:
            prices = [float(p) for p in as_list(m.get("outcomePrices"))]
            if as_list(m.get("outcomes")) != ["Yes", "No"] or sorted(prices) != [0.0, 1.0]:
                continue  # not Yes/No, or not settled cleanly (e.g. refunded at 50/50)
            tokens = as_list(m.get("clobTokenIds"))
            if len(tokens) != 2:
                continue
            m["_yes_token"], m["_yes_won"] = tokens[0], int(prices[0] == 1.0)
            out.append(m)
        offset += 100
    return out[:wanted]


def history(token: str) -> pd.Series:
    body = get(f"{DATA}/v2/prices-history", {"token_id": token, "interval": "max"})
    pts = body.get("data", [])
    while body.get("pagination", {}).get("has_more"):
        body = get(f"{DATA}/v2/prices-history", {"token_id": token, "cursor": body["pagination"]["next_cursor"]})
        pts += body.get("data", [])
    # drop the settlement point itself, it's the answer, not a forecast
    pts = [p for p in pts if p.get("resolution_seconds") != 0]
    return pd.Series({int(p["timestamp"]): float(p["price"]) for p in pts}).sort_index()


def end_time(m: dict) -> pd.Timestamp | None:
    """When the question was settled: the earlier of the planned end date and when it closed."""
    times = [pd.to_datetime(m.get(k), utc=True, errors="coerce") for k in ("endDate", "closedTime")]
    times = [t for t in times if pd.notna(t)]
    return min(times) if times else None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--per-tag", type=int, default=500)
    args = ap.parse_args()

    rows, seen = [], set()
    for slug in TAG_SLUGS:
        tag_id = get(f"{GAMMA}/tags/slug/{slug}")["id"]
        markets = [m for m in biggest_closed_markets(tag_id, args.per_tag) if m["id"] not in seen]
        print(f"{slug}: {len(markets)} markets")
        for i, m in enumerate(markets, 1):
            seen.add(m["id"])
            end = end_time(m)
            if end is None:
                continue
            h = history(m["_yes_token"])
            if h.empty:
                continue
            for days in HORIZONS_DAYS:
                at = int((end - pd.Timedelta(days=days)).timestamp())
                before = h[h.index <= at]
                if before.empty:
                    continue  # the market didn't exist yet
                rows.append({
                    "market_id": m["id"],
                    "question": m.get("question"),
                    "category": slug,
                    "volume_usd": float(m.get("volumeNum") or 0),
                    "created_at": m.get("createdAt"),
                    "ended_at": end.isoformat(),
                    "horizon_days": days,
                    "price_yes": before.iloc[-1],
                    "yes_won": m["_yes_won"],
                })
            if i % 100 == 0:
                print(f"  {i}/{len(markets)}")
    df = pd.DataFrame(rows)
    out = ROOT / "data" / "markets.csv"
    df.to_csv(out, index=False)
    print(f"wrote {len(df):,} rows ({df.market_id.nunique()} markets) to {out}")


if __name__ == "__main__":
    main()
