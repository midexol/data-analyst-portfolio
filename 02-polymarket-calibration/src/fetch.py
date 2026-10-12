"""Build the calibration dataset from Polymarket's public APIs (no API key).

For each resolved binary market:
  1. list it from the Gamma API (question, YES/NO token ids, volume, tag);
  2. read the YES token's price history from the Data API v2 -- the last point of
     a resolved market is its on-chain settlement (1 = YES won, 0 = NO won), which
     gives the outcome and the resolution time;
  3. take the YES price 30, 7 and 1 day(s) before resolution.

Usage:
    python src/fetch.py --per-tag 150
Writes data/markets.parquet (one row per market x horizon). Responses are cached
in data/cache/ so a re-run does not hit the API again.
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
TAG_SLUGS = ["politics", "sports", "crypto", "economy"]

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "data" / "cache"
CACHE.mkdir(parents=True, exist_ok=True)
session = requests.Session()


def get(url: str, params: dict | None = None, retries: int = 4) -> dict:
    key = hashlib.sha1((url + json.dumps(params or {}, sort_keys=True)).encode()).hexdigest()
    path = CACHE / f"{key}.json"
    if path.exists():
        return json.loads(path.read_text())
    for attempt in range(retries):
        r = session.get(url, params=params, timeout=30)
        if r.status_code == 429 or r.status_code >= 500:
            time.sleep(2 ** attempt)
            continue
        r.raise_for_status()
        body = r.json()
        path.write_text(json.dumps(body))
        time.sleep(0.15)  # be polite
        return body
    r.raise_for_status()
    return {}


def tag_id(slug: str) -> int | None:
    try:
        return get(f"{GAMMA}/tags/slug/{slug}").get("id")
    except requests.HTTPError:
        return None


def closed_markets(tag: int, wanted: int) -> list[dict]:
    """Page through closed markets for one tag until `wanted` binary ones are found."""
    out: list[dict] = []
    cursor = None
    while len(out) < wanted:
        params = {"closed": "true", "limit": 100, "tag_id": tag}
        if cursor:
            params["after_cursor"] = cursor
        page = get(f"{GAMMA}/markets/keyset", params)
        markets = page.get("markets", page if isinstance(page, list) else [])
        for m in markets:
            ids = m.get("clobTokenIds")
            ids = json.loads(ids) if isinstance(ids, str) else ids
            if ids and len(ids) == 2:
                m["_yes_token"] = ids[0]
                out.append(m)
        cursor = page.get("next_cursor") if isinstance(page, dict) else None
        if not cursor or not markets:
            break
    return out[:wanted]


def settlement(token: str) -> tuple[int, float] | None:
    """(resolution_ts, payout) from the final settlement point, or None if unresolved."""
    body = get(f"{DATA}/v2/prices-history", {"token_id": token, "interval": "max"})
    points = body.get("data", [])
    while body.get("pagination", {}).get("has_more"):
        body = get(f"{DATA}/v2/prices-history",
                   {"token_id": token, "cursor": body["pagination"]["next_cursor"]})
        points += body.get("data", [])
    if not points:
        return None
    last = points[-1]
    if last.get("resolution_seconds") != 0 or last["price"] not in (0, 1, 0.0, 1.0):
        return None  # no settlement point: not cleanly resolved
    return int(last["timestamp"]), float(last["price"])


def price_as_of(token: str, ts: int) -> float | None:
    body = get(f"{DATA}/v2/prices-history", {"token_id": token, "as_of": ts})
    pts = body.get("data", [])
    return float(pts[-1]["price"]) if pts else None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--per-tag", type=int, default=150)
    args = ap.parse_args()

    rows = []
    for slug in TAG_SLUGS:
        tid = tag_id(slug)
        if tid is None:
            print(f"skip tag {slug}: not found")
            continue
        markets = closed_markets(tid, args.per_tag)
        print(f"{slug}: {len(markets)} closed binary markets")
        for m in markets:
            token = m["_yes_token"]
            res = settlement(token)
            if res is None:
                continue
            resolved_at, outcome = res
            for h in HORIZONS_DAYS:
                p = price_as_of(token, resolved_at - h * 86400)
                if p is None:
                    continue
                rows.append({
                    "market_id": m.get("id"),
                    "question": m.get("question"),
                    "category": slug,
                    "volume": pd.to_numeric(m.get("volumeNum", m.get("volume")), errors="coerce"),
                    "liquidity": pd.to_numeric(m.get("liquidityNum", m.get("liquidity")), errors="coerce"),
                    "resolved_at": pd.to_datetime(resolved_at, unit="s", utc=True),
                    "horizon_days": h,
                    "price_yes": p,
                    "outcome_yes": int(outcome),
                })
    df = pd.DataFrame(rows)
    out = ROOT / "data" / "markets.parquet"
    df.to_parquet(out, index=False)
    print(f"wrote {len(df):,} rows ({df.market_id.nunique() if len(df) else 0} markets) to {out}")


if __name__ == "__main__":
    main()
