from __future__ import annotations
from pydantic import BaseModel, HttpUrl


class Driver(BaseModel):
    name: str
    co_driver: str | None = None
    nationality: str | None = None
    car: str | None = None


class Stage(BaseModel):
    id: str
    name: str
    distance_km: float | None = None
    surface: str | None = None


class Event(BaseModel):
    id: str
    name: str
    date: str | None = None
    location: str | None = None
    stages: list[Stage] = []
    drivers: list[Driver] = []


class Championship(BaseModel):
    id: str
    name: str
    season: str | None = None
    events: list[Event] = []


class ScrapeRequest(BaseModel):
    url: HttpUrl


class ScrapeResponse(BaseModel):
    url: str
    site: str
    data_type: str  # "championship" | "event" | "stage" | "unknown"
    data: Championship | Event | Stage | list | dict


# --- Rally detail models ---

class ServicePark(BaseModel):
    type: str  # "service_park" or "road_side"
    duration_minutes: int | None = None
    mechanics: int | None = None


class RallyStage(BaseModel):
    stage_number: int
    name: str
    country: str | None = None
    distance_km: float | None = None
    surface: str | None = None
    condition: str | None = None
    weather: str | None = None
    tyre_choice: str | None = None
    set_tyre: str | None = None
    service_before: ServicePark | None = None
    service_after: ServicePark | None = None


class RallyLeg(BaseModel):
    leg_number: int
    date_start: str | None = None
    date_end: str | None = None
    total_distance_km: float | None = None
    stages: list[RallyStage] = []


class RallyDetail(BaseModel):
    rally_id: str
    name: str | None = None
    creator: str | None = None
    discord_url: str | None = None
    damage_level: str | None = None
    password_protected: bool = False
    num_legs: int | None = None
    super_rally: bool = False
    pacenotes: str | None = None
    started: int | None = None
    finished: int | None = None
    total_distance_km: float | None = None
    car_groups: list[str] = []
    legs: list[RallyLeg] = []
