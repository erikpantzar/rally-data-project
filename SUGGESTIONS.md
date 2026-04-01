# Suggestions & Potential Improvements

## New Endpoints

- **`GET /rally/{rally_id}/results`** — Scrape the results page (`?centerbox=rally_results.php&rally_id={id}`). Return per-driver stage times and overall standings. The URL pattern is already known.
- **`GET /rally/{rally_id}/stages/{stage_number}`** — Return a single stage's details, useful for clients that only need one stage at a time.
- **`GET /rallies`** — Scrape the rally listing page to return a paginated list of available rallies (ID, name, date, status).
- **`GET /championship/{championship_id}`** — If RSF exposes championship pages, aggregate multiple rally results into a season standings view.

## Caching

- Add an in-memory or Redis cache (e.g. via `fastapi-cache2`) on `GET /rally/{rally_id}`. Rally data rarely changes mid-event, so a TTL of 5–15 minutes would cut upstream requests significantly and make the API much faster for repeated queries.

## Background Polling / Webhooks

- Add a background task that polls active rallies on a schedule and pushes updates to a webhook URL. Useful for Discord bots or dashboards that want live stage results without polling the API themselves.

## Data Persistence

- Store scraped results in SQLite (via SQLModel or SQLAlchemy) so historical data survives restarts and doesn't require re-scraping past events.
- Expose a `GET /rally/{rally_id}/history` endpoint for cached historical snapshots.

## Error Handling & Observability

- Return structured error bodies (error code + message) instead of plain `detail` strings.
- Add request logging with `rally_id` and upstream response time so slow or failing scrapes are easy to spot.
- Expose a `GET /health` endpoint that checks upstream reachability.

## Developer Experience

- Add a `Makefile` with targets: `make run`, `make test`, `make lint`.
- Add `pytest` tests with a fixture that serves a saved HTML snapshot so tests don't hit the live site.
- Add a `Dockerfile` for easy containerised deployment.

## Data Quality

- Parse leg dates into proper `datetime` objects (currently stored as raw strings).
- Normalise surface values (`"Gravel"`, `"gravel"`, `"GRAVEL"`) to a consistent enum.
- Validate `discord_url` as an actual URL before returning it (some entries may have malformed links).
