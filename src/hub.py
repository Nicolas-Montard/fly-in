from pydantic import BaseModel, Field
from typing import Literal

ZoneType = Literal["normal", "blocked", "restricted", "priority"]

class Hub(BaseModel):
    x: int
    y: int
    name: str
    zone_type: ZoneType = Field(default="normal")
    color: str = Field(default="black")
    max_drones: int = Field(default=1, gt=0)