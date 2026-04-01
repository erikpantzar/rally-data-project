# Rally Data API

A FastAPI service that scrapes rally event data from [rallysimfans.hu](https://www.rallysimfans.hu) and returns structured JSON.

## Requirements

- Python 3.14+

## Setup

```bash
python -m venv .venv
.venv/bin/pip install -e ".[dev]"
```

## Run

```bash
.venv/bin/uvicorn app.main:app --reload
```

The API is available at `http://localhost:8000`.
Interactive docs: `http://localhost:8000/docs`

## Endpoints

### `GET /rally/{rally_id}`

Returns structured data for a rally event.

```bash
curl http://localhost:8000/rally/1234
```

**Response fields:**

| Field | Description |
|---|---|
| `rally_id` | Rally identifier |
| `name` | Rally name |
| `creator` | Creator username |
| `discord_url` | Discord link (if any) |
| `damage_level` | Damage setting |
| `password_protected` | Whether entry requires a password |
| `num_legs` | Number of legs |
| `super_rally` | Super rally mode enabled |
| `pacenotes` | Pacenote type |
| `started` / `finished` | Participant counts |
| `total_distance_km` | Total rally distance |
| `car_groups` | Allowed car groups |
| `legs` | List of legs, each with stages and service parks |

## Project Structure

```
app/
  main.py               # FastAPI app and route definitions
  models.py             # Pydantic models
  scrapers/
    base.py             # BaseScraper ABC
    registry.py         # Domain-keyed scraper registry
    rallysimfans.py     # rallysimfans.hu scraper implementation
```
