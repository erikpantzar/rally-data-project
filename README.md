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

## Live API

**`https://rally-api-441264299241.europe-west1.run.app`**

```bash
curl https://rally-api-441264299241.europe-west1.run.app/rally/1234
```

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

## Deployment

### Google Cloud Run

Ensure `gcloud` CLI is installed and authenticated:

```bash
gcloud auth login
gcloud config set project rally-data-project
```

Enable required APIs (first time only):

```bash
gcloud services enable run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com
```

Deploy:

```bash
gcloud run deploy rally-api --source . --region europe-west1 --allow-unauthenticated
```

Cloud Build containerizes the app automatically using the `Dockerfile` — no local Docker required. The service URL is printed at the end of the deploy.

---

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
