from __future__ import annotations
import re
import httpx
from bs4 import BeautifulSoup, Tag

from app.scrapers.base import BaseScraper
from app.scrapers.registry import register
from app.models import RallyDetail, RallyLeg, RallyStage, ServicePark

BROWSER_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.rallysimfans.hu/rbr/rally_online.php",
}


@register("rallysimfans.hu")
class RallySimFansScraper(BaseScraper):

    async def fetch(self, url: str) -> str:
        async with httpx.AsyncClient(follow_redirects=True, timeout=30) as client:
            r = await client.get(url, headers=BROWSER_HEADERS)
            r.raise_for_status()
            return r.text

    def parse(self, html: str, url: str) -> dict:
        soup = BeautifulSoup(html, "lxml")
        m = re.search(r"rally_id=(\w+)", url)
        rally_id = m.group(1) if m else "unknown"

        info = self._parse_info_table(soup)
        leg_dates = info.pop("leg_dates", {})
        legs = self._parse_stages_table(soup, leg_dates)

        return RallyDetail(rally_id=rally_id, legs=legs, **info).model_dump()

    # ------------------------------------------------------------------
    # Info table
    # ------------------------------------------------------------------

    def _parse_info_table(self, soup: BeautifulSoup) -> dict:
        result: dict = {
            "name": None,
            "creator": None,
            "discord_url": None,
            "damage_level": None,
            "password_protected": False,
            "num_legs": None,
            "super_rally": False,
            "pacenotes": None,
            "started": None,
            "finished": None,
            "total_distance_km": None,
            "car_groups": [],
            "leg_dates": {},
        }

        # Find the exact table that directly contains the rally name header row
        fejlec = soup.find("tr", class_="fejlec")
        if not fejlec:
            return result
        info_table = fejlec.parent
        if fejlec:
            result["name"] = fejlec.get_text(strip=True)

        for row in info_table.find_all("tr"):
            cells = row.find_all("td")
            if len(cells) < 2:
                continue
            label = cells[0].get_text(strip=True).lower().rstrip(":")
            value_cell = cells[1]
            value_text = value_cell.get_text(strip=True)

            if "description" in label:
                a = value_cell.find("a")
                if a:
                    result["discord_url"] = a.get("href")
            elif "creator" in label:
                result["creator"] = value_text
            elif "damage" in label:
                result["damage_level"] = value_text
            elif "password" in label:
                result["password_protected"] = value_text.lower() == "yes"
            elif "number of legs" in label:
                try:
                    result["num_legs"] = int(value_text)
                except ValueError:
                    pass
            elif "super" in label and "rally" in label:
                result["super_rally"] = value_text.lower() == "yes"
            elif "pacenotes" in label:
                result["pacenotes"] = value_text
            elif "started" in label and "finished" in label:
                parts = value_text.split("/")
                if len(parts) == 2:
                    try:
                        result["started"] = int(parts[0].strip())
                        result["finished"] = int(parts[1].strip())
                    except ValueError:
                        pass
            elif "total distance" in label:
                result["total_distance_km"] = self._parse_km(value_text)
            elif "car group" in label:
                result["car_groups"] = [g.strip() for g in value_text.split(",") if g.strip()]
            elif re.match(r"leg\s*\d+", label):
                leg_m = re.search(r"\d+", label)
                if leg_m:
                    leg_num = int(leg_m.group())
                    dates = re.findall(r"\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}", value_text)
                    if len(dates) >= 2:
                        result["leg_dates"][leg_num] = {
                            "date_start": dates[0],
                            "date_end": dates[1],
                        }

        return result

    # ------------------------------------------------------------------
    # Stages table
    # ------------------------------------------------------------------

    def _parse_stages_table(self, soup: BeautifulSoup, leg_dates: dict) -> list[RallyLeg]:
        # Find the exact table that directly contains the stages header row
        fejlec2 = soup.find("tr", class_="fejlec2")
        if not fejlec2:
            return []
        stages_table = fejlec2.parent

        legs: list[RallyLeg] = []
        current_leg: RallyLeg | None = None
        pending_service: ServicePark | None = None

        for row in stages_table.find_all("tr"):
            row_classes = row.get("class") or []

            # Skip column header row
            if "fejlec2" in row_classes:
                continue

            # Leg header row — identified by <td class="lista_kiemelt">
            if row.find("td", class_="lista_kiemelt"):
                cells = row.find_all("td")
                if not cells:
                    continue
                leg_m = re.search(r"Leg\s*(\d+)", cells[0].get_text(strip=True), re.IGNORECASE)
                if not leg_m:
                    continue
                leg_num = int(leg_m.group(1))
                dates = leg_dates.get(leg_num, {})
                dist_km = None
                for c in cells:
                    d = self._parse_km(c.get_text(strip=True))
                    if d:
                        dist_km = d
                        break
                current_leg = RallyLeg(
                    leg_number=leg_num,
                    date_start=dates.get("date_start"),
                    date_end=dates.get("date_end"),
                    total_distance_km=dist_km,
                )
                legs.append(current_leg)
                continue

            # Service park row
            if "servicepark" in row_classes:
                service = self._parse_service(row.get_text(" ", strip=True))
                if current_leg and current_leg.stages:
                    # Service comes after the preceding stage
                    current_leg.stages[-1].service_after = service
                else:
                    # Service is before the first stage of the next leg
                    pending_service = service
                continue

            # Stage row — first cell is a plain integer
            if current_leg is None:
                continue
            cells = row.find_all("td")
            if not cells or not cells[0].get_text(strip=True).isdigit():
                continue

            stage = self._parse_stage_row(cells, pending_service)
            pending_service = None
            current_leg.stages.append(stage)

        return legs

    # ------------------------------------------------------------------
    # Row parsers
    # ------------------------------------------------------------------

    def _parse_stage_row(self, cells: list[Tag], service_before: ServicePark | None) -> RallyStage:
        def get(i: int) -> str:
            return cells[i].get_text(strip=True) if i < len(cells) else ""

        stage_number = int(cells[0].get_text(strip=True))

        # Stage name and country (country lives in the onmouseover tooltip string)
        name = ""
        country = None
        if len(cells) > 1:
            name_cell = cells[1]
            tip_div = name_cell.find("div", onmouseover=True)
            if tip_div:
                tip_str = tip_div.get("onmouseover", "")
                c_match = re.search(
                    r"<b>Country:</b></td><td[^>]*>[^<]*<img[^>]*/>\s*([^<']+)", tip_str
                )
                if c_match:
                    country = c_match.group(1).strip()
                name = tip_div.get_text(strip=True)
            else:
                name = name_cell.get_text(strip=True)

        # Surface cell: e.g. "Dry (Normal)" or "Dry (New)"
        surface_raw = get(3)
        surface = None
        condition = None
        surf_m = re.match(r"(\w+)\s*\(([^)]+)\)", surface_raw)
        if surf_m:
            surface = surf_m.group(1)
            condition = surf_m.group(2)
        elif surface_raw:
            surface = surface_raw

        return RallyStage(
            stage_number=stage_number,
            name=name,
            country=country,
            distance_km=self._parse_km(get(2)),
            surface=surface,
            condition=condition,
            weather=get(4) or None,
            tyre_choice=get(5) or None,
            set_tyre=get(6) or None,
            service_before=service_before,
        )

    def _parse_service(self, text: str) -> ServicePark:
        stype = "service_park" if "service park" in text.lower() else "road_side"
        duration = None
        mechanics = None
        dur_m = re.search(r"(\d+)\s+minute", text, re.IGNORECASE)
        if dur_m:
            duration = int(dur_m.group(1))
        mech_m = re.search(r"(\d+)\s+[Ss]killed", text)
        if mech_m:
            mechanics = int(mech_m.group(1))
        return ServicePark(type=stype, duration_minutes=duration, mechanics=mechanics)

    def _parse_km(self, text: str | None) -> float | None:
        if not text:
            return None
        m = re.search(r"([\d.,]+)\s*km", text, re.IGNORECASE)
        if not m:
            return None
        return float(m.group(1).replace(",", "."))
