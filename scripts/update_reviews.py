"""Fetch iAssist Repair's Google rating + review count from SerpApi and save reviews.json.

Runs daily from GitHub Actions. Keeps the last good numbers if anything looks wrong,
and exits with an error so GitHub emails the repo owner.
"""
import json
import os
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timezone

DATA_CID = "14567777598761347934"  # iAssist Repair, Silvercrest Centre (Google Maps CID)
OUT = "reviews.json"


def load_previous():
    try:
        with open(OUT) as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def fetch(api_key):
    query = urllib.parse.urlencode({"engine": "google_maps", "data_cid": DATA_CID, "hl": "en", "api_key": api_key})
    with urllib.request.urlopen(f"https://serpapi.com/search.json?{query}", timeout=60) as resp:
        data = json.load(resp)
    if data.get("error"):
        raise RuntimeError(f"SerpApi error: {data['error']}")
    place = data.get("place_results") or (data.get("local_results") or [{}])[0]
    return place.get("rating"), place.get("reviews")


def main():
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    prev = load_previous()
    out = dict(prev, checked=now)
    problem = None
    try:
        rating, count = fetch(os.environ["SERPAPI_KEY"])
        rating, count = float(rating), int(str(count).replace(",", ""))
        if not 1 <= rating <= 5 or count <= 0:
            problem = f"Unexpected numbers: rating={rating} count={count}"
        elif prev.get("count") and count < prev["count"] * 0.8:
            problem = f"Review count dropped from {prev['count']} to {count}; keeping old numbers"
        else:
            out.update(rating=round(rating, 1), count=count, updated=now)
            out.pop("last_error", None)
    except Exception as exc:  # network, bad key, layout change
        problem = f"{type(exc).__name__}: {exc}"

    if problem:
        out["last_error"] = problem
    with open(OUT, "w") as f:
        json.dump(out, f, indent=2)
        f.write("\n")
    print(json.dumps(out, indent=2))
    if problem:
        print(f"::error::{problem}")
        sys.exit(1)


if __name__ == "__main__":
    main()
