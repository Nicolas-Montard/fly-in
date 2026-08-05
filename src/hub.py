from pydantic import BaseModel, Field
from typing import Literal

ZoneType = Literal["normal", "blocked", "restricted", "priority"]


class Hub(BaseModel):
    x: int
    y: int
    name: str
    zone_type: ZoneType = Field(default="normal")
    color: str = Field(default="black")
    max_drones: int = Field(default=1, ge=0)
    current_drone: int = 0
    explored: bool = False

    def get_name(self) -> str:
        return self.name

    def get_max_capacity(self) -> int:
        return self.max_drones
