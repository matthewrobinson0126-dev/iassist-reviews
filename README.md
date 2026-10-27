# iassist-reviews

Keeps the Google rating and review count for the "★★★★★ 4.9 · 250 Google reviews" badge on
https://iassist.net.za up to date.

- `scripts/update_reviews.py` asks SerpApi (free plan) for the numbers once a day.
- `.github/workflows/update-reviews.yml` runs it every day at 06:00 SAST and saves `reviews.json`.
- GitHub Pages publishes `reviews.json`; the badge on the homepage reads it.
- If a check fails, the old numbers stay and GitHub emails the repo owner.

Secret needed: `SERPAPI_KEY` (Settings → Secrets and variables → Actions).
