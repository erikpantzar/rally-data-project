from fastapi import FastAPI, HTTPException
import httpx

import app.scrapers.rallysimfans  # noqa: F401 — triggers @register decorator
from app.scrapers.registry import get_scraper
from app.models import RallyDetail

app = FastAPI(title="Rally Data API")

_BASE_URL = (
    "https://www.rallysimfans.hu/rbr/rally_online.php"
    "?centerbox=rally_list_details.php&rally_id={rally_id}"
)


@app.get("/rally/{rally_id}", response_model=RallyDetail)
async def get_rally(rally_id: str):
    url = _BASE_URL.format(rally_id=rally_id)
    scraper = get_scraper(url)
    try:
        data = await scraper.scrape(url)
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=502, detail=f"Upstream returned {e.response.status_code}")
    except httpx.RequestError as e:
        raise HTTPException(status_code=504, detail=f"Upstream unreachable: {e}")
    return data
