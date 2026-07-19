# lane-swimming

Upcoming lane-swim times for a handful of Toronto pools, on one static page.

## How it works

- `scripts/pool_schedule.py` pulls the city's open schedule JSON
  (`toronto.ca/data/parks/live/...`) for the pools listed at the top of the
  script and writes `web/lane_swim_times.json`.
- A GitHub Action (`.github/workflows/update-schedule.yml`) runs it daily at
  11:00 Toronto time and commits the refreshed JSON when it changes.
- Cloudflare Pages serves the `web/` directory at `swim.mikelaskey.ca`,
  redeploying automatically on every push (including the bot's commits).

No server anywhere: the schedule refresh lives in the Actions tab, and hosting
is the same Cloudflare Pages pattern as the `mikelaskey.ca` landing page.

## Pages settings

Connected git repo, production branch `main`, no build command, build output
directory `web`.

## Local development

```sh
uv sync
uv run scripts/pool_schedule.py   # writes web/lane_swim_times.json
python -m http.server -d web      # preview at localhost:8000
```

To add or remove a pool, edit the `pools` list in `scripts/pool_schedule.py`
(the number is the location ID from toronto.ca's parks pages).
